"""Message that is sent from bot."""
import re
from typing import Any  # noqa: WPS235
from typing import BinaryIO, Dict, List, Optional, TextIO, Tuple, Union, cast
from uuid import UUID

from botx.models.buttons import ButtonOptions
from botx.models.entities import ChatMention, Mention, UserMention
from botx.models.enums import MentionTypes
from botx.models.files import File
from botx.models.messages.message import Message
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.markup import MessageMarkup
from botx.models.messages.sending.options import MessageOptions, NotificationOptions
from botx.models.messages.sending.payload import MessagePayload
from botx.models.typing import AvailableRecipients, BubbleMarkup, KeyboardMarkup

try:
    from typing import Final  # noqa: WPS433
except ImportError:
    from typing_extensions import Final  # type: ignore  # noqa: WPS433, WPS440, F401

ARGUMENTS_DUPLICATION_ERROR = (
    "{0} can not be passed along with manual validated_values for it"
)

EMBED_MENTION_TEMPATE = (
    "<embed_mention:{mention_type}:"
    "{mentioned_entity_id}:{mention_id}:{mention_name}>"  # noqa: WPS326
)
EMBED_MENTION_RE: Final = re.compile(
    "<embed_mention:(?P<mention_type>.+?):(?P<mentioned_entity_id>.+?)"
    ":(?P<mention_id>.+?):(?P<name>.+?)?>",  # noqa: WPS326 C812
)


