from typing import Any, Optional

from botx.clients.methods.base import BotXMethod
from botx.models import sending

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore


class BotXMethodCallProtocol(Protocol):
    async def call_method(
        self,
        method: BotXMethod[Any],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[sending.SendingCredentials] = None,
    ) -> Any:
        """TODO: write normal doc."""
