from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Awaitable, Callable, List, Literal, TypeVar, Union

from pybotx.models.commands import BotCommand
from pybotx.models.message.incoming_message import IncomingMessage
from pybotx.models.status import StatusRecipient
from pybotx.models.sync_smartapp_event import BotAPISyncSmartAppEventResponse
from pybotx.models.system_events.added_to_chat import AddedToChatEvent
from pybotx.models.system_events.chat_created import ChatCreatedEvent
from pybotx.models.system_events.chat_deleted_by_user import ChatDeletedByUserEvent
from pybotx.models.system_events.conference_changed import ConferenceChangedEvent
from pybotx.models.system_events.conference_created import ConferenceCreatedEvent
from pybotx.models.system_events.conference_deleted import ConferenceDeletedEvent
from pybotx.models.system_events.cts_login import CTSLoginEvent
from pybotx.models.system_events.cts_logout import CTSLogoutEvent
from pybotx.models.system_events.deleted_from_chat import DeletedFromChatEvent
from pybotx.models.system_events.event_edit import EventEdit
from pybotx.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)
from pybotx.models.system_events.left_from_chat import LeftFromChatEvent
from pybotx.models.system_events.smartapp_event import SmartAppEvent
from pybotx.models.system_events.user_joined_to_chat import JoinToChatEvent

if TYPE_CHECKING:  # To avoid circular import
    from pybotx.bot.bot import Bot

TBotCommand = TypeVar("TBotCommand", bound=BotCommand)
HandlerFunc = Callable[[TBotCommand, "Bot"], Awaitable[None]]

SyncSmartAppEventHandlerFunc = Callable[
    [SmartAppEvent, "Bot"],
    Awaitable[BotAPISyncSmartAppEventResponse],
]

IncomingMessageHandlerFunc = HandlerFunc[IncomingMessage]
SystemEventHandlerFunc = Union[
    HandlerFunc[AddedToChatEvent],
    HandlerFunc[ChatCreatedEvent],
    HandlerFunc[ChatDeletedByUserEvent],
    HandlerFunc[DeletedFromChatEvent],
    HandlerFunc[LeftFromChatEvent],
    HandlerFunc[CTSLoginEvent],
    HandlerFunc[CTSLogoutEvent],
    HandlerFunc[InternalBotNotificationEvent],
    HandlerFunc[SmartAppEvent],
    HandlerFunc[EventEdit],
    HandlerFunc[JoinToChatEvent],
    HandlerFunc[ConferenceChangedEvent],
    HandlerFunc[ConferenceCreatedEvent],
    HandlerFunc[ConferenceDeletedEvent],
]

VisibleFunc = Callable[[StatusRecipient, "Bot"], Awaitable[bool]]

Middleware = Callable[
    [IncomingMessage, "Bot", IncomingMessageHandlerFunc],
    Awaitable[None],
]


@dataclass
class BaseIncomingMessageHandler:
    handler_func: IncomingMessageHandlerFunc
    middlewares: List[Middleware]

    async def __call__(self, message: IncomingMessage, bot: "Bot") -> None:
        handler_func = self.handler_func

        for middleware in self.middlewares[::-1]:
            handler_func = partial(middleware, call_next=handler_func)

        await handler_func(message, bot)

    def add_middlewares(self, middlewares: List[Middleware]) -> None:
        self.middlewares = middlewares + self.middlewares


@dataclass
class HiddenCommandHandler(BaseIncomingMessageHandler):
    # Default should be here, see: https://github.com/python/mypy/issues/6113
    visible: Literal[False] = False


@dataclass
class VisibleCommandHandler(BaseIncomingMessageHandler):
    description: str
    visible: Union[Literal[True], VisibleFunc] = True


@dataclass
class DefaultMessageHandler(BaseIncomingMessageHandler):
    """Just for separate type."""


CommandHandler = Union[HiddenCommandHandler, VisibleCommandHandler]
