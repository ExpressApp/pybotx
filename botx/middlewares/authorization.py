from botx.models.credentials import ServerCredentials
from botx.models.messages import Message
from botx.typing import AsyncExecutor


async def authorization_middleware(message: Message, call_next: AsyncExecutor) -> None:
    bot = message.bot
    server = bot.get_cts_by_host(message.host)
    if server.server_credentials is None:
        token = await bot.get_token(
            message.host, message.bot_id, server.calculate_signature(message.bot_id)
        )
        server.server_credentials = ServerCredentials(
            bot_id=message.bot_id, token=token
        )
    await call_next(message)
