from botx import Collector, Message

collector = Collector()


@collector.handler
async def my_handler_for_a_service(message: Message) -> None:
    # do something here
    print(f"Message from {message.group_chat_id} chat")
