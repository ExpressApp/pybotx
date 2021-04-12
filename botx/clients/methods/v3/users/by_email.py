"""Method for searching user by his email."""
from http import HTTPStatus

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import user_not_found
from botx.models.users import UserFromSearch


class ByEmail(AuthorizedBotXMethod[UserFromSearch]):
    """Method for searching user by his email."""

    __url__ = "/api/v3/botx/users/by_email"
    __method__ = "GET"
    __returning__ = UserFromSearch
    __errors_handlers__ = {HTTPStatus.NOT_FOUND: user_not_found.handle_error}

    #: email to search
    email: str
