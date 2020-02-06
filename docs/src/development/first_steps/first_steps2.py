from botx import Bot, ExpressServer, IncomingMessage, Message, Status
from starlette.status import HTTP_202_ACCEPTED

from fastapi import FastAPI

users_data = {}
bot = Bot(known_hosts=[ExpressServer(host="cts.example.com", secret_key="secret")])


@bot.default(include_in_status=False)
async def echo_handler(message: Message) -> None:
    await bot.answer_message(message.body, message)


@bot.handler
async def fill_info(message: Message) -> None:
    if message.user_huid not in users_data:
        text = (
            "Hi! I'm a bot that will ask some questions about you.\n"
            "First of all: what is your name?"
        )
    else:
        text = (
            "You've already filled out information about yourself.\n"
            "You can view it by typing `/my-info` command.\n"
            "You can also view the processed information by typing `/info` command."
        )

    await bot.answer_message(text, message)


app = FastAPI()
app.add_event_handler("shutdown", bot.shutdown)


@app.get("/status", response_model=Status)
async def bot_status() -> Status:
    return await bot.status()


@app.post("/command", status_code=HTTP_202_ACCEPTED)
async def bot_command(message: IncomingMessage) -> None:
    await bot.execute_command(message.dict())
