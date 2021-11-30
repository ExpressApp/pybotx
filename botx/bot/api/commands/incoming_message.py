from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field

from botx.bot.api.attachments import BotAPIAttachment, convert_api_attachment_to_domain
from botx.bot.api.commands.base import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotAPICommandPayload,
    BotAPIDeviceContext,
    BotAPIUserContext,
)
from botx.bot.api.entities import BotAPIEntity, convert_bot_api_entity_to_domain
from botx.bot.api.enums import convert_client_platform
from botx.bot.models.commands.chat import Chat
from botx.bot.models.commands.entities import Forward, Mention, Reply
from botx.bot.models.commands.enums import AttachmentTypes
from botx.bot.models.commands.incoming_message import (
    ExpressApp,
    IncomingMessage,
    UserDevice,
    UserEventSender,
)
from botx.bot.models.commands.mentions import MentionList
from botx.shared_models.api.async_file import APIAsyncFile, convert_async_file_to_file
from botx.shared_models.chat_types import convert_chat_type_to_domain
from botx.shared_models.domain.attachments import (
    AttachmentContact,
    AttachmentLink,
    AttachmentLocation,
    FileAttachmentBase,
    IncomingFileAttachment,
)
from botx.shared_models.domain.files import File


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
