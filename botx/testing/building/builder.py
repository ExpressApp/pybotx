"""Builder for messages in tests."""

import uuid
from dataclasses import field
from typing import Any, Optional

from pydantic import BaseConfig, validator
from pydantic.dataclasses import dataclass

from botx.models.attachments import AttachList
from botx.models.entities import EntityList
from botx.models.enums import ChatTypes, ClientPlatformEnum, CommandTypes
from botx.models.messages.incoming_message import (
    Command,
    DeviceMeta,
    IncomingMessage,
    Sender,
)
from botx.testing.building.attachments import BuildAttachmentsMixin
from botx.testing.building.entites import BuildEntityMixin
from botx.testing.building.validators import (
    convert_to_acceptable_file,
    validate_body_corresponds_command,
    validate_command_type_corresponds_command,
)


def _build_default_user() -> Sender:
    return Sender(
        user_huid=uuid.uuid4(),
        group_chat_id=uuid.uuid4(),
        chat_type=ChatTypes.chat,
        ad_login="test_user",
        ad_domain="example.com",
        username="Test User",
        is_admin=True,
        is_creator=True,
        host="cts.example.com",
        manufacturer="Google",
        device="Chrome 87.0",
        device_software="macOS 10.15.7",
        device_meta=DeviceMeta(
            pushes=False,
            timezone="Asia/Novosibirsk",
            permissions={"microphone": True, "notifications": False},
        ),
        platform=ClientPlatformEnum.web,
        platform_package_id=None,
        app_version="1.15.52",
        locale="en",
    )


class BuilderConfig(BaseConfig):
    """Config for builder dataclass."""

    validate_assignment = True


@dataclass(config=BuilderConfig)
class MessageBuilder(BuildAttachmentsMixin, BuildEntityMixin):  # noqa: WPS214
    """Builder for command message for bot."""

    bot_id: uuid.UUID = field(default_factory=uuid.uuid4)

    command_data: dict = field(default_factory=dict)
    system_command: bool = field(default=False)
    file: Optional[Any] = field(default=None)
    attachments: AttachList = field(default_factory=list)  # type: ignore
    user: Sender = field(default_factory=_build_default_user)
    entities: EntityList = field(default_factory=list)  # type: ignore
    body: str = field(default="")

    _body_and_command_validator = validator("body", always=True)(
        validate_body_corresponds_command,
    )
    _command_type_and_data_validator = validator("system_command", always=True)(
        validate_command_type_corresponds_command,
    )
    _file_converter = validator("file", always=True)(convert_to_acceptable_file)

    @property
    def message(self) -> IncomingMessage:
        """Message that was built by builder."""
        command_type = CommandTypes.system if self.system_command else CommandTypes.user
        command = Command(
            body=self.body,
            command_type=command_type,
            data=self.command_data,
        )
        return IncomingMessage(
            sync_id=uuid.uuid4(),
            command=command,
            attachments=self.attachments,
            file=self.file,
            bot_id=self.bot_id,
            user=self.user,
            entities=self.entities,
        )
