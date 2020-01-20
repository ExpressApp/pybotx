from botx import Bot, Message, MessageMarkup

bot = Bot()


@bot.handler
async def my_handler_with_passing_predefined_markup(message: Message) -> None:
    markup = MessageMarkup()
    markup.add_bubble(command="", label="bubble 1")
    markup.add_bubble(command="", label="bubble 2", new_row=False)
    markup.add_bubble(command="", label="bubble 3")

    await bot.answer_message("Bubbles!!", message, markup=markup)
