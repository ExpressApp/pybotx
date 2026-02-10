from __future__ import annotations

from typing import Any, TypeGuard, cast
from uuid import UUID

from pydantic import Field, ValidationError, field_validator, TypeAdapter

from pybotx.presentation.contracts.attachments import (
    BotAPIAttachment,
    convert_api_attachment_to_domain,
)
from pybotx.presentation.contracts.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotAPICommandPayload,
    BotAPIDeviceContext,
    BotAPIUserContext,
)
from pybotx.presentation.contracts.enums import (
    BotAPIEntityTypes,
    BotAPIMentionTypes,
    convert_chat_type_to_domain,
    convert_client_platform_to_domain,
)
from pybotx.presentation.contracts.message.forward import BotAPIForward
from pybotx.presentation.contracts.message.mentions import (
    BotAPIMention,
    BotAPIMentionData,
    BotAPINestedMentionData,
)
from pybotx.presentation.contracts.message.reply import BotAPIReply
from pybotx.domain.logger import logger
from pybotx.domain.models.attachments import (
    Contact,
    FileAttachmentBase,
    IncomingFileAttachment,
    Link,
    Location,
)
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.enums import ChatTypes
from pybotx.domain.models.message.forward import Forward
from pybotx.domain.models.message.incoming_message import (
    IncomingMessage,
    UserDevice,
    UserSender,
)
from pybotx.domain.models.message.mentions import Mention, MentionBuilder, MentionList
from pybotx.domain.models.message.reply import Reply
from pybotx.domain.models.stickers import Sticker


BotAPIEntity = BotAPIMention | BotAPIForward | BotAPIReply
Entity = Mention | Forward | Reply


def _convert_bot_api_mention_to_domain(api_mention_data: BotAPIMentionData) -> Mention:
    mention_data = cast(BotAPINestedMentionData, api_mention_data.mention_data)

    match api_mention_data.mention_type:
        case BotAPIMentionTypes.USER:
            return MentionBuilder.user(
                entity_id=mention_data.entity_id,
                name=mention_data.name,
            )
        case BotAPIMentionTypes.CHAT:
            return MentionBuilder.chat(
                entity_id=mention_data.entity_id,
                name=mention_data.name,
            )
        case BotAPIMentionTypes.CONTACT:
            return MentionBuilder.contact(
                entity_id=mention_data.entity_id,
                name=mention_data.name,
            )
        case BotAPIMentionTypes.CHANNEL:
            return MentionBuilder.channel(
                entity_id=mention_data.entity_id,
                name=mention_data.name,
            )
        case BotAPIMentionTypes.ALL:
            return MentionBuilder.all()
        case _:
            raise NotImplementedError(
                f"Unsupported mention type: {api_mention_data.mention_type}",
            )


def _is_bot_api_mention(entity: BotAPIEntity) -> TypeGuard[BotAPIMention]:
    return entity.type == BotAPIEntityTypes.MENTION


def _is_bot_api_forward(entity: BotAPIEntity) -> TypeGuard[BotAPIForward]:
    return entity.type == BotAPIEntityTypes.FORWARD


def _is_bot_api_reply(entity: BotAPIEntity) -> TypeGuard[BotAPIReply]:
    return entity.type == BotAPIEntityTypes.REPLY


def convert_bot_api_entity_to_domain(api_entity: BotAPIEntity) -> Entity:
    match api_entity.type:
        case BotAPIEntityTypes.MENTION:
            if not _is_bot_api_mention(api_entity):
                raise NotImplementedError(
                    f"Unsupported entity type: {api_entity.type}",
                )
            return _convert_bot_api_mention_to_domain(api_entity.data)
        case BotAPIEntityTypes.FORWARD:
            if not _is_bot_api_forward(api_entity):
                raise NotImplementedError(
                    f"Unsupported entity type: {api_entity.type}",
                )
            return Forward(
                chat_id=api_entity.data.group_chat_id,
                author_id=api_entity.data.sender_huid,
                sync_id=api_entity.data.source_sync_id,
                chat_name=api_entity.data.source_chat_name,
                forward_type=convert_chat_type_to_domain(api_entity.data.forward_type),
                inserted_at=api_entity.data.source_inserted_at,
            )
        case BotAPIEntityTypes.REPLY:
            if not _is_bot_api_reply(api_entity):
                raise NotImplementedError(
                    f"Unsupported entity type: {api_entity.type}",
                )
            mentions = MentionList()
            for api_mention_data in api_entity.data.mentions:
                mentions.append(_convert_bot_api_mention_to_domain(api_mention_data))

            return Reply(
                author_id=api_entity.data.sender,
                sync_id=api_entity.data.source_sync_id,
                body=api_entity.data.body,
                mentions=mentions,
            )
        case _:
            raise NotImplementedError(f"Unsupported entity type: {api_entity.type}")


