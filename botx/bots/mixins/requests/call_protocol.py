from typing import Any, Optional, Protocol

from botx.clients.methods.base import BotXMethod
from botx.models import sending


class BotXMethodCallProtocol(Protocol):
    async def call_method(
        self,
        method: BotXMethod[Any],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[sending.SendingCredentials] = None,
    ) -> Any:
        ...
