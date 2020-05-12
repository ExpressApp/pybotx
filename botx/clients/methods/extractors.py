from uuid import UUID

from botx.clients.methods.base import BotXMethod
from botx.models.responses import PushResult


def extract_generated_sync_id(_method: BotXMethod, push: PushResult) -> UUID:
    return push.sync_id
