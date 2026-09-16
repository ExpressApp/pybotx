from pybotx.bot.bot import Bot, MissingOptionalAttachment
from pybotx.missing import Undefined
from pybotx.models.message.incoming_message import IncomingMessage

from .base import PYBOTX_WIDGET_FLAG, build_outgoing_message_from_incoming
from .markup import MessageMarkup


async def send_or_update_message(
    message: IncomingMessage,
    bot: Bot,
    body: str,
    markup: MessageMarkup | None = None,
    msg_file: MissingOptionalAttachment = Undefined,
) -> None:
    markup = markup or MessageMarkup()

    if message.metadata.get(PYBOTX_WIDGET_FLAG) and message.source_sync_id is not None:
        await bot.edit_message(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
            body=body,
            metadata=dict(message.metadata),
            bubbles=markup.bubbles,
            keyboard=markup.keyboard,
            file=msg_file,
        )
        return

    out_message = build_outgoing_message_from_incoming(
        message=message,
        body=body,
        bubbles=markup.bubbles,
        keyboard=markup.keyboard,
        file=msg_file if msg_file is not None else Undefined,
    )
    await bot.send(message=out_message)
