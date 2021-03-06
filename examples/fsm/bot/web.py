from fastapi import FastAPI

from bot.bot import bot
from botx import Status

app = FastAPI()


@app.get("/status", response_model=Status)
async def bot_status() -> Status:
    return await bot.status()


@app.post("/command")
async def bot_command(message: dict) -> None:
    await bot.execute_command(message)
