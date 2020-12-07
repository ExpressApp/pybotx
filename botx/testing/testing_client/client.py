"""Definition of client for testing."""
from typing import Tuple, Union

from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.methods.v3.events.reply_event import ReplyEvent
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.testing.testing_client.base import BaseTestClient
from botx.testing.typing import APIMessage, APIRequest


class TestClient(BaseTestClient):
    """Test client for testing bots."""

    # https://docs.pytest.org/en/latest/changelog.html#changes
    # Allow to skip test classes from being collected
    __test__: bool = False

    @property
    def requests(self) -> Tuple[APIRequest, ...]:
        """Return all requests that were sent by bot.

        Returns:
            Sequence of requests that were sent from bot.
        """
        return tuple(request.copy(deep=True) for request in self._requests)

    @property
    def messages(self) -> Tuple[APIMessage, ...]:
        """Return all entities that were sent by bot.

        Returns:
            Sequence of messages that were sent from bot.
        """
        return tuple(message.copy(deep=True) for message in self._messages)

    @property
    def command_results(self) -> Tuple[CommandResult, ...]:
        """Return all command results that were sent by bot.

        Returns:
            Sequence of command results that were sent from bot.
        """
        return tuple(
            message for message in self.messages if isinstance(message, CommandResult)
        )

    @property
    def notifications(self) -> Tuple[Union[Notification, NotificationDirect], ...]:
        """Return all notifications that were sent by bot.

        Returns:
            Sequence of notifications that were sent by bot.
        """
        return tuple(
            message
            for message in self.messages
            if isinstance(message, (Notification, NotificationDirect))
        )

    @property
    def message_updates(self) -> Tuple[EditEvent, ...]:
        """Return all updates that were sent by bot.

        Returns:
            Sequence of updates that were sent by bot.
        """
        return tuple(
            message for message in self.messages if isinstance(message, EditEvent)
        )

    @property
    def replies(self) -> Tuple[ReplyEvent, ...]:
        """Return all replies that were sent by bot.

        Returns:
            Sequence of replies that were sent by bot.
        """
        return tuple(
            message for message in self.messages if isinstance(message, ReplyEvent)
        )
