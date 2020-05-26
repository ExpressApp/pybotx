from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import user_not_found
from botx.clients.types.users import UserFromSearch


class ByEmail(AuthorizedBotXMethod[UserFromSearch]):
    __url__ = "/api/v3/botx/users/by_email"
    __method__ = "GET"
    __returning__ = UserFromSearch
    __errors_handlers__ = {StatusCode.NOT_FOUND: user_not_found.handle_error}

    email: str
