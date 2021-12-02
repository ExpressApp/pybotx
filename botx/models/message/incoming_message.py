from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from pydantic import Field

from botx.models.async_files import APIAsyncFile, File, convert_async_file_to_file
from botx.models.attachments import (
    AttachmentContact,
    AttachmentLink,
    AttachmentLocation,
    BotAPIAttachment,
    FileAttachmentBase,
    IncomingFileAttachment,
    convert_api_attachment_to_domain,
)
from botx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotAPICommandPayload,
    BotAPIDeviceContext,
    BotAPIUserContext,
    BotCommandBase,
)
from botx.models.chat import Chat
from botx.models.enums import (
    AttachmentTypes,
    ClientPlatforms,
    convert_chat_type_to_domain,
    convert_client_platform,
)
from botx.models.message.entities import (
    BotAPIEntity,
    Forward,
    Mention,
    MentionList,
    Reply,
    convert_bot_api_entity_to_domain,
)


@dataclass
class ExpressApp:
    pushes: Optional[bool]
    timezone: Optional[str]
    permissions: Optional[Dict[str, Any]]
    platform: Optional[ClientPlatforms]
    platform_package_id: Optional[str]
    version: Optional[str]


@dataclass
class UserDevice:
    manufacturer: Optional[str]
    name: Optional[str]
    os: Optional[str]


@dataclass
class UserEventSender:
    huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    username: Optional[str]
    is_chat_admin: Optional[bool]
    is_chat_creator: Optional[bool]
    locale: Optional[str]
    express_app: ExpressApp
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
    sender: UserEventSender
    chat: Chat
    mentions: MentionList = field(default_factory=MentionList)
    forward: Optional[Forward] = None
    reply: Optional[Reply] = None
    file: Optional[Union[File, IncomingFileAttachment]] = None
    location: Optional[AttachmentLocation] = None
    contact: Optional[AttachmentContact] = None
    link: Optional[AttachmentLink] = None

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
    attachments: List[BotAPIAttachment]
    async_files: List[APIAsyncFile]
    entities: List[BotAPIEntity]

    def to_domain(self, raw_command: Dict[str, Any]) -> IncomingMessage:  # noqa: WPS231
        device = UserDevice(
            manufacturer=self.sender.manufacturer,
            name=self.sender.device,
            os=self.sender.device_software,
        )
        express_app = ExpressApp(
            pushes=self.sender.device_meta.pushes,
            timezone=self.sender.device_meta.timezone,
            permissions=self.sender.device_meta.permissions,
            platform=(
                convert_client_platform(self.sender.platform)
                if self.sender.platform
                else None
            ),
            platform_package_id=self.sender.platform_package_id,
            version=self.sender.app_version,
        )
        sender = UserEventSender(
            huid=self.sender.user_huid,
            ad_login=self.sender.ad_login,
            ad_domain=self.sender.ad_domain,
            username=self.sender.username,
            is_chat_admin=self.sender.is_admin,
            is_chat_creator=self.sender.is_creator,
            locale=self.sender.locale,
            device=device,
            express_app=express_app,
        )

        chat = Chat(
            id=self.sender.group_chat_id,
            type=convert_chat_type_to_domain(self.sender.chat_type),
            host=self.sender.host,
        )

        file: Optional[Union[File, IncomingFileAttachment]] = None
        location: Optional[AttachmentLocation] = None
        contact: Optional[AttachmentContact] = None
        link: Optional[AttachmentLink] = None
        if self.async_files:
            # Always one async file per-message
            file = convert_async_file_to_file(self.async_files[0])
        elif self.attachments:
            # Always one attachment per-message
            attachment_domain = convert_api_attachment_to_domain(self.attachments[0])
            if isinstance(attachment_domain, FileAttachmentBase):
                file = attachment_domain
            elif attachment_domain.type == AttachmentTypes.LOCATION:
                location = attachment_domain
            elif attachment_domain.type == AttachmentTypes.CONTACT:
                contact = attachment_domain
            elif attachment_domain.type == AttachmentTypes.LINK:
                link = attachment_domain
            else:
                raise NotImplementedError

        mentions: MentionList = MentionList()
        forward: Optional[Forward] = None
        reply: Optional[Reply] = None
        for entity in self.entities:
            entity_domain = convert_bot_api_entity_to_domain(entity)
            if isinstance(entity_domain, Mention):
                mentions.append(entity_domain)
            elif isinstance(entity_domain, Forward):
                # Max one forward per message
                forward = entity_domain
            elif isinstance(entity_domain, Reply):
                # Max one reply per message
                reply = entity_domain
            else:
                raise NotImplementedError

        return IncomingMessage(
            bot_id=self.bot_id,
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
            mentions=mentions,
            forward=forward,
            reply=reply,
        )
