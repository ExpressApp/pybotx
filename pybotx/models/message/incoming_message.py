from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from uuid import UUID

from pydantic import Field

from pybotx.logger import logger
from pybotx.models.attachments import (
    BotAPIAttachment,
    Contact,
    FileAttachmentBase,
    IncomingFileAttachment,
    Link,
    Location,
    convert_api_attachment_to_domain,
)
from pybotx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotAPICommandPayload,
    BotAPIDeviceContext,
    BotAPIUserContext,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.chats import Chat
from pybotx.models.enums import (
    BotAPIEntityTypes,
    BotAPIMentionTypes,
    ClientPlatforms,
    convert_chat_type_to_domain,
    convert_client_platform_to_domain,
)
from pybotx.models.message.forward import BotAPIForward, Forward
from pybotx.models.message.mentions import (
    BotAPIMention,
    BotAPIMentionData,
    BotAPINestedMentionData,
    Mention,
    MentionBuilder,
    MentionList,
)
from pybotx.models.message.reply import BotAPIReply, Reply
from pybotx.models.stickers import Sticker


@dataclass
class UserDevice:
    manufacturer: Optional[str]
    device_name: Optional[str]
    os: Optional[str]
    pushes: Optional[bool]
    timezone: Optional[str]
    permissions: Optional[Dict[str, Any]]
    platform: Optional[ClientPlatforms]
    platform_package_id: Optional[str]
    app_version: Optional[str]
    locale: Optional[str]


@dataclass
class UserSender:
    huid: UUID
    udid: Optional[UUID]
    ad_login: Optional[str]
    ad_domain: Optional[str]
    username: Optional[str]
    is_chat_admin: Optional[bool]
    is_chat_creator: Optional[bool]
    device: UserDevice

    @property
    def upn(self) -> Optional[str]:
        # https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats
        if not (self.ad_login and self.ad_domain):
            return None

        return f"{self.ad_login}@{self.ad_domain}"


@dataclass
class IncomingMessage(BotCommandBase):
    sync_id: UUID
    source_sync_id: Optional[UUID]
    body: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    sender: UserSender
    chat: Chat
    mentions: MentionList = field(default_factory=MentionList)
    forward: Optional[Forward] = None
    reply: Optional[Reply] = None
    file: Optional[IncomingFileAttachment] = None
    location: Optional[Location] = None
    contact: Optional[Contact] = None
    link: Optional[Link] = None
    sticker: Optional[Sticker] = None

    state: SimpleNamespace = field(default_factory=SimpleNamespace)

    @property
    def argument(self) -> str:
        split_body = self.body.split()
        if not split_body:
            return ""

        command_len = len(split_body[0])
        return self.body[command_len:].strip()

    @property
    def arguments(self) -> Tuple[str, ...]:
        return tuple(arg.strip() for arg in self.argument.split())


BotAPIEntity = Union[BotAPIMention, BotAPIForward, BotAPIReply]
Entity = Union[Mention, Forward, Reply]


def _convert_bot_api_mention_to_domain(api_mention_data: BotAPIMentionData) -> Mention:
    mention_data = cast(BotAPINestedMentionData, api_mention_data.mention_data)

    if api_mention_data.mention_type == BotAPIMentionTypes.USER:
        return MentionBuilder.user(
            entity_id=mention_data.entity_id,
            name=mention_data.name,
        )

    if api_mention_data.mention_type == BotAPIMentionTypes.CHAT:
        return MentionBuilder.chat(
            entity_id=mention_data.entity_id,
            name=mention_data.name,
        )

    if api_mention_data.mention_type == BotAPIMentionTypes.CONTACT:
        return MentionBuilder.contact(
            entity_id=mention_data.entity_id,
            name=mention_data.name,
        )

    if api_mention_data.mention_type == BotAPIMentionTypes.CHANNEL:
        return MentionBuilder.channel(
            entity_id=mention_data.entity_id,
            name=mention_data.name,
        )

    if api_mention_data.mention_type == BotAPIMentionTypes.ALL:
        return MentionBuilder.all()

    raise NotImplementedError(
        f"Unsupported mention type: {api_mention_data.mention_type}",
    )


def convert_bot_api_entity_to_domain(api_entity: BotAPIEntity) -> Entity:
    if api_entity.type == BotAPIEntityTypes.MENTION:
        api_entity = cast(BotAPIMention, api_entity)
        return _convert_bot_api_mention_to_domain(api_entity.data)

    if api_entity.type == BotAPIEntityTypes.FORWARD:
        api_entity = cast(BotAPIForward, api_entity)

        return Forward(
            chat_id=api_entity.data.group_chat_id,
            author_id=api_entity.data.sender_huid,
            sync_id=api_entity.data.source_sync_id,
            chat_name=api_entity.data.source_chat_name,
            forward_type=convert_chat_type_to_domain(api_entity.data.forward_type),
            inserted_at=api_entity.data.source_inserted_at,
        )

    if api_entity.type == BotAPIEntityTypes.REPLY:
        api_entity = cast(BotAPIReply, api_entity)

        mentions = MentionList()
        for api_mention_data in api_entity.data.mentions:
            mentions.append(_convert_bot_api_mention_to_domain(api_mention_data))

        return Reply(
            author_id=api_entity.data.sender,
            sync_id=api_entity.data.source_sync_id,
            body=api_entity.data.body,
            mentions=mentions,
        )

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

    source_sync_id: Optional[UUID]
    attachments: List[Union[BotAPIAttachment, Dict[str, Any]]]  # noqa: WPS234
    entities: List[Union[BotAPIEntity, Dict[str, Any]]]  # noqa: WPS234

    def to_domain(self, raw_command: Dict[str, Any]) -> IncomingMessage:  # noqa: WPS231
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

        file: Optional[IncomingFileAttachment] = None
        location: Optional[Location] = None
        contact: Optional[Contact] = None
        link: Optional[Link] = None
        sticker: Optional[Sticker] = None

        if self.attachments:
            # Always one attachment per-message
            if isinstance(self.attachments[0], dict):
                logger.warning("Received unknown attachment type")
            else:
                attachment_domain = convert_api_attachment_to_domain(
                    self.attachments[0],
                    self.payload.body,
                )
                if isinstance(attachment_domain, FileAttachmentBase):  # noqa: WPS223
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
        forward: Optional[Forward] = None
        reply: Optional[Reply] = None
        for entity in self.entities:
            if isinstance(entity, dict):
                logger.warning("Received unknown entity type")
            else:
                entity_domain = convert_bot_api_entity_to_domain(entity)
                if isinstance(
                    entity_domain,
                    Mention.__args__,  # type: ignore [attr-defined]  # noqa: WPS609
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
