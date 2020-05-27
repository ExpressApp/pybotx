from abc import ABC, abstractmethod
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from httpx import URL, Response
from pydantic import BaseConfig, BaseModel, Extra
from pydantic.generics import GenericModel

from botx.clients.methods.request_wrapper import HTTPRequest, PrimitiveDataType
from botx.models.enums import Statuses

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

PRIMITIVES_FOR_QUERY = (str, int, float, bool, type(None))

ResponseT = TypeVar("ResponseT")
SyncErrorHandler = Callable[["BotXMethod", Response], NoReturn]
AsyncErrorHandler = Callable[["BotXMethod", Response], Awaitable[NoReturn]]
ErrorHandler = Union[SyncErrorHandler, AsyncErrorHandler]
ErrorHandlersInMethod = Union[Sequence[ErrorHandler], ErrorHandler]


class APIResponse(GenericModel, Generic[ResponseT]):
    status: Literal[Statuses.ok] = Statuses.ok
    result: ResponseT


class APIErrorResponse(GenericModel, Generic[ResponseT]):
    status: Literal[Statuses.error] = Statuses.error
    reason: str
    errors: List[str]
    error_data: ResponseT


class AbstractBotXMethod(ABC, Generic[ResponseT]):
    @property
    @abstractmethod
    def __url__(self) -> str:
        """Path for method in BotX API."""

    @property
    @abstractmethod
    def __method__(self) -> str:
        """HTTP method used for method."""

    @property
    @abstractmethod
    def __returning__(self) -> Type[Any]:
        """Shape returned from method that can be parsed by pydantic."""


CREDENTIALS_FIELDS = ("token", "host", "scheme")


class BaseBotXMethod(AbstractBotXMethod[ResponseT], ABC):
    host: str = ""
    token: str = ""
    scheme: str = "https"

    def configure(self, *, host: str, token: str, scheme: str = "https") -> None:
        self.token = token
        self.host = host
        self.scheme = scheme

    @property
    def base_url(self) -> str:
        return "{scheme}://{host}".format(scheme=self.scheme, host=self.host)

    @property
    def url(self) -> str:
        return str(URL(self.base_url).join(self.__url__))

    @property
    def http_method(self) -> str:
        return self.__method__

    @property
    def headers(self) -> Dict[str, str]:
        return {"Content-Type": "application/json"}

    @property
    def params(self) -> Mapping[str, PrimitiveDataType]:
        return {}

    @property
    def __errors_handlers__(self,) -> Mapping[int, ErrorHandlersInMethod]:
        return {}

    @property
    def __result_extractor__(
        self,
    ) -> Optional[Callable[["BotXMethod", Any], ResponseT]]:
        return None


class BotXMethod(BaseBotXMethod[ResponseT], BaseModel, ABC):
    class Config(BaseConfig):
        extra = Extra.allow
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        orm_mode = True

    def encode(self) -> Optional[str]:
        return self.json(by_alias=True, exclude=set(CREDENTIALS_FIELDS))

    def build_http_request(self) -> HTTPRequest:
        request_params = self.params
        request_data = self.encode()

        if self.__method__ == "GET":
            if request_data:
                request_data = None

            if not request_params:
                request_params = _convert_query_to_primitives(
                    self.dict(exclude=set(CREDENTIALS_FIELDS))
                )
                request_data = None

        return HTTPRequest(
            method=self.__method__,
            url=self.url,
            headers=self.headers,
            query_params=dict(request_params),
            request_data=request_data,
        )


class AuthorizedBotXMethod(BotXMethod[ResponseT], ABC):
    @property
    def headers(self) -> Dict[str, str]:
        headers = super().headers
        headers["Authorization"] = "Bearer {token}".format(token=self.token)
        return headers


def _convert_query_to_primitives(
    query_params: Mapping[str, Any]
) -> Dict[str, PrimitiveDataType]:
    converted_params = {}
    for param_key, param_value in query_params.items():
        if isinstance(param_value, PRIMITIVES_FOR_QUERY):
            converted_params[param_key] = param_value
        else:
            converted_params[param_key] = str(param_value)

    return converted_params
