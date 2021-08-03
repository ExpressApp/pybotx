"""Definition for base class that is responsible for request to BotX API."""
from __future__ import annotations

import json
import typing
from abc import ABC, abstractmethod
from urllib.parse import urljoin

from httpx import Response
from pydantic import BaseConfig, BaseModel, Extra
from pydantic.generics import GenericModel

from botx.clients.types.http import HTTPRequest, HTTPResponse, PrimitiveDataType
from botx.models.enums import Statuses

try:
    from typing import Literal  # noqa: WPS433, WPS458
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS433, WPS440, F401

ResponseT = typing.TypeVar("ResponseT")
SyncErrorHandler = typing.Callable[["BotXMethod", HTTPResponse], typing.NoReturn]
AsyncErrorHandler = typing.Callable[
    ["BotXMethod", Response],
    typing.Awaitable[typing.NoReturn],
]
ErrorHandler = typing.Union[SyncErrorHandler, AsyncErrorHandler]
ErrorHandlersInMethod = typing.Union[typing.Sequence[ErrorHandler], ErrorHandler]


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
    def __errors_handlers__(self) -> typing.Mapping[int, ErrorHandlersInMethod]:
        """Error handlers for responses from BotX API by status code and handler."""
        return typing.cast(typing.Mapping[int, ErrorHandlersInMethod], {})

    @property
    def __result_extractor__(
        self,
    ) -> typing.Optional[typing.Callable[[BotXMethod, typing.Any], ResponseT]]:
        """Extractor for response shape from BotX API."""
        return None  # noqa: WPS324


CREDENTIALS_FIELDS = frozenset(("token", "host", "scheme"))


class BaseBotXMethod(AbstractBotXMethod[ResponseT], ABC):
    """Base logic that is responsible for configuration and shortcuts for fields."""

    #: host where request should be sent.
    host: str = ""

    #: token for request.
    token: str = ""

    #: HTTP scheme for request.
    scheme: str = "https"

    @property
    def url(self) -> str:
        """Full URL for request."""
        base_url = "{scheme}://{host}".format(scheme=self.scheme, host=self.host)
        return urljoin(base_url, self.__url__)

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
    def returning(self) -> typing.Type[typing.Any]:
        """Shape returned from method that can be parsed by pydantic."""
        return self.__returning__

    @property
    def error_handlers(self) -> typing.Mapping[int, ErrorHandlersInMethod]:
        """Error handlers for responses from BotX API by status code and handler."""
        return self.__errors_handlers__

    @property
    def result_extractor(
        self,
    ) -> typing.Optional[typing.Callable[[BotXMethod, typing.Any], ResponseT]]:
        """Extractor for response shape from BotX API."""
        return self.__result_extractor__


class BotXMethod(BaseBotXMethod[ResponseT], BaseModel, ABC):
    """Method for BotX API that should be extended by actual implementation."""

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

    def build_serialized_dict(
        self,
    ) -> typing.Optional[typing.Dict[str, PrimitiveDataType]]:
        """Build serialized dict (with only primitive types) for request.

        Returns:
            Serialized dict.
        """
        # TODO: Waiting for <https://github.com/samuelcolvin/pydantic/issues/1409/>
        serialized_dict = json.loads(
            self.json(
                by_alias=True,
                exclude=CREDENTIALS_FIELDS,
                exclude_none=True,
            ),
        )

        # Because exclude_none removes empty file key on message update
        if hasattr(self, "file") and self.file is None:  # type: ignore # noqa: WPS421
            serialized_dict["file"] = None

        return serialized_dict

    def build_http_request(self) -> HTTPRequest:
        """Build HTTP request that can be used by clients for making real requests.

        Returns:
            Built HTTP request.
        """
        request_params = self.query_params
        request_data = self.build_serialized_dict()

        if self.__method__ == "GET" and request_data:
            request_params = request_data
            request_data = None

        return HTTPRequest(
            method=self.__method__,
            url=self.url,
            headers=self.headers,
            query_params=dict(request_params),
            json_body=request_data,
        )


class AuthorizedBotXMethod(BotXMethod[ResponseT], ABC):
    """Method for BotX API that adds authorization token."""

    @property
    def headers(self) -> typing.Dict[str, str]:
        """Headers that should be used in request."""
        headers = super().headers
        headers["Authorization"] = "Bearer {token}".format(token=self.token)
        return headers
