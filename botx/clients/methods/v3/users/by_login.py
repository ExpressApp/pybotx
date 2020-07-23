"""Method for searching user by his AD credentials."""
from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import user_not_found
from botx.models.users import UserFromSearch


class ByLogin(AuthorizedBotXMethod[UserFromSearch]):
    """Method for searching user by his AD credentials."""

    __url__ = "/api/v3/botx/users/by_login"
    __method__ = "GET"
    __returning__ = UserFromSearch
    __errors_handlers__ = {StatusCode.NOT_FOUND: user_not_found.handle_error}

    #: AD login to search
    ad_login: str

    #: AD domain to search
    ad_domain: str
