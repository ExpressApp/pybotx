from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import Field

from botx.bot.api.commands.base import (
    BotAPIBaseCommand,
    BotAPICommandPayload,
    BotAPIUserEventSender,
)
from botx.bot.api.enums import convert_client_platform
from botx.bot.models.commands.incoming_message import (
    Chat,
    ExpressApp,
    IncomingMessage,
    UserDevice,
    UserEventSender,
)
from botx.shared_models.chat_types import convert_chat_type_to_domain


class BotAPIIncomingMessage(BotAPIBaseCommand):
    payload: BotAPICommandPayload = Field(..., alias="command")
    sender: BotAPIUserEventSender = Field(..., alias="from")
    source_sync_id: Optional[UUID]

    def to_domain(self, raw_command: Dict[str, Any]) -> IncomingMessage:
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
        )
