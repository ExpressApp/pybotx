"""Protocol for using in mixins to make mypy and typing happy."""
from typing import Any, Optional

from botx.clients.methods.base import BotXMethod
from botx.models.messages.sending.credentials import SendingCredentials

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import (  # type: ignore  # noqa: WPS433, WPS440, F401
        Protocol,
    )


class BotXMethodCallProtocol(Protocol):
    """Protocol for using in mixins to make mypy and typing happy."""

    async def call_method(
        self,
        method: BotXMethod[Any],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[SendingCredentials] = None,
    ) -> Any:
        """Send request to BotX API through bot's async client."""
