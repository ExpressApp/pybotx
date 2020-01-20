"""Definition of message object that is used in all bot handlers."""

from typing import BinaryIO, List, Optional, TextIO, Union, cast
from uuid import UUID

from botx import bots
from botx.models.datastructures import State
from botx.models.enums import Recipients
from botx.models.files import File
from botx.models.mentions import ChatMention, Mention, MentionTypes, UserMention
from botx.models.receiving import Command, IncomingMessage, User
from botx.models.sending import (
    MessageMarkup,
    MessageOptions,
    MessagePayload,
    NotificationOptions,
    SendingCredentials,
)
from botx.models.typing import AvailableRecipients, BubbleMarkup, KeyboardMarkup


class Message:  # noqa: WPS214
    """Message that is used in handlers."""

    def __init__(self, message: IncomingMessage, bot: "bots.Bot") -> None:
        """Init message with required params.

        Arguments:
            message: incoming message.
            bot: bot that handles message.
        """
        self.bot: bots.Bot = bot
        """bot that is used for handling message."""
        self.state: State = State()
        """message state."""
        self._message = message

    @property
    def sync_id(self) -> UUID:
        """Event id of message."""
        return self._message.sync_id

    @property
    def command(self) -> Command:
        """Command for bot."""
        return self._message.command

    @property
    def file(self) -> Optional[File]:
        """File attached to message."""
        return self._message.file

    @property
    def user(self) -> User:
        """Information about user that sent message."""
        return self._message.user

    @property
    def bot_id(self) -> UUID:
        """Id of bot that should handle message."""
        return self._message.bot_id

    @property
    def body(self) -> str:
        """Command body."""
        return self.command.body

    @property
    def data(self) -> dict:
        """Command payload."""
        return self.command.data_dict

    @property
    def user_huid(self) -> Optional[UUID]:
        """User huid."""
        return self.user.user_huid

    @property
    def ad_login(self) -> Optional[str]:
        """User AD login."""
        return self.user.ad_login

    @property
    def group_chat_id(self) -> UUID:
        """Chat from which message was received."""
        return self.user.group_chat_id

    @property
    def chat_type(self) -> str:
        """Type of chat."""
        return self.user.chat_type.value

    @property
    def host(self) -> str:
        """Host from which message was received."""
        return self.user.host

    @property
    def credentials(self) -> SendingCredentials:
        """Reply credentials for this message."""
        return SendingCredentials(
            sync_id=self.sync_id, bot_id=self.bot_id, host=self.host
        )

    @property
    def incoming_message(self) -> IncomingMessage:
        """Incoming message from which this was generated."""
        return self._message.copy(deep=True)

    @classmethod
    def from_dict(cls, message: dict, bot: "bots.Bot") -> "Message":
        """Parse incoming dict into message.

        Arguments:
            message: incoming message to bot as dictionary.
            bot: bot that handles message.

        Returns:
            Parsed message.
        """
        incoming_msg = IncomingMessage(**message)
        return cls(incoming_msg, bot)


