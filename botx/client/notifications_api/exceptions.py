from botx.client.exceptions.callbacks import BotXMethodFailedCallbackReceivedError


class ChatNotFoundCallbackError(BotXMethodFailedCallbackReceivedError):
    """Invalid chat id."""


class BotIsNotChatMemberCallbackError(BotXMethodFailedCallbackReceivedError):
    """Bot is not in the list of chat members."""


class FinalRecipientsListEmptyCallbackError(BotXMethodFailedCallbackReceivedError):
    """Resulting event recipients list is empty."""
