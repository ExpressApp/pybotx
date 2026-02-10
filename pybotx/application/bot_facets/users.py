from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.domain.models.users import UserFromCSV, UserFromSearch


class BotUsersMixin:
    async def search_user_by_emails(
        self,
        *,
        bot_id: UUID,
        emails: list[str],
    ) -> list[UserFromSearch]:
        """Search user by emails for search.

        :param bot_id: Bot which should perform the request.
        :param emails: User emails.

        :return: Search result with user information.
        """
        return await self._botx_api.search_user_by_emails(
            bot_id=bot_id,
            emails=emails,
        )

    async def search_user_by_email_post(
        self,
        *,
        bot_id: UUID,
        email: str,
    ) -> UserFromSearch:
        """Search user by email for search.

        Wraps the single email into a list payload and returns the first result.
        For multiple emails use `search_user_by_emails`.

        :param bot_id: Bot which should perform the request.
        :param email: User email.

        :return: User information.
        """
        return await self._botx_api.search_user_by_email_post(
            bot_id=bot_id,
            email=email,
        )

    async def search_user_by_email(
        self,
        *,
        bot_id: UUID,
        email: str,
    ) -> UserFromSearch:
        """Search user by email for search.

        DEPRECATED. Use `search_user_by_email_post`.

        :param bot_id: Bot which should perform the request.
        :param email: User email.

        :return: User information.
        """
        return await self._botx_api.search_user_by_email(
            bot_id=bot_id,
            email=email,
        )

    async def search_user_by_huid(
        self,
        *,
        bot_id: UUID,
        huid: UUID,
    ) -> UserFromSearch:
        """Search user by huid for search.

        :param bot_id: Bot which should perform the request.
        :param huid: User huid.

        :return: User information.
        """
        return await self._botx_api.search_user_by_huid(
            bot_id=bot_id,
            huid=huid,
        )

    async def search_user_by_ad(
        self,
        *,
        bot_id: UUID,
        ad_login: str,
        ad_domain: str,
    ) -> UserFromSearch:
        """Search user by AD login and AD domain for search.

        :param bot_id: Bot which should perform the request.
        :param ad_login: User AD login.
        :param ad_domain: User AD domain.

        :return: User information.
        """
        return await self._botx_api.search_user_by_ad(
            bot_id=bot_id,
            ad_login=ad_login,
            ad_domain=ad_domain,
        )

    async def search_user_by_other_id(
        self,
        *,
        bot_id: UUID,
        other_id: str,
    ) -> UserFromSearch:
        """Search user by other identificator for search.

        :param bot_id: Bot which should perform the request.
        :param other_id: User other identificator.

        :return: User information.
        """
        return await self._botx_api.search_user_by_other_id(
            bot_id=bot_id,
            other_id=other_id,
        )

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
        """Update user profile.

        :param bot_id: Bot which should perform the request.
        :param user_huid: User huid whose profile needs to be updated.
        :param avatar: New user avatar.
        :param name: New user name.
        :param public_name: New user public name.
        :param company: New user company.
        :param company_position: New user company position.
        :param description: New user description.
        :param department: New user department.
        :param office: New user office.
        :param manager: New user manager.
        """
        await self._botx_api.update_user_profile(
            bot_id=bot_id,
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

    @asynccontextmanager
    async def users_as_csv(
        self,
        *,
        bot_id: UUID,
        cts_user: bool = True,
        unregistered: bool = True,
        botx: bool = False,
    ) -> AsyncIterator[AsyncIterator[UserFromCSV]]:
        """Get a list of users on a CTS.

        :param bot_id: Bot which should perform the request.
        :param cts_user: Include CTS users in the list.
        :param unregistered: Include unregistered users in the list.
        :param botx: Include bots in the list.

        :yield: The list of users.
        """
        async with self._botx_api.users_as_csv(
            bot_id=bot_id,
            cts_user=cts_user,
            unregistered=unregistered,
            botx=botx,
        ) as users:
            yield users
