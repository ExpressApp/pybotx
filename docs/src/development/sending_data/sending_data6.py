from botx import Bot, BubbleElement, Message, MessageMarkup

bot = Bot()


@bot.handler
async def my_handler_with_direct_bubbles_definition(message: Message) -> None:
    await bot.answer_message(
        "Bubbles!!",
        message,
        markup=MessageMarkup(
            bubbles=[
                [BubbleElement(label="bubble 1", command="")],
                [
                    BubbleElement(label="bubble 2", command=""),
                    BubbleElement(label="bubble 3", command=""),
                ],
            ],
        ),
    )
