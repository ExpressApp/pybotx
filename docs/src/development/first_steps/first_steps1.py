from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_202_ACCEPTED, HTTP_503_SERVICE_UNAVAILABLE

from botx import (
    Bot,
    BotDisabledErrorData,
    BotDisabledResponse,
    ExpressServer,
    IncomingMessage,
    Message,
    ServerUnknownError,
    Status,
)

bot = Bot(known_hosts=[ExpressServer(host="cts.example.com", secret_key="secret")])


@bot.default(include_in_status=False)
async def echo_handler(message: Message) -> None:
    await bot.answer_message(message.body, message)


app = FastAPI()
app.add_event_handler("shutdown", bot.shutdown)


@app.get("/status", response_model=Status)
async def bot_status() -> Status:
    return await bot.status()


@app.post("/command", status_code=HTTP_202_ACCEPTED)
async def bot_command(message: IncomingMessage) -> None:
    await bot.execute_command(message.dict())


@app.exception_handler(ServerUnknownError)
async def message_from_unknown_server_hanlder(
    _request: Request, exc: ServerUnknownError
) -> Response:
    return JSONResponse(
        status_code=HTTP_503_SERVICE_UNAVAILABLE,
        content=BotDisabledResponse(
            error_data=BotDisabledErrorData(
                status_message=(
                    f"Sorry, bot can not communicate with user from {exc.host} CTS"
                ),
            ),
        ).dict(),
    )