# currently I have no idea how to clean this.
class SendingMessage:  # noqa: WPS214
    """Message that will be sent by bot."""

    def __init__(  # noqa: WPS211
        self,
        *,
        text: str = "",
        bot_id: Optional[UUID] = None,
        host: Optional[str] = None,
        sync_id: Optional[UUID] = None,
        chat_id: Optional[UUID] = None,
        message_id: Optional[UUID] = None,
        recipients: Optional[AvailableRecipients] = None,
        mentions: Optional[List[Mention]] = None,
        bubbles: Optional[BubbleMarkup] = None,
        keyboard: Optional[KeyboardMarkup] = None,
        notification_options: Optional[NotificationOptions] = None,
        file: Optional[File] = None,
        credentials: Optional[SendingCredentials] = None,
        options: Optional[MessageOptions] = None,
        markup: Optional[MessageMarkup] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embed_mentions: bool = False,
    ) -> None:
        """Init message with required attributes.

        !!! info
            You should pass at least already built credentials or bot_id, host and
            one of sync_id, chat_id or chat_ids for message.
        !!! info
            You can not pass markup along with bubbles or keyboards. You can merge them
            manual before or after building message.
        !!! info
            You can not pass options along with any of recipients, mentions or
            notification_options. You can merge them manual before or after building
            message.

        Arguments:
            text: text for message.
            file: file that will be attached to message.
            bot_id: bot id.
            host: host for message.
            sync_id: message event id.
            chat_id: chat id.
            message_id: custom id of new message.
            credentials: message credentials.
            bubbles: bubbles that will be attached to message.
            keyboard: keyboard elements that will be attached to message.
            markup: message markup.
            recipients: recipients for message.
            mentions: mentions that will be attached to message.
            notification_options: configuration for notifications for message.
            options: message options.
            metadata: message metadata.
            embed_mentions: get mentions from text.
        """
        self.credentials: SendingCredentials = _build_credentials(
            bot_id=bot_id,
            host=host,
            sync_id=sync_id,
            message_id=message_id,
            chat_id=chat_id,
            credentials=(credentials.copy() if credentials else credentials),
        )

        options = _build_options(
            recipients=recipients,
            mentions=mentions,
            notification_options=notification_options,
            options=options,
        )
        if embed_mentions:
            updated_text, found_mentions = self._find_and_replace_embed_mentions(text)

            text = updated_text
            options.mentions = found_mentions
            options.raw_mentions = True

        self.payload: MessagePayload = MessagePayload(
            text=text,
            metadata=metadata or {},
            file=file,
            markup=_build_markup(bubbles=bubbles, keyboard=keyboard, markup=markup),
            options=options,
        )

    @classmethod
    def from_message(
        cls,
        *,
        text: str = "",
        file: Optional[File] = None,
        message: Message,
    ) -> "SendingMessage":
        """Build message for sending from incoming message.

        Arguments:
            text: text for message.
            file: file attached to message.
            message: incoming message.

        Returns:
            Built message.
        """
        return cls(
            text=text,
            file=file,
            sync_id=message.sync_id,
            chat_id=message.group_chat_id,
            bot_id=message.bot_id,
            host=message.host,
        )

    @classmethod
    def make_mention_embeddable(cls, mention: Mention) -> str:
        """Get mention as string, which can be embed in text.

        Arguments:
            mention: mention for embedding.

        Raises:
            NotImplementedError: If unsupported mention type was passed.

        Returns:
            Formatted mention.
        """
        if mention.mention_type in {MentionTypes.user, MentionTypes.contact}:
            assert isinstance(mention.mention_data, UserMention)  # for mypy
            mentioned_entity_id = mention.mention_data.user_huid
        elif mention.mention_type in {MentionTypes.chat, MentionTypes.channel}:
            assert isinstance(mention.mention_data, ChatMention)  # for mypy
            mentioned_entity_id = mention.mention_data.group_chat_id
        else:
            raise NotImplementedError("Unsupported mention type")

        mention_name = mention.mention_data.name or ""

        return EMBED_MENTION_TEMPATE.format(
            mention_type=mention.mention_type,
            mentioned_entity_id=mentioned_entity_id,
            mention_id=mention.mention_id,
            mention_name=mention_name,
        )

    @classmethod
    def build_embeddable_user_mention(
        cls,
        user_huid: UUID,
        name: Optional[str] = None,
        mention_id: Optional[UUID] = None,
    ) -> str:
        """Get user mention as string, which can be embed in text.

        Arguments:
            user_huid: user id to mention.
            name: for overriding mention name.
            mention_id: mention id (if not passed, will be generated).

        Returns:
            Formatted mention.
        """
        mention = Mention.build_from_values(
            MentionTypes.user,
            user_huid,
            name,
            mention_id,
        )

        return cls.make_mention_embeddable(mention)

    @classmethod
    def build_embeddable_contact_mention(
        cls,
        user_huid: UUID,
        name: Optional[str] = None,
        mention_id: Optional[UUID] = None,
    ) -> str:
        """Get contact mention as string, which can be embed in text.

        Arguments:
            user_huid: user id to mention.
            name: for overriding mention name.
            mention_id: mention id (if not passed, will be generated).

        Returns:
            Formatted mention.
        """
        mention = Mention.build_from_values(
            MentionTypes.contact,
            user_huid,
            name,
            mention_id,
        )

        return cls.make_mention_embeddable(mention)

    @classmethod
    def build_embeddable_chat_mention(
        cls,
        group_chat_id: UUID,
        name: Optional[str] = None,
        mention_id: Optional[UUID] = None,
    ) -> str:
        """Get chat mention as string, which can be embed in text.

        Arguments:
            group_chat_id: chat id to mention.
            name: for overriding mention name.
            mention_id: mention id (if not passed, will be generated).

        Returns:
            Formatted mention.
        """
        mention = Mention.build_from_values(
            MentionTypes.chat,
            group_chat_id,
            name,
            mention_id,
        )

        return cls.make_mention_embeddable(mention)

    @classmethod
    def build_embeddable_channel_mention(
        cls,
        group_chat_id: UUID,
        name: Optional[str] = None,
        mention_id: Optional[UUID] = None,
    ) -> str:
        """Get channel mention as string, which can be embed in text.

        Arguments:
            group_chat_id: channel id to mention.
            name: for overriding mention name.
            mention_id: mention id (if not passed, will be generated).

        Returns:
            Formatted mention.
        """
        mention = Mention.build_from_values(
            MentionTypes.channel,
            group_chat_id,
            name,
            mention_id,
        )

        return cls.make_mention_embeddable(mention)

    @property
    def text(self) -> str:
        """Text in message."""
        return self.payload.text

    @text.setter
    def text(self, text: str) -> None:
        """Text in message."""
        self.payload.text = text

    @property
    def metadata(self) -> Dict[str, Any]:
        """Metadata in message."""
        return self.payload.metadata

    @metadata.setter
    def metadata(self, metadata: Dict[str, Any]) -> None:
        self.payload.metadata = metadata

    @property
    def file(self) -> Optional[File]:
        """File attached to message."""
        return self.payload.file

    @file.setter
    def file(self, file: File) -> None:
        """File attached to message."""
        self.payload.file = file

    @property
    def markup(self) -> MessageMarkup:
        """Message markup."""
        return self.payload.markup

    @markup.setter
    def markup(self, markup: MessageMarkup) -> None:
        """Message markup."""
        self.payload.markup = markup

    @property
    def options(self) -> MessageOptions:
        """Message options."""
        return self.payload.options

    @options.setter
    def options(self, options: MessageOptions) -> None:
        """Message options."""
        self.payload.options = options

    @property
    def sync_id(self) -> Optional[UUID]:
        """Event id on which message should answer."""
        return self.credentials.sync_id

    @sync_id.setter
    def sync_id(self, sync_id: UUID) -> None:
        """Event id on which message should answer."""
        self.credentials.sync_id = sync_id

    @property
    def chat_id(self) -> Optional[UUID]:
        """Chat id in which message should be sent."""
        return self.credentials.chat_id

    @chat_id.setter
    def chat_id(self, chat_id: UUID) -> None:
        """Chat id in which message should be sent."""
        self.credentials.chat_id = chat_id

    @property
    def bot_id(self) -> UUID:
        """Bot id that handles message."""
        return cast(UUID, self.credentials.bot_id)

    @bot_id.setter
    def bot_id(self, bot_id: UUID) -> None:
        """Bot id that handles message."""
        self.credentials.bot_id = bot_id

    @property
    def host(self) -> str:
        """Host where BotX API places."""
        return cast(str, self.credentials.host)

    @host.setter
    def host(self, host: str) -> None:
        """Host where BotX API places."""
        self.credentials.host = host

    def add_file(
        self,
        file: Union[TextIO, BinaryIO, File],
        filename: Optional[str] = None,
    ) -> None:
        """Attach file to message.

        Arguments:
            file: file that should be attached to the message.
            filename: name for file that will be used if if can not be retrieved from
                file.
        """
        if isinstance(file, File):
            file.file_name = filename or file.file_name
            self.payload.file = file
        else:
            self.payload.file = File.from_file(file, filename=filename)

    def mention_user(self, user_huid: UUID, name: Optional[str] = None) -> None:
        """Mention user in message.

        Arguments:
            user_huid: id of user that should be mentioned.
            name: name that will be shown.
        """
        self.payload.options.mentions.append(
            Mention(mention_data=UserMention(user_huid=user_huid, name=name)),
        )

    def mention_contact(self, user_huid: UUID, name: Optional[str] = None) -> None:
        """Mention contact in message.

        Arguments:
            user_huid: id of user that should be mentioned.
            name: name that will be shown.
        """
        self.payload.options.mentions.append(
            Mention(
                mention_data=UserMention(user_huid=user_huid, name=name),
                mention_type=MentionTypes.contact,
            ),
        )

    def mention_chat(self, group_chat_id: UUID, name: Optional[str] = None) -> None:
        """Mention chat in message.

        Arguments:
            group_chat_id: id of chat that should be mentioned.
            name: name that will be shown.
        """
        self.payload.options.mentions.append(
            Mention(
                mention_data=ChatMention(group_chat_id=group_chat_id, name=name),
                mention_type=MentionTypes.chat,
            ),
        )

    def add_recipient(self, recipient: UUID) -> None:
        """Add new user that will receive message.

        Arguments:
            recipient: recipient for message.
        """
        if self.payload.options.recipients == "all":
            self.payload.options.recipients = []

        self.payload.options.recipients.append(recipient)

    def add_recipients(self, recipients: List[UUID]) -> None:
        """Add list of recipients that should receive message.

        Arguments:
            recipients: recipients for message.
        """
        if self.payload.options.recipients == "all":
            self.payload.options.recipients = []

        self.payload.options.recipients.extend(recipients)

    def add_bubble(  # noqa: WPS211
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,  # noqa: WPS110
        options: Optional[ButtonOptions] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new bubble button to message markup.

        Arguments:
            command: command that will be triggered on bubble click.
            label: label that will be shown on bubble.
            data: payload that will be attached to bubble.
            options: add special effects to bubble.
            new_row: place bubble on new row or on current.
        """
        self.payload.markup.add_bubble(command, label, data, options, new_row=new_row)

    def add_keyboard_button(  # noqa: WPS211
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,  # noqa: WPS110
        options: Optional[ButtonOptions] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new keyboard button to message markup.

        Arguments:
            command: command that will be triggered on keyboard click.
            label: label that will be shown on keyboard button.
            data: payload that will be attached to keyboard.
            options: add special effects to keyboard button.
            new_row: place keyboard on new row or on current.
        """
        self.payload.markup.add_keyboard_button(
            command,
            label,
            data,
            options,
            new_row=new_row,
        )

    def show_notification(self, show: bool) -> None:
        """Show notification about message.

        Arguments:
            show: show notification about message.
        """
        self.payload.options.notifications.send = show

    def force_notification(self, force: bool) -> None:
        """Break mute on bot messages.

        Arguments:
            force: break mute on bot messages.
        """
        self.payload.options.notifications.force_dnd = force

    def _find_and_replace_embed_mentions(  # noqa: WPS210
        self,
        text: str,
    ) -> Tuple[str, List[Mention]]:
        mentions = []

        match = EMBED_MENTION_RE.search(text)
        while match:
            mention_dict = match.groupdict()
            embed_mention = match.group(0)

            mention = Mention.build_from_values(
                MentionTypes(mention_dict["mention_type"]),
                UUID(mention_dict["mentioned_entity_id"]),
                mention_dict["name"],
                UUID(mention_dict["mention_id"]),
            )

            text = text.replace(embed_mention, mention.to_botx_format())
            mentions.append(mention)

            match = EMBED_MENTION_RE.search(text)

        return text, mentions


def _build_credentials(  # noqa: WPS211
    bot_id: Optional[UUID] = None,
    host: Optional[str] = None,
    sync_id: Optional[UUID] = None,
    message_id: Optional[UUID] = None,
    chat_id: Optional[UUID] = None,
    credentials: Optional[SendingCredentials] = None,
) -> SendingCredentials:
    """Build credentials for message.

    Arguments:
        bot_id: bot id.
        host: host for message.
        sync_id: message event id.
        message_id: id of new message.
        chat_id: chat id.
        credentials: message credentials.

    Returns:
        Credentials for message.

    Raises:
        AssertionError: raised if credentials were passed with separate parameters.
    """
    if bot_id and host:
        if credentials is not None:
            raise AssertionError(
                ARGUMENTS_DUPLICATION_ERROR.format("MessageCredentials"),
            )

        return SendingCredentials(
            bot_id=bot_id,
            host=host,
            sync_id=sync_id,
            chat_id=chat_id,
            message_id=message_id,
        )

    if credentials is None:
        raise AssertionError(
            "MessageCredentials or manual validated_values should be passed",
        )

    if credentials.message_id is None:
        credentials.message_id = message_id

    return credentials


def _build_markup(
    bubbles: Optional[BubbleMarkup] = None,
    keyboard: Optional[KeyboardMarkup] = None,
    markup: Optional[MessageMarkup] = None,
) -> MessageMarkup:
    """Build markup for message.

    Arguments:
        bubbles: bubbles that will be attached to message.
        keyboard: keyboard elements that will be attached to message.
        markup: message markup.

    Returns:
        Markup for message.

    Raises:
        AssertionError: raised if markup were passed with separate parameters.
    """
    if bubbles is not None or keyboard is not None:
        if markup is not None:
            raise AssertionError(
                "Markup can not be passed along with bubbles or keyboard elements",
            )
        return MessageMarkup(bubbles=bubbles or [], keyboard=keyboard or [])

    return markup or MessageMarkup()


def _build_options(
    recipients: Optional[AvailableRecipients] = None,
    mentions: Optional[List[Mention]] = None,
    notification_options: Optional[NotificationOptions] = None,
    options: Optional[MessageOptions] = None,
) -> MessageOptions:
    """Build options for message.

    Arguments:
        recipients: recipients for message.
        mentions: mentions that will be attached to message.
        notification_options: configuration for notifications for message.
        options: message options.

    Returns:
        Options for message.

    Raises:
        AssertionError: raised if options were passed with separate parameters.
    """
    if mentions or recipients or notification_options:
        if options is not None:
            raise AssertionError(ARGUMENTS_DUPLICATION_ERROR.format("MessageOptions"))
        return MessageOptions(
            recipients=recipients or "all",
            mentions=mentions or [],
            notifications=notification_options or NotificationOptions(),
        )

    return options or MessageOptions()
