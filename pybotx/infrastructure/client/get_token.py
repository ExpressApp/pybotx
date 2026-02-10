from uuid import UUID

from pybotx.domain.ports.bot_accounts_storage import BotAccountsStoragePort
from pybotx.domain.ports.http_client import HttpClientPort
from pybotx.infrastructure.client.bots_api.get_token import (
    BotXAPIGetTokenRequestPayload,
    GetTokenMethod,
)


async def get_token(
    bot_id: UUID,
    http_client: HttpClientPort,
    bot_accounts_storage: BotAccountsStoragePort,
) -> str:
    """Request token for bot.

    Moved to separate file because used in `AuthorizedBotXMethod` and `Bot.get_token`.
    """

    method = GetTokenMethod(
        bot_id,
        http_client,
        bot_accounts_storage,
    )

    signature = bot_accounts_storage.build_signature(bot_id)
    payload = BotXAPIGetTokenRequestPayload.from_domain(signature)

    botx_api_token = await method.execute(payload)

    return botx_api_token.to_domain()
