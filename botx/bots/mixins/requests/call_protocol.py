"""Protocol for using in mixins to make mypy and typing happy."""
from typing import Any, Optional
from uuid import UUID

from botx.clients.methods.base import BotXMethod
from botx.models.messages.sending.credentials import SendingCredentials

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class BotXMethodCallProtocol(Protocol):
    """Protocol for using in mixins to make mypy and typing happy."""

    async def call_method(  # noqa: WPS211
        self,
        method: BotXMethod[Any],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        bot_id: Optional[UUID] = None,
        credentials: Optional[SendingCredentials] = None,
    ) -> Any:
        """Send request to BotX API through bot's async client."""
