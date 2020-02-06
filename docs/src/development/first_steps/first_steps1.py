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
from starlette.status import HTTP_202_ACCEPTED, HTTP_406_NOT_ACCEPTABLE

from fastapi import FastAPI, HTTPException

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
    try:
        await bot.execute_command(message.dict())
    except ServerUnknownError:
        raise HTTPException(
            status_code=HTTP_406_NOT_ACCEPTABLE,
            detail=BotDisabledResponse(
                error_data=BotDisabledErrorData(
                    status_message=(
                        "Sorry, bot can not communicate with user "
                        f"from {message.user.host} CTS"
                    )
                )
            ),
        )
