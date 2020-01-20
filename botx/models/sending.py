"""Entities that are used in sending operations."""

from typing import List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator

from botx.models.buttons import BubbleElement, Button, KeyboardElement
from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.enums import Recipients
from botx.models.files import File
from botx.models.mentions import Mention
from botx.models.typing import BubbleMarkup, KeyboardMarkup


class SendingCredentials(BaseModel):
    """Credentials that are required to send command or notification result."""

    sync_id: Optional[UUID] = None
    """message event id."""
    chat_id: Optional[UUID] = None
    """chat id in which bot should send message."""
    chat_ids: List[UUID] = []
    """list of chats that should receive message."""
    bot_id: Optional[UUID] = None
    """bot that handles message."""
    host: Optional[str] = None
    """host on which bot answers."""
    token: Optional[str] = None
    """token that is used for bot authorization on requests to BotX API."""

    @validator("chat_ids", always=True, whole=True)
    def receiver_id_should_be_passed(
        cls, value: List[UUID], values: dict  # noqa: N805
    ) -> List[UUID]:
        """Add `chat_id` in `chat_ids` if was passed.

        Arguments:
            value: value that should be checked.
            values: all other values checked before.
        """
        if values["chat_id"]:
            value.append(values["chat_id"])
        elif not (value or values["sync_id"]):
            raise ValueError(
                "sync_id, chat_id or chat_ids should be passed to initialization"
            )

        return value


TUIElement = TypeVar("TUIElement", bound=Button)


class MessageMarkup(BaseModel):
    """Collection for bubbles and keyboard with some helper methods."""

    bubbles: List[List[BubbleElement]] = []
    """bubbles that will be attached to message."""
    keyboard: List[List[KeyboardElement]] = []
    """keyboard elements that will be attached to message."""

    def add_bubble(
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new bubble button to markup.

        Arguments:
            command: command that will be triggered on bubble click.
            label: label that will be shown on bubble.
            data: payload that will be attached to bubble.
            new_row: place bubble on new row or on current.
        """
        self._add_ui_element(
            ui_cls=BubbleElement,
            ui_array=self.bubbles,
            command=command,
            label=label,
            data=data,
            new_row=new_row,
        )

    def add_bubble_element(
        self, element: BubbleElement, *, new_row: bool = True
    ) -> None:
        """Add new button to markup from existing element.

        Arguments:
            element: existed bubble element.
            new_row: place bubble on new row or on current.
        """
        self._add_ui_element(
            ui_cls=BubbleElement,
            ui_array=self.bubbles,
            command=element.command,
            label=element.label,
            data=element.data,
            new_row=new_row,
        )

    def add_keyboard_button(
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new keyboard button to markup.

        Arguments:
            command: command that will be triggered on keyboard click.
            label: label that will be shown on keyboard button.
            data: payload that will be attached to keyboard.
            new_row: place keyboard on new row or on current.
        """
        self._add_ui_element(
            ui_cls=KeyboardElement,
            ui_array=self.keyboard,
            command=command,
            label=label,
            data=data,
            new_row=new_row,
        )

    def add_keyboard_button_element(
        self, element: KeyboardElement, *, new_row: bool = True
    ) -> None:
        """Add new keyboard button to markup from existing element.

        Arguments:
            element: existed keyboard button element.
            new_row: place keyboard button on new row or on current.
        """
        self._add_ui_element(
            ui_cls=KeyboardElement,
            ui_array=self.keyboard,
            command=element.command,
            label=element.label,
            data=element.data,
            new_row=new_row,
        )

    def _add_ui_element(  # noqa: WPS211
        self,
        ui_cls: Type[TUIElement],
        ui_array: List[List[TUIElement]],
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,
        new_row: bool = True,
    ) -> None:
        """Add new button to bubble or keyboard arrays.

        Arguments:
            ui_cls: UIElement instance that should be added to array.
            ui_array: storage for ui elements.
            command: command that will be triggered on ui element click.
            label: label that will be shown on ui element.
            data: payload that will be attached to ui element.
            new_row: place ui element on new row or on current.
        """
        element = ui_cls(command=command, label=label, data=data or {})

        if new_row:
            ui_array.append([element])
            return

        if not ui_array:
            ui_array.append([])

        ui_array[-1].append(element)


class NotificationOptions(BaseModel):
    """Configurations for message notifications."""

    send: bool = True
    """show notification about message."""
    force_dnd: bool = False
    """break mute on bot messages."""


class MessageOptions(BaseModel):
    """Message options configuration."""

    recipients: Union[List[UUID], Recipients] = Recipients.all
    """users that should receive message."""
    mentions: List[Mention] = []
    """attached to message mentions."""
    notifications: NotificationOptions = NotificationOptions()
    """notification configuration."""


class MessagePayload(BaseModel):
    """Message payload configuration."""

    text: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)
    """message text."""
    file: Optional[File] = None
    """attached to message file."""
    markup: MessageMarkup = MessageMarkup()
    """message markup."""
    options: MessageOptions = MessageOptions()
    """message configuration."""


class UpdatePayload(BaseModel):
    """Payload for message edition."""

    text: Optional[str] = Field(None, max_length=MAXIMUM_TEXT_LENGTH)
    """new message text."""
    keyboard: Optional[KeyboardMarkup] = None
    """new message bubbles."""
    bubbles: Optional[BubbleMarkup] = None
    """new message keyboard."""
    mentions: Optional[List[Mention]] = None
    """new message mentions."""
    opts: Optional[NotificationOptions] = None
    """new message options."""

    @property
    def markup(self) -> MessageMarkup:
        """Markup for edited message."""
        return MessageMarkup(bubbles=self.bubbles or [], keyboard=self.keyboard or [])

    def set_markup(self, markup: MessageMarkup) -> None:
        """Markup for edited message.

        Arguments:
            markup: markup that should be applied to payload.
        """
        self.bubbles = markup.bubbles
        self.keyboard = markup.keyboard
