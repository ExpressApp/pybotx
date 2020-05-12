from typing import List
from uuid import UUID

from httpx import StatusCode
from pydantic import BaseModel

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import user_not_found


class UserFromSearch(BaseModel):
    user_huid: UUID
    ad_login: str
    ad_domain: str
    name: str
    company: str
    company_position: str
    department: str
    emails: List[str]


class ByLogin(AuthorizedBotXMethod[UserFromSearch]):
    __url__ = "/api/v3/botx/users/by_login"
    __method__ = "GET"
    __returning__ = str
    __error_handlers__ = {StatusCode.NOT_FOUND: user_not_found.handle_error}

    ad_login: str
    ad_domain: str
