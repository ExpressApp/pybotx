from http import HTTPStatus
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from botx import (
    Bot,
    BotAccountWithSecret,
    ChatCreatedEvent,
    HandlerCollector,
    IncomingMessage,
    build_command_accepted_response,
)

collector = HandlerCollector()


@collector.chat_created
async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    await bot.answer_message("Hello!")


@collector.command("/echo", description="Send back the received message body")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(message.body)


@collector.default_message_handler
async def default_message_handler(event: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Sorry, command not found.")


bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(  # noqa: S106
            # Replace fake account credentials with yours
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            host="cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
)

app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(await request.json())
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(dict(request.query_params))
    return JSONResponse(status)


@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    bot.set_raw_botx_method_result(await request.json())
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )
