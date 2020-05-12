import collections
import contextlib
from abc import ABC, abstractmethod
from typing import (
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

from botx.clients.clients import AsyncClient
from botx.exceptions import BotXAPIError
from botx.models.enums import Statuses

ResponseT = TypeVar("ResponseT")
ErrorHandler = Callable[["BotXMethod", Response], Awaitable[NoReturn]]
ErrorHandlersInMethod = Union[Sequence[ErrorHandler], ErrorHandler]


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
        ...

    @property
    @abstractmethod
    def __method__(self) -> str:
        ...

    @property
    def api_method(self) -> str:
        return self.__method__

    @property
    @abstractmethod
    def __returning__(self) -> Type[ResponseT]:
        ...


class BaseBotXMethod(AbstractBotXMethod[ResponseT], ABC):
    def fill_credentials(self, host: str, token: str, *, scheme: str = "https") -> None:
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
    def __error_handlers__(self,) -> Mapping[int, ErrorHandlersInMethod]:
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
        return self.json(by_alias=True)

    async def call(self, client: AsyncClient) -> ResponseT:
        response = await self.execute(client)

        if StatusCode.is_error(response.status_code):
            error_handlers = self.__error_handlers__.get(response.status_code)
            if error_handlers is not None:
                await self._handle_error(error_handlers, response)
            else:
                raise BotXAPIError(
                    url=self.url,
                    method=self.__method__,
                    status=response.status_code,
                    response_content=response.json(),
                )

        return self._extract_result(response)

    async def execute(self, client: AsyncClient) -> Response:
        return await client.http_client.request(
            self.__method__,
            self.url,
            headers=self.headers,
            params=self.params,
            data=self.encode(),
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
                await error_handler(self, response)


class AuthorizedBotXMethod(BotXMethod[ResponseT], ABC):
    @property
    def headers(self) -> Dict[str, str]:
        headers = super().headers
        headers["Authorization"] = "Bearer {token}".format(token=self.token)
        return headers