class SendingMessage:  # noqa: WPS214, WPS230
    """Message that will be sent by bot."""

    def __init__(  # noqa: WPS211
        self,
        *,
        text: str = "",
        bot_id: Optional[UUID] = None,
        host: Optional[str] = None,
        sync_id: Optional[UUID] = None,
        chat_id: Optional[UUID] = None,
        chat_ids: Optional[List[UUID]] = None,
        recipients: Optional[Union[List[UUID], Recipients]] = None,
        mentions: Optional[List[Mention]] = None,
        bubbles: Optional[BubbleMarkup] = None,
        keyboard: Optional[KeyboardMarkup] = None,
        notification_options: Optional[NotificationOptions] = None,
        file: Optional[File] = None,
        credentials: Optional[SendingCredentials] = None,
        options: Optional[MessageOptions] = None,
        markup: Optional[MessageMarkup] = None,
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
            chat_ids: sequence of chat ids.
            credentials: message credentials.
            bubbles: bubbles that will be attached to message.
            keyboard: keyboard elements that will be attached to message.
            markup: message markup.
            recipients: recipients for message.
            mentions: mentions that will be attached to message.
            notification_options: configuration for notifications for message.
            options: message options.
        """
        self.credentials: SendingCredentials = self._built_credentials(
            bot_id=bot_id,
            host=host,
            sync_id=sync_id,
            chat_id=chat_id,
            chat_ids=chat_ids,
            credentials=credentials,
        )

        self.payload: MessagePayload = MessagePayload(
            text=text,
            file=file,
            markup=self._built_markup(
                bubbles=bubbles, keyboard=keyboard, markup=markup
            ),
            options=self._build_options(
                recipients=recipients,
                mentions=mentions,
                notification_options=notification_options,
                options=options,
            ),
        )

    @classmethod
    def from_message(
        cls, *, text: str = "", file: Optional[File] = None, message: Message
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
            bot_id=message.bot_id,
            host=message.host,
        )

    @property
    def text(self) -> str:
        """Text in message."""
        return self.payload.text

    @text.setter  # noqa: WPS440
    def text(self, text: str) -> None:
        """Text in message."""
        self.payload.text = text

    @property
    def file(self) -> Optional[File]:
        """File attached to message."""
        return self.payload.file

    @file.setter  # noqa: WPS440
    def file(self, file: File) -> None:
        """File attached to message."""
        self.payload.file = file

    @property
    def markup(self) -> MessageMarkup:
        """Message markup."""
        return self.payload.markup

    @markup.setter  # noqa: WPS440
    def markup(self, markup: MessageMarkup) -> None:
        """Message markup."""
        self.payload.markup = markup

    @property
    def options(self) -> MessageOptions:
        """Message options."""
        return self.payload.options

    @options.setter  # noqa: WPS440
    def options(self, options: MessageOptions) -> None:
        """Message options."""
        self.payload.options = options

    @property
    def sync_id(self) -> Optional[UUID]:
        """Event id on which message should answer."""
        return self.credentials.sync_id

    @sync_id.setter  # noqa: WPS440
    def sync_id(self, sync_id: UUID) -> None:
        """Event id on which message should answer."""
        self.credentials.sync_id = sync_id

    @property
    def chat_id(self) -> Optional[UUID]:
        """Chat id in which message should be sent."""
        return self.credentials.chat_ids[0]

    @chat_id.setter  # noqa: WPS440
    def chat_id(self, chat_id: UUID) -> None:
        """Chat id in which message should be sent."""
        self.credentials.chat_ids.append(chat_id)

    @property
    def chat_ids(self) -> List[UUID]:
        """Chat ids in which message should be sent."""
        return self.credentials.chat_ids

    @chat_ids.setter  # noqa: WPS440
    def chat_ids(self, chat_ids: List[UUID]) -> None:
        """Chat ids in which message should be sent."""
        self.credentials.chat_ids = chat_ids

    @property
    def bot_id(self) -> UUID:
        """Bot id that handles message."""
        return cast(UUID, self.credentials.bot_id)

    @bot_id.setter  # noqa: WPS440
    def bot_id(self, bot_id: UUID) -> None:
        """Bot id that handles message."""
        self.credentials.bot_id = bot_id

    @property
    def host(self) -> str:
        """Host where BotX API places."""
        return cast(str, self.credentials.host)

    @host.setter  # noqa: WPS440
    def host(self, host: str) -> None:
        """Host where BotX API places."""
        self.credentials.host = host

    def add_file(
        self, file: Union[TextIO, BinaryIO, File], filename: Optional[str] = None
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
            Mention(mention_data=UserMention(user_huid=user_huid, name=name))
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
            )
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
            )
        )

    def add_recipient(self, recipient: UUID) -> None:
        """Add new user that will receive message.

        Arguments:
            recipient: recipient for message.
        """
        if self.payload.options.recipients == Recipients.all:
            self.payload.options.recipients = []

        cast(List[UUID], self.payload.options.recipients).append(recipient)

    def add_recipients(self, recipients: List[UUID]) -> None:
        """Add list of recipients that should receive message.

        Arguments:
            recipients: recipients for message.
        """
        if self.payload.options.recipients == Recipients.all:
            self.payload.options.recipients = []

        cast(List[UUID], self.payload.options.recipients).extend(recipients)

    def add_bubble(
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new bubble button to message markup.

        Arguments:
            command: command that will be triggered on bubble click.
            label: label that will be shown on bubble.
            data: payload that will be attached to bubble.
            new_row: place bubble on new row or on current.
        """
        self.payload.markup.add_bubble(command, label, data, new_row=new_row)

    def add_keyboard_button(
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new keyboard button to message markup.

        Arguments:
            command: command that will be triggered on keyboard click.
            label: label that will be shown on keyboard button.
            data: payload that will be attached to keyboard.
            new_row: place keyboard on new row or on current.
        """
        self.payload.markup.add_keyboard_button(command, label, data, new_row=new_row)

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

    def _built_credentials(
        self,
        bot_id: Optional[UUID] = None,
        host: Optional[str] = None,
        sync_id: Optional[UUID] = None,
        chat_id: Optional[UUID] = None,
        chat_ids: Optional[List[UUID]] = None,
        credentials: Optional[SendingCredentials] = None,
    ) -> SendingCredentials:
        """Build credentials for message.

        Arguments:
            bot_id: bot id.
            host: host for message.
            sync_id: message event id.
            chat_id: chat id.
            chat_ids: sequence of chat ids.
            credentials: message credentials.

        Returns:
            Credentials for message.
        """
        if bot_id and host:
            assert (
                not credentials
            ), "MessageCredentials can not be passed along with manual values for it"

            return SendingCredentials(
                bot_id=bot_id,
                host=host,
                sync_id=sync_id,
                chat_ids=chat_ids or [],
                chat_id=chat_id,
            )

        assert credentials, "MessageCredentials or manual values should be passed"
        return credentials

    def _built_markup(
        self,
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
        """
        if bubbles is not None or keyboard is not None:
            assert (
                not markup
            ), "Markup can not be passed along with bubbles or keyboard elements"
            return MessageMarkup(bubbles=bubbles or [], keyboard=keyboard or [])

        return markup or MessageMarkup()

    def _build_options(
        self,
        recipients: Optional[AvailableRecipients] = None,
        mentions: Optional[List[Mention]] = None,
        notification_options: Optional[NotificationOptions] = None,
        options: Optional[MessageOptions] = None,
    ) -> MessageOptions:
        """Built options for message.

        Arguments:
            recipients: recipients for message.
            mentions: mentions that will be attached to message.
            notification_options: configuration for notifications for message.
            options: message options.

        Returns:
            Options for message.
        """
        if mentions or recipients or notification_options:
            assert (
                not options
            ), "MessageOptions can not be passed along with manual values for it"
            return MessageOptions(
                recipients=recipients or Recipients.all,
                mentions=mentions or [],
                notifications=notification_options or NotificationOptions(),
            )

        return options or MessageOptions()