class BotAPIIncomingMessageContext(
    BotAPIUserContext,
    BotAPIChatContext,
    BotAPIDeviceContext,
):
    """Class for merging contexts."""


class BotAPIIncomingMessage(BotAPIBaseCommand):
    payload: BotAPICommandPayload = Field(..., alias="command")
    sender: BotAPIIncomingMessageContext = Field(..., alias="from")

    source_sync_id: UUID | None
    attachments: list[BotAPIAttachment | dict[str, Any]]
    entities: list[BotAPIEntity | dict[str, Any]]

    @staticmethod
    def validate_items(value: list[dict[str, Any] | Any], info: Any) -> list[Any]:
        item_model = (
            BotAPIAttachment if info.field_name == "attachments" else BotAPIEntity
        )
        parsed: list[Any] = []
        for item in value:
            if isinstance(item, dict):
                try:
                    parsed.append(TypeAdapter(item_model).validate_python(item))
                except ValidationError:
                    parsed.append(item)
        return parsed

    @field_validator("attachments", "entities", mode="before")
    @classmethod
    def _validate_items_field(
        cls, value: list[dict[str, Any] | Any], info: Any
    ) -> list[Any]:
        # Pydantic-валидатор: просто делегируем статическому методу
        return cls.validate_items(value, info)

    def to_domain(self, raw_command: dict[str, Any]) -> IncomingMessage:
        if self.sender.device_meta:
            pushes = self.sender.device_meta.pushes
            timezone = self.sender.device_meta.timezone
            permissions = self.sender.device_meta.permissions
        else:
            pushes, timezone, permissions = None, None, None

        device = UserDevice(
            manufacturer=self.sender.manufacturer,
            device_name=self.sender.device,
            os=self.sender.device_software,
            pushes=pushes,
            timezone=timezone,
            permissions=permissions,
            platform=(
                convert_client_platform_to_domain(self.sender.platform)
                if self.sender.platform
                else None
            ),
            platform_package_id=self.sender.platform_package_id,
            app_version=self.sender.app_version,
            locale=self.sender.locale,
        )

        sender = UserSender(
            huid=self.sender.user_huid,
            udid=self.sender.user_udid,
            ad_login=self.sender.ad_login,
            ad_domain=self.sender.ad_domain,
            username=self.sender.username,
            is_chat_admin=self.sender.is_admin,
            is_chat_creator=self.sender.is_creator,
            device=device,
        )

        chat = Chat(
            id=self.sender.group_chat_id,
            type=convert_chat_type_to_domain(self.sender.chat_type),
        )

        file: IncomingFileAttachment | None = None
        location: Location | None = None
        contact: Contact | None = None
        link: Link | None = None
        sticker: Sticker | None = None

        if self.attachments:
            # Always one attachment per-message
            if isinstance(self.attachments[0], dict):
                logger.warning("Received unknown attachment type")
            else:
                attachment_domain = convert_api_attachment_to_domain(
                    self.attachments[0],
                    self.payload.body,
                )
                if isinstance(attachment_domain, FileAttachmentBase):
                    file = attachment_domain
                elif isinstance(attachment_domain, Location):
                    location = attachment_domain
                elif isinstance(attachment_domain, Contact):
                    contact = attachment_domain
                elif isinstance(attachment_domain, Link):
                    link = attachment_domain
                elif isinstance(attachment_domain, Sticker):
                    sticker = attachment_domain
                else:
                    raise NotImplementedError

        mentions: MentionList = MentionList()
        forward: Forward | None = None
        reply: Reply | None = None
        for entity in self.entities:
            if isinstance(entity, dict):
                logger.warning("Received unknown entity type")
            else:
                entity_domain = convert_bot_api_entity_to_domain(entity)
                if isinstance(
                    entity_domain,
                    Mention.__args__,
                ):
                    mentions.append(entity_domain)
                elif isinstance(entity_domain, Forward):
                    # Max one forward per message
                    forward = entity_domain
                elif isinstance(entity_domain, Reply):
                    # Max one reply per message
                    reply = entity_domain
                else:
                    raise NotImplementedError

        bot = BotAccount(
            id=self.bot_id,
            host=self.sender.host,
        )

        return IncomingMessage(
            bot=bot,
            sync_id=self.sync_id,
            source_sync_id=self.source_sync_id,
            body=self.payload.body,
            data=self.payload.data,
            metadata=self.payload.metadata,
            sender=sender,
            chat=chat,
            raw_command=raw_command,
            file=file,
            location=location,
            contact=contact,
            link=link,
            sticker=sticker,
            mentions=mentions,
            forward=forward,
            reply=reply,
        )
