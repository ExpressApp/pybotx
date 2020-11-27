"""Builder for messages in tests."""

import uuid
from dataclasses import field
from typing import Any, List, Optional

from pydantic import BaseConfig, validator
from pydantic.dataclasses import dataclass

from botx import ChatMention, Mention, MentionTypes, UserMention
from botx.models import enums
from botx.models.attachments import (
    AttachList,
    Attachment,
    Contact,
    Document,
    Image,
    Link,
    Location,
    Video,
    Voice,
)
from botx.models.enums import AttachmentsTypes, ChatTypes, EntityTypes
from botx.models.messages.incoming_message import (
    Command,
    Entity,
    IncomingMessage,
    Sender,
)
from botx.testing import content as test_content
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
    )


class BuilderConfig(BaseConfig):
    """Config for builder dataclass."""

    validate_assignment = True


@dataclass(config=BuilderConfig)
class MessageBuilder:  # noqa: WPS214
    """Builder for command message for bot."""

    bot_id: uuid.UUID = field(default_factory=uuid.uuid4)

    command_data: dict = field(default_factory=dict)
    system_command: bool = field(default=False)
    file: Optional[Any] = field(default=None)
    attachments: AttachList = field(default_factory=list)  # type: ignore
    user: Sender = field(default_factory=_build_default_user)
    entities: List[Entity] = field(default_factory=list)
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
        command_type = (
            enums.CommandTypes.system
            if self.system_command
            else enums.CommandTypes.user
        )
        command = Command(
            body=self.body, command_type=command_type, data=self.command_data,
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

    def mention_contact(self, user_huid: uuid.UUID) -> None:
        """Add contact mention to message for bot.

        Arguments:
            user_huid: huid of user to mention.
        """
        self.entities.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(
                    mention_data=UserMention(user_huid=user_huid),
                    mention_type=MentionTypes.contact,
                ),
            ),
        )

    def mention_user(self, user_huid: uuid.UUID) -> None:
        """Add user mention to message for bot.

        Arguments:
            user_huid: huid of user to mention.
        """
        self.entities.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(mention_data=UserMention(user_huid=user_huid)),
            ),
        )

    def mention_chat(self, chat_id: uuid.UUID) -> None:
        """Add chat mention to message for bot.

        Arguments:
            chat_id: id of chat to mention.
        """
        self.entities.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(
                    mention_data=ChatMention(group_chat_id=chat_id),
                    mention_type=MentionTypes.chat,
                ),
            ),
        )

    def image(
        self,
        content: str = test_content.PNG_DATA,  # noqa: WPS110
        file_name: str = "image.jpg",
    ) -> None:
        """Add image into incoming message.

        Arguments:
            content: image content in RFC 2397 format.
            file_name: name of file.
        """
        self.attachments.__root__.append(
            Attachment(
                type=AttachmentsTypes.image,
                data=Image(content=content, file_name=file_name),
            ),
        )

    def document(
        self,
        content: str = test_content.DOCX_DATA,  # noqa: WPS110
        file_name: str = "document.docx",
    ) -> None:
        """Add document into incoming message.

        Arguments:
            content: document content in RFC 2397 format.
            file_name: name of file.
        """
        self.attachments.__root__.append(
            Attachment(
                type=AttachmentsTypes.document,
                data=Document(content=content, file_name=file_name),
            ),
        )

    def location(
        self,
        location_name: str = "loc_name",
        location_address: str = "loc_address",
        location_lat: int = 0,
        location_lng: int = 0,
    ) -> None:
        """Add location into incoming message.

        Arguments:
            location_name: name of location.
            location_lat: latitude.
            location_lng: longitude.
            location_address: address of location.
        """
        self.attachments.__root__.append(
            Attachment(
                type=AttachmentsTypes.location,
                data=Location(
                    location_name=location_name,
                    location_lat=location_lat,
                    location_lng=location_lng,
                    location_address=location_address,
                ),
            ),
        )

    def voice(
        self, content: str = test_content.MP3_DATA, duration: int = 10,  # noqa: WPS110
    ) -> None:
        """Add voice into incoming message.

        Arguments:
            content: voice content in RFC 2397 format.
            duration: voice duration.
        """
        self.attachments.__root__.append(
            Attachment(
                type=AttachmentsTypes.voice,
                data=Voice(duration=duration, content=content),
            ),
        )

    def video(
        self,
        content: str = test_content.MP4_DATA,  # noqa: WPS110
        file_name: str = "video.mp4",
        duration: int = 10,
    ) -> None:
        """Add video into incoming message.

        Arguments:
            content: voice content in RFC 2397 format.
            file_name: name of file.
            duration: video duration.
        """
        self.attachments.__root__.append(
            Attachment(
                type=AttachmentsTypes.video,
                data=Video(content=content, file_name=file_name, duration=duration),
            ),
        )

    def link(
        self,
        url: str = "https://google.com",
        url_preview: str = "https://image.jpg",
        url_text: str = "foo",
        url_title: str = "bar",
    ) -> None:
        """Add link into incoming message.

        Arguments:
            url: link on resource.
            url_preview: link on url preview.
            url_text: presented text on link.
            url_title: title of link.
        """
        self.attachments.__root__.append(
            Attachment(
                type=AttachmentsTypes.link,
                data=Link(
                    url=url,
                    url_preview=url_preview,
                    url_text=url_text,
                    url_title=url_title,
                ),
            ),
        )

    def contact(self, contact_name: str = "Foo") -> None:
        """Add link into incoming message.

        Arguments:
            contact_name: name of contact
        """
        self.attachments.__root__.append(
            Attachment(
                type=AttachmentsTypes.contact, data=Contact(contact_name=contact_name),
            ),
        )
