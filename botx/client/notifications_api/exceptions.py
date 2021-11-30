from botx.client.exceptions.base import BaseClientException


class BotIsNotChatMemberError(BaseClientException):
    """Bot is not in the list of chat members."""


class FinalRecipientsListEmptyError(BaseClientException):
    """Resulting event recipients list is empty."""


class StealthModeDisabledError(BaseClientException):
    """Requested stealth mode disabled in specified chat."""
