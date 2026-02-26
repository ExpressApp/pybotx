from collections.abc import Iterator, Sequence
from itertools import cycle, islice
from typing import Any

from pybotx.bot.bot import Bot
from pybotx.models.message.incoming_message import IncomingMessage

from . import strings
from .base import Widget
from .markup import MessageMarkup
from .service import send_or_update_message

LEFT_PRESSED = "CAROUSEL_LEFT_BUTTON_PRESSED"
RIGHT_PRESSED = "CAROUSEL_RIGHT_BUTTON_PRESSED"

START_FROM_KEY = "carousel_start_from"
SELECTED_VALUE_KEY = "carousel_selected_val"
SELECTED_VALUE_LABEL_KEY = "carousel_selected_value_label"
MESSAGE_LABEL_KEY = "carousel_message_label"


def _to_int(value: object, default: int) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return default


class CarouselWidget(Widget):
    LEFT_ARROW = strings.LEFT_ARROW
    RIGHT_ARROW = strings.RIGHT_ARROW
    LEFT_LABEL_WITH_NUMBERS = f"{LEFT_ARROW} ({{}}-{{}})"
    RIGHT_LABEL_WITH_NUMBERS = f"{RIGHT_ARROW} ({{}}-{{}})"
    SELECTED_VALUE_LABEL = strings.SELECTED_VALUE_LABEL

    def __init__(
        self,
        widget_content: Sequence[Any],
        label: str,
        start_from: int = 0,
        displayed_content_count: int = 3,
        control_labels: tuple[str, str] | None = None,
        inline: bool = True,
        loop: bool = True,
        show_numbers: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.widget_content = widget_content
        self.widget_message.body = label
        self.displayed_content_count = displayed_content_count
        self.inline = inline
        self.loop = loop
        self.show_numbers = show_numbers

        if control_labels is not None:
            self._control_labels = control_labels
        elif show_numbers:
            self._control_labels = (
                self.LEFT_LABEL_WITH_NUMBERS,
                self.RIGHT_LABEL_WITH_NUMBERS,
            )
        else:
            self._control_labels = (self.LEFT_ARROW, self.RIGHT_ARROW)

        self._start_from = _to_int(self.message.data.get(START_FROM_KEY), start_from)
        self.selected_val = self.message.data.get(SELECTED_VALUE_KEY, "")
        self.content_len = len(self.widget_content)

        self._validate_params(start_from)

        if self.selected_val == LEFT_PRESSED:
            self._start_from -= displayed_content_count
        elif self.selected_val == RIGHT_PRESSED:
            self._start_from += displayed_content_count

    @classmethod
    async def get_value(
        cls,
        message: IncomingMessage,
        bot: Bot,
        *,
        send_feedback: bool = True,
    ) -> str | None:
        selected_val = message.data[SELECTED_VALUE_KEY]
        if not selected_val or selected_val in {LEFT_PRESSED, RIGHT_PRESSED}:
            return None

        label = str(message.data.get(MESSAGE_LABEL_KEY, ""))
        selected_value_label = str(
            message.data.get(SELECTED_VALUE_LABEL_KEY, cls.SELECTED_VALUE_LABEL)
        )
        msg_text = selected_value_label.format(
            label=label,
            selected_val=selected_val,
        )
        if send_feedback:
            await send_or_update_message(message, bot, msg_text, MessageMarkup())
        _clear_carousel_data(message)

        return str(selected_val)

    @property
    def start_from(self) -> int:
        if self.content_len == 0:
            return 0

        if self._start_from < 0 or self._start_from > self.content_len:
            return abs(self.content_len - abs(self._start_from))

        return self._start_from

    @property
    def end(self) -> int:
        return self.start_from + self.displayed_content_count

    @property
    def left_btn_label(self) -> str:
        left_label = self._control_labels[0]
        if self.show_numbers:
            left_bound = self.start_from - self.displayed_content_count + 1
            left_label = left_label.format(left_bound, self.start_from)
        return left_label

    @property
    def right_btn_label(self) -> str:
        right_label = self._control_labels[1]
        if self.show_numbers:
            right_bound = self.end + self.displayed_content_count
            if self.content_len < right_bound:
                right_bound = self.content_len
            right_label = right_label.format(self.end + 1, right_bound)
        return right_label

    @property
    def displayed_content(self) -> Iterator[Any]:
        if self.loop and self.widget_content:
            return islice(cycle(self.widget_content), self.start_from, self.end)
        return islice(self.widget_content, self.start_from, self.end)

    def add_markup(self) -> None:
        if self.inline:
            self.add_inline_markup()
        else:
            self.add_newline_markup()

        self.add_additional_markup()

    def add_inline_markup(self) -> None:
        show_left_arrow, show_right_arrow = self.get_left_and_right_button_visibility()

        if show_left_arrow:
            self.widget_bubbles.add_button(
                command=self.command,
                label=self.left_btn_label,
                data=self._control_data(LEFT_PRESSED),
            )

        for idx, content_item in enumerate(self.displayed_content):
            self.widget_bubbles.add_button(
                command=self.command,
                label=str(content_item),
                data=self._item_data(content_item),
                new_row=idx == 0 and not show_left_arrow,
            )

        if show_right_arrow:
            self.widget_bubbles.add_button(
                command=self.command,
                label=self.right_btn_label,
                data=self._control_data(RIGHT_PRESSED),
                new_row=False,
            )

    def add_newline_markup(self) -> None:
        show_left_arrow, show_right_arrow = self.get_left_and_right_button_visibility()

        for content_item in self.displayed_content:
            if isinstance(content_item, (list, tuple, set)):
                for idx, row_item in enumerate(content_item):
                    self.widget_bubbles.add_button(
                        command=self.command,
                        label=str(row_item),
                        data=self._item_data(row_item),
                        new_row=idx == 0,
                    )
                continue

            self.widget_bubbles.add_button(
                command=self.command,
                label=str(content_item),
                data=self._item_data(content_item),
            )

        if show_left_arrow:
            self.widget_bubbles.add_button(
                command=self.command,
                label=self.left_btn_label,
                data=self._control_data(LEFT_PRESSED),
            )

        if show_right_arrow:
            self.widget_bubbles.add_button(
                command=self.command,
                label=self.right_btn_label,
                data=self._control_data(RIGHT_PRESSED),
                new_row=not show_left_arrow,
            )

    def get_left_and_right_button_visibility(self) -> tuple[bool, bool]:
        if len(self.widget_content) <= self.displayed_content_count:
            return False, False

        if self.loop:
            return True, True

        return self.start_from > 0, self.end < self.content_len

    def _item_data(self, selected_value: Any) -> dict[str, Any]:
        return {
            START_FROM_KEY: self.start_from,
            SELECTED_VALUE_KEY: selected_value,
            SELECTED_VALUE_LABEL_KEY: self.SELECTED_VALUE_LABEL,
            MESSAGE_LABEL_KEY: self.widget_message.body,
        }

    def _control_data(self, selected_value: str) -> dict[str, Any]:
        return {
            START_FROM_KEY: self.start_from,
            SELECTED_VALUE_KEY: selected_value,
            SELECTED_VALUE_LABEL_KEY: self.SELECTED_VALUE_LABEL,
            MESSAGE_LABEL_KEY: self.widget_message.body,
        }

    def _validate_params(self, start_from: int) -> None:
        if "{selected_val}" not in self.SELECTED_VALUE_LABEL:
            raise ValueError("'SELECTED_VALUE_LABEL' should contain '{selected_val}'")

        if start_from > len(self.widget_content):
            raise ValueError("'start_from' is greater than 'widget_content'")

        if self.displayed_content_count <= 0:
            raise ValueError("'displayed_content_count' should be greater than 0")

        if self.loop and self.show_numbers:
            raise ValueError("You cannot enable both 'loop' and 'show_numbers'")

        if self.inline and self.show_numbers:
            raise ValueError("You cannot enable both 'inline' and 'show_numbers'")

        if self.show_numbers:
            if self._control_labels[0].count("{}") != 2:
                raise ValueError("Left control label should have exactly two '{}'")
            if self._control_labels[1].count("{}") != 2:
                raise ValueError("Right control label should have exactly two '{}'")


def _clear_carousel_data(message: IncomingMessage) -> None:
    for metadata in (message.data, message.metadata):
        metadata.pop(SELECTED_VALUE_KEY, None)
        metadata.pop(SELECTED_VALUE_LABEL_KEY, None)
        metadata.pop(MESSAGE_LABEL_KEY, None)
        metadata.pop(START_FROM_KEY, None)
