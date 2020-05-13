from uuid import UUID

from botx.clients.methods.base import BotXMethod
from botx.clients.types.push_response import PushResult


def extract_generated_sync_id(_method: BotXMethod, push: PushResult) -> UUID:
    return push.sync_id
