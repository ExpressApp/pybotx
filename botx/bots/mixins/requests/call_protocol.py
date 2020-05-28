"""Protocol for using in mixins to make mypy and typing happy."""
from typing import Any, Optional

from botx.clients.methods.base import BotXMethod
from botx.models import sending
from botx.typing import Protocol


class BotXMethodCallProtocol(Protocol):
    """Protocol for using in mixins to make mypy and typing happy."""

    async def call_method(
        self,
        method: BotXMethod[Any],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[sending.SendingCredentials] = None,
    ) -> Any:
        """Send request to BotX API through bot's async client."""
