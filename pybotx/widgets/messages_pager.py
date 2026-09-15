from collections.abc import Sequence
from typing import cast

from pybotx.bot.bot import Bot
from pybotx.models.message.incoming_message import IncomingMessage
from pybotx.models.message.outgoing_message import OutgoingMessage

from .base import WidgetResultMode
from .markup import MessageMarkup
from .pagination import PaginationWidget


class MessagesPagerWidget(PaginationWidget):
    def __init__(
        self,
        elements: Sequence[str],
        page_size: int,
        item_template: str = "Element: {element}",
        delay_between_messages: float = 0.5,
        *,
        message: IncomingMessage,
        bot: Bot,
        command: str,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> None:
        widget_content = [
            item_template.format(
                element=element,
                index=index + 1,
                total=len(elements),
            )
            for index, element in enumerate(elements)
        ]
        super().__init__(
            widget_content=cast(list[OutgoingMessage | str], widget_content),
            paginate_by=page_size,
            delay_between_messages=delay_between_messages,
            message=message,
            bot=bot,
            command=command,
            additional_markup=additional_markup,
            result_mode=result_mode,
        )
