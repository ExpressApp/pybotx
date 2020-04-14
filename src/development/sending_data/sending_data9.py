from uuid import UUID

from botx import Bot, Message, SendingMessage

bot = Bot()
CHAT_FOR_MENTION = UUID("369b49fd-b5eb-4d5b-8e4d-83b020ff2b14")
USER_FOR_MENTION = UUID("cbf4b952-77d5-4484-aea0-f05fb622e089")


@bot.handler
async def my_handler_with_user_mention(message: Message) -> None:
    reply = SendingMessage.from_message(
        text="Hi! There is a notification with mention for you", message=message
    )
    reply.mention_user(message.user_huid)

    await bot.send(reply)


@bot.handler
async def my_handler_with_chat_mention(message: Message) -> None:
    reply = SendingMessage.from_message(text="Check this chat", message=message)
    reply.mention_chat(CHAT_FOR_MENTION, name="Interesting chat")
    await bot.send(reply)


@bot.handler
async def my_handler_with_contact_mention(message: Message) -> None:
    reply = SendingMessage.from_message(
        text="You should request access!", message=message
    )
    reply.mention_chat(USER_FOR_MENTION, name="Administrator")
    await bot.send(reply)
