from botx import Bot, Message, SendingMessage

bot = Bot()


@bot.handler
async def my_handler_with_markup_in_sending_message(message: Message) -> None:
    reply = SendingMessage.from_message(text="More buttons!!!", message=message)
    reply.add_bubble(command="", label="bubble 1")
    reply.add_keyboard_button(command="", label="keyboard button 1", new_row=False)
    reply.add_keyboard_button(command="", label="keyboard button 2")

    await bot.send(reply)
