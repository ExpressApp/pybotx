from loguru import logger
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

CTS_HOST: str = config("CTS_HOST")
BOT_SECRET: Secret = config("BOT_SECRET", cast=Secret)

logger.enable("botx")