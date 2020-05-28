"""Definition for base class that is responsible for request to BotX API."""
from __future__ import annotations

import typing
from abc import ABC, abstractmethod

from httpx import URL, Response
from pydantic import BaseConfig, BaseModel, Extra
from pydantic.generics import GenericModel

from botx.clients.methods.request_wrapper import HTTPRequest, PrimitiveDataType
from botx.models.enums import Statuses

try:
    from typing import Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import Literal  # noqa: WPS433, WPS440

PRIMITIVES_FOR_QUERY = (str, int, float, bool, type(None))

ResponseT = typing.TypeVar("ResponseT")
SyncErrorHandler = typing.Callable[["BotXMethod", Response], typing.NoReturn]
AsyncErrorHandler = typing.Callable[
    ["BotXMethod", Response], typing.Awaitable[typing.NoReturn],
]
ErrorHandler = typing.Union[SyncErrorHandler, AsyncErrorHandler]
ErrorHandlersInMethod = typing.Union[typing.Sequence[ErrorHandler], ErrorHandler]


def _convert_query_to_primitives(
        query_params: typing.Mapping[str, typing.Any],
) -> typing.Dict[str, PrimitiveDataType]:
    converted_params = {}
    for param_key, param_value in query_params.items():
        if isinstance(param_value, PRIMITIVES_FOR_QUERY):
            converted_params[param_key] = param_value
        else:
            converted_params[param_key] = str(param_value)

    return converted_params


class APIResponse(GenericModel, typing.Generic[ResponseT]):
    """Model for successful response from BotX API."""

    #: status of requested operation response.
    status: Literal[Statuses.ok] = Statuses.ok

    #: generic response shape.
    result: ResponseT


class APIErrorResponse(GenericModel, typing.Generic[ResponseT]):
    """Model for error response from BotX API."""

    #: status of requested operation response.
    status: Literal[Statuses.error] = Statuses.error

    #: reason why operation failed
    reason: str

    #: errors from API.
    errors: typing.List[str]

    #: additional payload with more data about error.
    error_data: ResponseT


class AbstractBotXMethod(ABC, typing.Generic[ResponseT]):
    """Abstract base class for BotX request."""

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
    def __returning__(self) -> typing.Type[typing.Any]:
        """Shape returned from method that can be parsed by pydantic."""

    @property
    def __errors_handlers__(self) -> typing.Dict[int, ErrorHandlersInMethod]:
        """Special handlers for errors from BotX API by status code and handler."""
        return {}

    @property
    def __result_extractor__(self) -> typing.Optional[
        typing.Callable[[BotXMethod, typing.Any], ResponseT]
    ]:
        """Extractor for response shape from BotX API."""
        return None


CREDENTIALS_FIELDS = ("token", "host", "scheme")


class BaseBotXMethod(AbstractBotXMethod[ResponseT], ABC):
    """Base logic that is responsible for configuration and shortcuts for fields."""

    #: host where request should be sent.
    host: str = ""

    #: token for request.
    token: str = ""

    #: HTTP scheme for request.
    scheme: str = "https"

    @property
    def base_url(self) -> str:
        """Base URL(scheme + hsot) for httpx clients."""
        return "{scheme}://{host}".format(scheme=self.scheme, host=self.host)

    @property
    def url(self) -> str:
        """Full URL for request."""
        return str(URL(self.base_url).join(self.__url__))

    @property
    def http_method(self) -> str:
        """HTTP method for request."""
        return self.__method__

    @property
    def headers(self) -> typing.Dict[str, str]:
        """Headers that should be used in request."""
        return {"Content-Type": "application/json"}

    @property
    def query_params(self) -> typing.Dict[str, PrimitiveDataType]:
        """Query string query_params for request."""
        return {}

    @property
    def error_handlers(self) -> typing.Dict[int, ErrorHandlersInMethod]:
        return self.__errors_handlers__

    @property
    def result_extractor(
            self,
    ) -> typing.Optional[typing.Callable[[BotXMethod, typing.Any], ResponseT]]:
        return self.__result_extractor__

    @property
    def returning(self) -> typing.Type[typing.Any]:
        return self.__returning__


class BotXMethod(BaseBotXMethod[ResponseT], BaseModel, ABC):
    class Config(BaseConfig):
        extra = Extra.allow
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        orm_mode = True

    def configure(self, *, host: str, token: str, scheme: str = "https") -> None:
        """Configure request with credentials and transport related stuff.

        Arguments:
            host: host where request should be sent.
            token: token for request.
            scheme: HTTP scheme for request.
        """
        self.token = token
        self.host = host
        self.scheme = scheme

    def encode(self) -> typing.Optional[str]:
        return self.json(by_alias=True, exclude=set(CREDENTIALS_FIELDS))

    def build_http_request(self) -> HTTPRequest:
        request_params = self.query_params
        request_data = self.encode()

        if self.__method__ == "GET":
            if request_data:
                request_data = None

            if not request_params:
                request_params = _convert_query_to_primitives(
                    self.dict(exclude=set(CREDENTIALS_FIELDS)),
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
    def headers(self) -> typing.Dict[str, str]:
        headers = super().headers
        headers["Authorization"] = "Bearer {token}".format(token=self.token)
        return headers
