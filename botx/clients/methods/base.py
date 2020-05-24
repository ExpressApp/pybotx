import collections
import contextlib
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

from httpx import URL, Response, StatusCode
from pydantic import BaseConfig, BaseModel, Extra, Field, ValidationError
from pydantic.generics import GenericModel

from botx import concurrency
from botx.clients.client import AsyncClient
from botx.exceptions import BotXAPIError
from botx.models.enums import Statuses

PRIMITIVES_FOR_QUERY = (str, int, float, bool, type(None))

ResponseT = TypeVar("ResponseT")
SyncErrorHandler = Callable[["BotXMethod", Response], NoReturn]
AsyncErrorHandler = Callable[["BotXMethod", Response], Awaitable[NoReturn]]
ErrorHandler = Union[SyncErrorHandler, AsyncClient]
ErrorHandlersInMethod = Union[Sequence[ErrorHandler], ErrorHandler]
PrimitiveDataType = Union[None, str, int, float, bool]


class APIResponse(GenericModel, Generic[ResponseT]):
    status: Statuses = Field(Statuses.ok, const=True)
    result: ResponseT


class APIErrorResponse(GenericModel, Generic[ResponseT]):
    status: Statuses = Field(Statuses.error, const=True)
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
    def __returning__(self) -> Type[ResponseT]:
        """Shape returned from method that can be parsed by pydantic."""


CREDENTIALS_FIELDS = ("token", "host", "scheme")


class BaseBotXMethod(AbstractBotXMethod[ResponseT], ABC):
    host: str = ''
    token: str = ''
    scheme: str = 'https'

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
    def headers(self) -> Dict[str, str]:
        return {"Content-Type": "application/json"}

    @property
    def params(self) -> Mapping[str, str]:
        return {}

    @property
    def __errors_handlers__(self, ) -> Mapping[int, ErrorHandlersInMethod]:
        return {}

    @property
    def __result_extractor__(self) -> Optional[Callable[[APIResponse], ResponseT]]:
        return None


class BotXMethod(BaseBotXMethod[ResponseT], BaseModel, ABC):
    class Config(BaseConfig):
        extra = Extra.allow
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        orm_mode = True

    def encode(self) -> Optional[str]:
        return self.json(by_alias=True, exclude=set(CREDENTIALS_FIELDS))

    async def call(self, client: AsyncClient, host: Optional[str] = None) -> ResponseT:
        if host is not None:
            self.host = host

        response = await self.execute(client)

        if StatusCode.is_error(response.status_code):
            error_handlers = self.__errors_handlers__.get(response.status_code)
            if error_handlers is not None:
                await self._handle_error(error_handlers, response)

            raise BotXAPIError(
                url=self.url,
                method=self.__method__,
                status=response.status_code,
                response_content=response.json(),
            )

        return self._extract_result(response)

    async def execute(self, client: AsyncClient) -> Response:
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

        return await client.http_client.request(
            self.__method__,
            self.url,
            headers=self.headers,
            params=request_params,
            data=request_data,
        )

    def _extract_result(self, response: Response) -> ResponseT:
        api_response = APIResponse[self.__returning__].parse_obj(  # type: ignore
            response.json()
        )
        result = api_response.result
        if self.__result_extractor__ is not None:
            return self.__result_extractor__(result)

        return result

    async def _handle_error(
            self, error_handlers: ErrorHandlersInMethod, response: Response
    ) -> None:
        if not isinstance(error_handlers, collections.Sequence):
            error_handlers = [error_handlers]

        for error_handler in error_handlers:
            with contextlib.suppress(ValidationError):
                await concurrency.callable_to_coroutine(error_handler, self, response)


class AuthorizedBotXMethod(BotXMethod[ResponseT], ABC):
    @property
    def headers(self) -> Dict[str, str]:
        headers = super().headers
        headers["Authorization"] = "Bearer {token}".format(token=self.token)
        return headers


def _convert_query_to_primitives(
        query_params: Mapping[str, Any]
) -> Mapping[str, PrimitiveDataType]:
    converted_params = {}
    for param_key, param_value in query_params.items():
        if not isinstance(param_value, PRIMITIVES_FOR_QUERY):
            converted_params[param_key] = str(param_value)
        else:
            converted_params[param_key] = param_value

    return converted_params
