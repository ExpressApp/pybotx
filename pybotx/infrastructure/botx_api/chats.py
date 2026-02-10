from __future__ import annotations

from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.chats import ChatInfo, ChatLink, ChatListItem
from pybotx.domain.models.enums import ChatLinkTypes, ChatTypes
from pybotx.infrastructure.client.chats_api.add_admin import (
    AddAdminMethod,
    BotXAPIAddAdminRequestPayload,
)
from pybotx.infrastructure.client.chats_api.add_user import (
    AddUserMethod,
    BotXAPIAddUserRequestPayload,
)
from pybotx.infrastructure.client.chats_api.chat_info import (
    BotXAPIChatInfoRequestPayload,
    ChatInfoMethod,
)
from pybotx.infrastructure.client.chats_api.create_chat import (
    BotXAPICreateChatRequestPayload,
    CreateChatMethod,
)
from pybotx.infrastructure.client.chats_api.create_chat_link import (
    BotXAPICreateChatLinkRequestPayload,
    CreateChatLinkMethod,
)
from pybotx.infrastructure.client.chats_api.create_thread import (
    BotXAPICreateThreadRequestPayload,
    CreateThreadMethod,
)
from pybotx.infrastructure.client.chats_api.disable_stealth import (
    BotXAPIDisableStealthRequestPayload,
    DisableStealthMethod,
)
from pybotx.infrastructure.client.chats_api.list_chats import ListChatsMethod
from pybotx.infrastructure.client.chats_api.pin_message import (
    BotXAPIPinMessageRequestPayload,
    PinMessageMethod,
)
from pybotx.infrastructure.client.chats_api.remove_user import (
    BotXAPIRemoveUserRequestPayload,
    RemoveUserMethod,
)
from pybotx.infrastructure.client.chats_api.set_stealth import (
    BotXAPISetStealthRequestPayload,
    SetStealthMethod,
)
from pybotx.infrastructure.client.chats_api.unpin_message import (
    BotXAPIUnpinMessageRequestPayload,
    UnpinMessageMethod,
)
from pybotx.infrastructure.client.chats_api.personal_chat import (
    BotXAPIPersonalChatRequestPayload,
    PersonalChatMethod,
)


class ChatsApiMixin:
    async def list_chats(self, *, bot_id: UUID) -> list[ChatListItem]:
        method = self._method_factory.build(ListChatsMethod, bot_id=bot_id)
        botx_api_chat_list = await method.execute()
        return botx_api_chat_list.to_domain()

    async def chat_info(self, *, bot_id: UUID, chat_id: UUID) -> ChatInfo:
        method = self._method_factory.build(ChatInfoMethod, bot_id=bot_id)
        payload = BotXAPIChatInfoRequestPayload.from_domain(chat_id=chat_id)
        botx_api_chat_info = await method.execute(payload)
        return botx_api_chat_info.to_domain()

    async def personal_chat(self, *, bot_id: UUID, user_huid: UUID) -> ChatInfo:
        method = self._method_factory.build(PersonalChatMethod, bot_id=bot_id)
        payload = BotXAPIPersonalChatRequestPayload.from_domain(user_huid=user_huid)
        botx_api_personal_chat = await method.execute(payload)
        return botx_api_personal_chat.to_domain()

    async def add_users_to_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None:
        method = self._method_factory.build(AddUserMethod, bot_id=bot_id)
        payload = BotXAPIAddUserRequestPayload.from_domain(chat_id=chat_id, huids=huids)
        await method.execute(payload)

    async def remove_users_from_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None:
        method = self._method_factory.build(RemoveUserMethod, bot_id=bot_id)
        payload = BotXAPIRemoveUserRequestPayload.from_domain(
            chat_id=chat_id,
            huids=huids,
        )
        await method.execute(payload)

    async def promote_to_chat_admins(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None:
        method = self._method_factory.build(AddAdminMethod, bot_id=bot_id)
        payload = BotXAPIAddAdminRequestPayload.from_domain(chat_id=chat_id, huids=huids)
        await method.execute(payload)

    async def enable_stealth(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        disable_web_client: Missing[bool] = Undefined,
        ttl_after_read: Missing[int] = Undefined,
        total_ttl: Missing[int] = Undefined,
    ) -> None:
        method = self._method_factory.build(SetStealthMethod, bot_id=bot_id)
        payload = BotXAPISetStealthRequestPayload.from_domain(
            chat_id=chat_id,
            disable_web_client=disable_web_client,
            ttl_after_read=ttl_after_read,
            total_ttl=total_ttl,
        )
        await method.execute(payload)

    async def disable_stealth(self, *, bot_id: UUID, chat_id: UUID) -> None:
        method = self._method_factory.build(DisableStealthMethod, bot_id=bot_id)
        payload = BotXAPIDisableStealthRequestPayload.from_domain(chat_id=chat_id)
        await method.execute(payload)

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
        method = self._method_factory.build(CreateChatMethod, bot_id=bot_id)
        payload = BotXAPICreateChatRequestPayload(
            name=name,
            chat_type=chat_type,
            members=huids,
            description=description,
            shared_history=shared_history,
            avatar=avatar,
        )
        botx_api_chat_creation_response = await method.execute(payload)
        return botx_api_chat_creation_response.to_domain()

    async def create_chat_link(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        link_type: ChatLinkTypes,
        access_code: Missing[str | None] = Undefined,
        link_ttl: Missing[int | None] = Undefined,
    ) -> ChatLink:
        method = self._method_factory.build(CreateChatLinkMethod, bot_id=bot_id)
        payload = BotXAPICreateChatLinkRequestPayload.from_domain(
            chat_id=chat_id,
            link_type=link_type,
            access_code=access_code,
            link_ttl=link_ttl,
        )
        botx_api_chat_link = await method.execute(payload)
        return botx_api_chat_link.to_domain()

    async def create_thread(self, bot_id: UUID, sync_id: UUID) -> UUID:
        method = self._method_factory.build(CreateThreadMethod, bot_id=bot_id)
        payload = BotXAPICreateThreadRequestPayload.from_domain(sync_id=sync_id)
        botx_api_thread_creation_response = await method.execute(payload)
        return botx_api_thread_creation_response.to_domain()

    async def pin_message(self, *, bot_id: UUID, chat_id: UUID, sync_id: UUID) -> None:
        method = self._method_factory.build(PinMessageMethod, bot_id=bot_id)
        payload = BotXAPIPinMessageRequestPayload.from_domain(
            chat_id=chat_id,
            sync_id=sync_id,
        )
        await method.execute(payload)

    async def unpin_message(self, *, bot_id: UUID, chat_id: UUID) -> None:
        method = self._method_factory.build(UnpinMessageMethod, bot_id=bot_id)
        payload = BotXAPIUnpinMessageRequestPayload.from_domain(chat_id=chat_id)
        await method.execute(payload)
