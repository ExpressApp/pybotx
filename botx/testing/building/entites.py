"""Mixin for building entities."""

import uuid
from dataclasses import field
from datetime import datetime
from typing import Optional

from botx.models.attachments_meta import DocumentAttachmentMeta
from botx.models.entities import (
    ChatMention,
    Entity,
    EntityList,
    Forward,
    Mention,
    MentionTypes,
    Reply,
    UserMention,
)
from botx.models.enums import ChatTypes, EntityTypes
from botx.models.messages.message import Message


class BuildEntityMixin:
    """Mixin for building entities in message."""

    entities: EntityList = field(default_factory=list)  # type: ignore

    def mention_contact(self, user_huid: uuid.UUID) -> None:
        """Add contact mention to message for bot.

        Arguments:
            user_huid: huid of user to mention.
        """
        self.entities.__root__.append(
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
        self.entities.__root__.append(
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
        self.entities.__root__.append(
            Entity(
                type=EntityTypes.mention,
                data=Mention(
                    mention_data=ChatMention(group_chat_id=chat_id),
                    mention_type=MentionTypes.chat,
                ),
            ),
        )

    def mention(self, mention: Mention) -> None:
        """Add mention by mention model.

        Arguments:
            mention: mention model to build.
        """
        self.entities.__root__.append(Entity(type=EntityTypes.mention, data=mention))

    def reply(
        self,
        *,
        message: Optional[Message] = None,
        reply: Optional[Reply] = None,
        source_chat_name: str = "chat",
    ) -> None:
        """Add reply to message for bot.

        Arguments:
            message: replied message.
            reply: reply model to build.
            source_chat_name: name of chat where message was reply.

        Raises:
            ValueError: raise if conflict of requirement arguments.
        """
        if message and not reply:
            mentions = message.entities.mentions

            reply = Reply(
                attachment=DocumentAttachmentMeta(file_name="test.doc"),
                body=message.body,
                mentions=mentions,
                reply_type=ChatTypes(message.chat_type),
                sender=message.user_huid,  # type: ignore
                source_chat_name=source_chat_name,
                source_sync_id=message.sync_id,
                source_group_chat_id=message.group_chat_id,
            )
        elif reply and not message:
            pass  # noqa: WPS420
        else:
            raise ValueError("Must be replied message of reply model")
        self.entities.__root__.append(Entity(type=EntityTypes.reply, data=reply))

    def forward(
        self,
        *,
        message: Optional[Message] = None,
        forward: Optional[Forward] = None,
        source_chat_name: str = "chat",
        source_inserted_at: datetime = datetime(  # noqa: B008, WPS404
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            None,
        ),
    ) -> None:
        """Add forward to message for bot.

        Arguments:
            message: forwarded message.
            forward: forward model to build.
            source_chat_name: name of chat where message was forward.
            source_inserted_at: ts of forwarded message.

        Raises:
            ValueError: raise if conflict of requirement arguments.
        """
        if message and not forward:
            forward = Forward(
                group_chat_id=message.group_chat_id,
                sender_huid=message.user_huid or uuid.uuid4(),
                forward_type=ChatTypes(message.chat_type),
                source_chat_name=source_chat_name,
                source_sync_id=message.sync_id,
                source_inserted_at=source_inserted_at,
            )
        elif forward and not message:
            pass  # noqa: WPS420
        else:
            raise ValueError("Must be forwarding message or forward")

        self.entities.__root__.append(Entity(type=EntityTypes.forward, data=forward))
