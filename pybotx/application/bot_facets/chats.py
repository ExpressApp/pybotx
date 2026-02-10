from __future__ import annotations

from uuid import UUID

from pybotx.domain.errors import ChatNotFoundError
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.chats import ChatInfo, ChatLink, ChatListItem
from pybotx.domain.models.enums import ChatLinkTypes, ChatTypes


class BotChatsMixin:
    async def list_chats(
        self,
        *,
        bot_id: UUID,
    ) -> list[ChatListItem]:
        """Get all bot chats.

        :param bot_id: Bot which should perform the request.

        :returns: List of chats info.
        """
        return await self._botx_api.list_chats(bot_id=bot_id)

    async def chat_info(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> ChatInfo:
        """Get chat information.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.

        :return: Chat information.
        """
        return await self._botx_api.chat_info(bot_id=bot_id, chat_id=chat_id)

    async def personal_chat(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
    ) -> ChatInfo:
        """Get personal chat between bot and user.

        :param bot_id: Bot which should perform the request.
        :param user_huid: User identifier.

        :return: Chat information.
        """
        return await self._botx_api.personal_chat(bot_id=bot_id, user_huid=user_huid)

    async def ensure_personal_chat(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
        name: str | None = None,
    ) -> ChatInfo:
        """Get or create personal chat with user.

        Tries to fetch existing personal chat. If not found, creates it and
        returns chat info for the new chat.

        :param bot_id: Bot which should perform the request.
        :param user_huid: Target user HUID.
        :param name: Optional chat name for creation.

        :return: Chat information.
        """

        try:
            return await self.personal_chat(bot_id=bot_id, user_huid=user_huid)
        except ChatNotFoundError:
            chat_name = name or f"Personal chat {user_huid}"
            chat_id = await self.create_chat(
                bot_id=bot_id,
                name=chat_name,
                chat_type=ChatTypes.PERSONAL_CHAT,
                huids=[user_huid],
            )
            return await self.chat_info(bot_id=bot_id, chat_id=chat_id)

    async def add_users_to_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None:
        """Add user to chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param huids: List of eXpress account ids.
        """
        await self._botx_api.add_users_to_chat(
            bot_id=bot_id,
            chat_id=chat_id,
            huids=huids,
        )

    async def remove_users_from_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None:
        """Remove eXpress accounts from chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param huids: List of eXpress account ids.
        """
        await self._botx_api.remove_users_from_chat(
            bot_id=bot_id,
            chat_id=chat_id,
            huids=huids,
        )

    async def promote_to_chat_admins(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None:
        """Promote users in chat to admins.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param huids: List of eXpress account ids.
        """
        await self._botx_api.promote_to_chat_admins(
            bot_id=bot_id,
            chat_id=chat_id,
            huids=huids,
        )

    async def enable_stealth(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        disable_web_client: Missing[bool] = Undefined,
        ttl_after_read: Missing[int] = Undefined,
        total_ttl: Missing[int] = Undefined,
    ) -> None:
        """Enable stealth mode.

        After the expiration of the time all messages will be hidden.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param disable_web_client: (BotX default: False) Should messages
            be shown in web.
        :param ttl_after_read: (BotX default: OFF) Time of messages burning
            after read.
        :param total_ttl: (BotX default: OFF) Time of messages burning after
            send.
        """
        await self._botx_api.enable_stealth(
            bot_id=bot_id,
            chat_id=chat_id,
            disable_web_client=disable_web_client,
            ttl_after_read=ttl_after_read,
            total_ttl=total_ttl,
        )

    async def disable_stealth(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Disable stealth model. Hides all messages that were in stealth.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """
        await self._botx_api.disable_stealth(bot_id=bot_id, chat_id=chat_id)

    async def create_chat(
        self,
        *,
        bot_id: UUID,
        name: str,
        chat_type: ChatTypes,
        huids: list[UUID],
        description: str | None = None,
        shared_history: Missing[bool] = Undefined,
        avatar: str | None = None,
    ) -> UUID:
        """Create chat.

        :param bot_id: Bot which should perform the request.
        :param name: Chat visible name.
        :param chat_type: Chat type.
        :param huids: List of eXpress account ids.
        :param description: Chat description.
        :param shared_history: (BotX default: False) Open old chat history for
            new added users.
        :param avatar: Chat avatar in data URL format (RFC 2397).

        :return: Created chat uuid.
        """
        return await self._botx_api.create_chat(
            bot_id=bot_id,
            name=name,
            chat_type=chat_type,
            huids=huids,
            description=description,
            shared_history=shared_history,
            avatar=avatar,
        )

    async def create_chat_link(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        link_type: ChatLinkTypes,
        access_code: Missing[str | None] = Undefined,
        link_ttl: Missing[int | None] = Undefined,
    ) -> ChatLink:
        """Create chat invite link (BotX >= 3.58).

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param link_type: Link type.
        :param access_code: Link access code (or `None` to make it public).
        :param link_ttl: Link ttl in seconds (or `None` for infinite).

        :return: Created chat link.
        """
        return await self._botx_api.create_chat_link(
            bot_id=bot_id,
            chat_id=chat_id,
            link_type=link_type,
            access_code=access_code,
            link_ttl=link_ttl,
        )

    async def create_thread(self, bot_id: UUID, sync_id: UUID) -> UUID:
        """
        Create thread.

        :param bot_id: Bot which should perform the request.
        :param sync_id: Message for which thread should be created

        :return: Created thread uuid.
        """
        return await self._botx_api.create_thread(bot_id=bot_id, sync_id=sync_id)

    async def pin_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        sync_id: UUID,
    ) -> None:
        """Pin message in chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param sync_id: Target sync id.
        """
        await self._botx_api.pin_message(
            bot_id=bot_id,
            chat_id=chat_id,
            sync_id=sync_id,
        )

    async def unpin_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Unpin message in chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """
        await self._botx_api.unpin_message(bot_id=bot_id, chat_id=chat_id)
