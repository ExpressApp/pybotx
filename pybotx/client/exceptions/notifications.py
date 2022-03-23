from pybotx.client.exceptions.base import BaseClientError


class BotIsNotChatMemberError(BaseClientError):
    """Bot is not in the list of chat members."""


class FinalRecipientsListEmptyError(BaseClientError):
    """Resulting event recipients list is empty."""


class StealthModeDisabledError(BaseClientError):
    """Requested stealth mode disabled in specified chat."""
