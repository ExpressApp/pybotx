from botx import Bot, ExpressServer, IncomingMessage, Message, Status

from fastapi import FastAPI
from starlette.status import HTTP_202_ACCEPTED

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


@bot.handler(command="/my-info")
async def get_info_for_user(message: Message) -> None:
    if message.user_huid not in users_data:
        text = (
            "I have no information about you :(\n"
            "Type `/fill-info` so I can collect it, please."
        )
        await bot.answer_message(text, message)
    else:
        text = (
            f"Your name: {users_data[message.user_huid]['name']}\n"
            f"Your age: {users_data[message.user_huid]['age']}\n"
            f"Your gender: {users_data[message.user_huid]['gender']}\n"
            "This is all that I have now."
        )
        await bot.answer_message(text, message)


@bot.handler(commands=["/info", "/information"])
async def get_processed_information(message: Message) -> None:
    users_count = len(users_data)
    average_age = sum(user["age"] for user in users_data) / users_count
    gender_array = [1 if user["gender"] == "male" else 2 for user in users_data]
    text = (
        f"Count of users: {users_count}\n"
        f"Average age: {average_age}\n"
        f"Male users count: {gender_array.count(1)}\n"
        f"Female users count: {gender_array.count(2)}"
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
