from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.users import UserFromCSV, UserFromSearch
from pybotx.infrastructure.client.users_api.search_user_by_email import (
    BotXAPISearchUserByEmailRequestPayload,
    SearchUserByEmailMethod,
    SearchUserByEmailPostMethod,
)
from pybotx.infrastructure.client.users_api.search_user_by_emails import (
    BotXAPISearchUserByEmailsRequestPayload,
    SearchUserByEmailsMethod,
)
from pybotx.infrastructure.client.users_api.search_user_by_huid import (
    BotXAPISearchUserByHUIDRequestPayload,
    SearchUserByHUIDMethod,
)
from pybotx.infrastructure.client.users_api.search_user_by_login import (
    BotXAPISearchUserByLoginRequestPayload,
    SearchUserByLoginMethod,
)
from pybotx.infrastructure.client.users_api.search_user_by_other_id import (
    BotXAPISearchUserByOtherIdRequestPayload,
    SearchUserByOtherIdMethod,
)
from pybotx.infrastructure.client.users_api.update_user_profile import (
    BotXAPIUpdateUserProfileRequestPayload,
    UpdateUsersProfileMethod,
)
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment


class UsersApiMixin:
    async def search_user_by_emails(
        self,
        *,
        bot_id: UUID,
        emails: list[str],
    ) -> list[UserFromSearch]:
        method = self._method_factory.build(SearchUserByEmailsMethod, bot_id=bot_id)
        payload = BotXAPISearchUserByEmailsRequestPayload.from_domain(emails=emails)
        botx_api_users = await method.execute(payload)
        return botx_api_users.to_domain()

    async def search_user_by_email_post(self, *, bot_id: UUID, email: str) -> UserFromSearch:
        method = self._method_factory.build(SearchUserByEmailPostMethod, bot_id=bot_id)
        payload = BotXAPISearchUserByEmailRequestPayload.from_domain(email=email)
        botx_api_user = await method.execute(payload)
        return botx_api_user.to_domain()

    async def search_user_by_email(self, *, bot_id: UUID, email: str) -> UserFromSearch:
        method = self._method_factory.build(SearchUserByEmailMethod, bot_id=bot_id)
        payload = BotXAPISearchUserByEmailRequestPayload.from_domain(email=email)
        botx_api_user = await method.execute(payload)
        return botx_api_user.to_domain()

    async def search_user_by_huid(self, *, bot_id: UUID, huid: UUID) -> UserFromSearch:
        method = self._method_factory.build(SearchUserByHUIDMethod, bot_id=bot_id)
        payload = BotXAPISearchUserByHUIDRequestPayload.from_domain(huid=huid)
        botx_api_user = await method.execute(payload)
        return botx_api_user.to_domain()

    async def search_user_by_ad(
        self,
        *,
        bot_id: UUID,
        ad_login: str,
        ad_domain: str,
    ) -> UserFromSearch:
        method = self._method_factory.build(SearchUserByLoginMethod, bot_id=bot_id)
        payload = BotXAPISearchUserByLoginRequestPayload.from_domain(
            ad_login=ad_login,
            ad_domain=ad_domain,
        )
        botx_api_user = await method.execute(payload)
        return botx_api_user.to_domain()

    async def search_user_by_other_id(
        self,
        *,
        bot_id: UUID,
        other_id: str,
    ) -> UserFromSearch:
        method = self._method_factory.build(SearchUserByOtherIdMethod, bot_id=bot_id)
        payload = BotXAPISearchUserByOtherIdRequestPayload.from_domain(other_id=other_id)
        botx_api_user = await method.execute(payload)
        return botx_api_user.to_domain()

    async def update_user_profile(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
        avatar: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        name: Missing[str] = Undefined,
        public_name: Missing[str] = Undefined,
        company: Missing[str] = Undefined,
        company_position: Missing[str] = Undefined,
        description: Missing[str] = Undefined,
        department: Missing[str] = Undefined,
        office: Missing[str] = Undefined,
        manager: Missing[str] = Undefined,
    ) -> None:
        method = self._method_factory.build(UpdateUsersProfileMethod, bot_id=bot_id)
        payload = BotXAPIUpdateUserProfileRequestPayload.from_domain(
            user_huid=user_huid,
            avatar=avatar,
            name=name,
            public_name=public_name,
            company=company,
            company_position=company_position,
            description=description,
            department=department,
            office=office,
            manager=manager,
        )
        await method.execute(payload)

    @asynccontextmanager
    async def users_as_csv(
        self,
        *,
        bot_id: UUID,
        cts_user: bool = True,
        unregistered: bool = True,
        botx: bool = False,
    ) -> AsyncIterator[AsyncIterator[UserFromCSV]]:
        async with self._users_csv_service.stream_users(
            bot_id=bot_id,
            cts_user=cts_user,
            unregistered=unregistered,
            botx=botx,
        ) as iterator:
            yield iterator
