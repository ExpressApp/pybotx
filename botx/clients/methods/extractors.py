from uuid import UUID

from botx.clients.methods.base import BotXMethod
from botx.clients.types.response_results import ChatCreatedResult, PushResult


def extract_generated_sync_id(_method: BotXMethod, push: PushResult) -> UUID:
    return push.sync_id


def extract_generated_chat_id(_method: BotXMethod, response: ChatCreatedResult) -> UUID:
    return response.chat_id
