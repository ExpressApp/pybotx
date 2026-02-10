from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Literal, TypeVar
from collections.abc import Awaitable, Callable

from pybotx.domain.models.commands import BotCommand
from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.models.status import StatusRecipient
from pybotx.domain.models.sync_smartapp_event import SyncSmartAppEventResponse
from pybotx.domain.models.system_events.added_to_chat import AddedToChatEvent
from pybotx.domain.models.system_events.chat_created import ChatCreatedEvent
from pybotx.domain.models.system_events.chat_deleted_by_user import ChatDeletedByUserEvent
from pybotx.domain.models.system_events.conference_changed import ConferenceChangedEvent
from pybotx.domain.models.system_events.conference_created import ConferenceCreatedEvent
from pybotx.domain.models.system_events.conference_deleted import ConferenceDeletedEvent
from pybotx.domain.models.system_events.cts_login import CTSLoginEvent
from pybotx.domain.models.system_events.cts_logout import CTSLogoutEvent
from pybotx.domain.models.system_events.deleted_from_chat import DeletedFromChatEvent
from pybotx.domain.models.system_events.event_delete import EventDeleted
from pybotx.domain.models.system_events.event_edit import EventEdit
from pybotx.domain.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)
from pybotx.domain.models.system_events.left_from_chat import LeftFromChatEvent
from pybotx.domain.models.system_events.smartapp_event import SmartAppEvent
from pybotx.domain.models.system_events.user_joined_to_chat import JoinToChatEvent

if TYPE_CHECKING:  # To avoid circular import
    from pybotx.application.bot import Bot

TBotCommand = TypeVar("TBotCommand", bound=BotCommand)
HandlerFunc = Callable[[TBotCommand, "Bot"], Awaitable[None]]

SyncSmartAppEventHandlerFunc = Callable[
    [SmartAppEvent, "Bot"],
    Awaitable[SyncSmartAppEventResponse],
]

IncomingMessageHandlerFunc = HandlerFunc[IncomingMessage]
SystemEventHandlerFunc = (
    HandlerFunc[AddedToChatEvent]
    | HandlerFunc[ChatCreatedEvent]
    | HandlerFunc[ChatDeletedByUserEvent]
    | HandlerFunc[DeletedFromChatEvent]
    | HandlerFunc[LeftFromChatEvent]
    | HandlerFunc[CTSLoginEvent]
    | HandlerFunc[CTSLogoutEvent]
    | HandlerFunc[InternalBotNotificationEvent]
    | HandlerFunc[SmartAppEvent]
    | HandlerFunc[EventDeleted]
    | HandlerFunc[EventEdit]
    | HandlerFunc[JoinToChatEvent]
    | HandlerFunc[ConferenceChangedEvent]
    | HandlerFunc[ConferenceCreatedEvent]
    | HandlerFunc[ConferenceDeletedEvent]
)

VisibleFunc = Callable[[StatusRecipient, "Bot"], Awaitable[bool]]

Middleware = Callable[
    [IncomingMessage, "Bot", IncomingMessageHandlerFunc],
    Awaitable[None],
]


@dataclass(slots=True)
class BaseIncomingMessageHandler:
    handler_func: IncomingMessageHandlerFunc
    middlewares: list[Middleware]

    async def __call__(self, message: IncomingMessage, bot: "Bot") -> None:
        handler_func = self.handler_func

        for middleware in self.middlewares[::-1]:
            handler_func = partial(
                middleware,
                call_next=handler_func,  # type: ignore[call-arg]
            )

        await handler_func(message, bot)

    def add_middlewares(self, middlewares: list[Middleware]) -> None:
        self.middlewares = middlewares + self.middlewares


@dataclass(slots=True)
class HiddenCommandHandler(BaseIncomingMessageHandler):
    # Default should be here, see: https://github.com/python/mypy/issues/6113
    visible: Literal[False] = False


@dataclass(slots=True)
class VisibleCommandHandler(BaseIncomingMessageHandler):
    description: str
    visible: Literal[True] | VisibleFunc = True


@dataclass(slots=True)
class DefaultMessageHandler(BaseIncomingMessageHandler):
    """Just for separate type."""


CommandHandler = HiddenCommandHandler | VisibleCommandHandler
