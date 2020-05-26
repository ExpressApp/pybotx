"""Definition for mixin that defines BotX API methods."""
from typing import Optional, Tuple
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.base import BotXMethod
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin
from botx.clients.types.users import UserFromSearch
from botx.models.sending import SendingCredentials


class UsersRequestsMixin:
    async def search_user(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        *,
        user_huid: Optional[UUID] = None,
        email: Optional[str] = None,
        ad: Optional[Tuple[str, str]] = None,
    ) -> UserFromSearch:
        method: BotXMethod
        if user_huid is not None:
            method = ByHUID(user_huid=user_huid)
        elif email is not None:
            method = ByEmail(email=email)
        elif ad is not None:
            method = ByLogin(ad_login=ad[0], ad_domain=ad[1])
        else:
            raise ValueError("one of user_huid, email or ad params should be filled")

        return await self.call_method(method, credentials=credentials)
