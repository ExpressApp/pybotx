"""Define Mixin that combines API and sending mixins and will be used in Bot."""
from typing import List
from uuid import UUID

from botx.bots.mixins.requests.mixin import BotXRequestsMixin
from botx.bots.mixins.sending import SendingMixin
from botx.exceptions import TokenError, UnknownBotError
from botx.models.credentials import BotXCredentials


class ClientsMixin(SendingMixin, BotXRequestsMixin):
    """Mixin that defines methods that are used for communicating with BotX API."""

    bot_accounts: List[BotXCredentials]

    def get_account_by_bot_id(self, bot_id: UUID) -> BotXCredentials:
        """Find BotCredentials in bot registered bot.

        Arguments:
            bot_id: UUID of bot for which server should be searched.

        Returns:
            Found instance of registered server.

        Raises:
            UnknownBotError: raised if account was not found.
        """
        for bot in self.bot_accounts:
            if bot.bot_id == bot_id:
                return bot

        raise UnknownBotError(bot_id=bot_id)

    def get_token_for_bot(self, bot_id: UUID) -> str:
        """Search token in bot saved tokens by bot_id.

        Arguments:
            bot_id: UUID of bot for which token should be searched.

        Returns:
            Found bot's token.

        Raises:
            TokenError: raised of there is not token for bot.
        """
        account = self.get_account_by_bot_id(bot_id)
        if account.token is not None:
            return account.token

        raise TokenError(message_template="Token is empty")
