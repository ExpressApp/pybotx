from uuid import UUID

from fastapi import FastAPI
from starlette.status import HTTP_202_ACCEPTED

from botx import Bot, BotXCredentials, IncomingMessage, Message, Status

bot = Bot(bot_accounts=[BotXCredentials(host="cts.example.com", secret_key="secret", bot_id=UUID("bot_id"))])


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