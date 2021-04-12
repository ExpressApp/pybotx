"""Method for searching user by his HUID."""
from http import HTTPStatus
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import user_not_found
from botx.models.users import UserFromSearch


class ByHUID(AuthorizedBotXMethod[UserFromSearch]):
    """Method for searching user by his HUID."""

    __url__ = "/api/v3/botx/users/by_huid"
    __method__ = "GET"
    __returning__ = UserFromSearch
    __errors_handlers__ = {HTTPStatus.NOT_FOUND: user_not_found.handle_error}

    #: HUID to search
    user_huid: UUID
