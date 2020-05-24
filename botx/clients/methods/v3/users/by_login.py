from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import user_not_found
from botx.clients.types.users import UserFromSearch


class ByLogin(AuthorizedBotXMethod[UserFromSearch]):
    __url__ = "/api/v3/botx/users/by_login"
    __method__ = "GET"
    __returning__ = UserFromSearch
    __errors_handlers__ = {StatusCode.NOT_FOUND: user_not_found.handle_error}

    ad_login: str
    ad_domain: str
