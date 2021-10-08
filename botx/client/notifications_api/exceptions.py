from botx.client.exceptions.callbacks import BotXMethodFailedCallbackReceivedError


class ChatNotFoundError(BotXMethodFailedCallbackReceivedError):
    """Invalid chat id."""


class BotIsNotChatMemberError(BotXMethodFailedCallbackReceivedError):
    """Bot is not in the list of chat members."""


class FinalRecipientsListEmptyError(BotXMethodFailedCallbackReceivedError):
    """Resulting event recipients list is empty."""
