"""Mixin for shortcut for users resource requests."""

from typing import Optional, Tuple
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.users import UserFromSearch


class UsersRequestsMixin:
    """Mixin for shortcut for users resource requests."""

    async def search_user(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        *,
        user_huid: Optional[UUID] = None,
        email: Optional[str] = None,
        ad: Optional[Tuple[str, str]] = None,
    ) -> UserFromSearch:
        """Search user by one of provided params for search.

        Arguments:
            credentials: credentials for making request.
            user_huid: HUID of user.
            email: email of user.
            ad: AD login and domain of user.

        Returns:
            Information about user.

        Raises:
            ValueError: raised if none  of provided params were filled.
        """
        if user_huid is not None:
            return await self.call_method(
                ByHUID(user_huid=user_huid),
                credentials=credentials,
            )
        elif email is not None:
            return await self.call_method(ByEmail(email=email), credentials=credentials)
        elif ad is not None:
            return await self.call_method(
                ByLogin(ad_login=ad[0], ad_domain=ad[1]),
                credentials=credentials,
            )

        raise ValueError("one of user_huid, email or ad query_params should be filled")
