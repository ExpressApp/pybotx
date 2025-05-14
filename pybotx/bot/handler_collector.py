import asyncio
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Type,
    Union,
    overload,
)
from weakref import WeakSet

from pybotx.bot.contextvars import bot_id_var, bot_var, chat_id_var
from pybotx.bot.handler import (
    CommandHandler,
    DefaultMessageHandler,
    HandlerFunc,
    HiddenCommandHandler,
    IncomingMessageHandlerFunc,
    Middleware,
    SyncSmartAppEventHandlerFunc,
    SystemEventHandlerFunc,
    VisibleCommandHandler,
    VisibleFunc,
)
from pybotx.bot.middlewares.exception_middleware import (
    ExceptionHandlersDict,
    ExceptionMiddleware,
)
from pybotx.client.smartapps_api.exceptions import SyncSmartAppEventHandlerNotFoundError
from pybotx.converters import optional_sequence_to_list
from pybotx.logger import logger
from pybotx.models.commands import BotCommand, SystemEvent
from pybotx.models.message.incoming_message import IncomingMessage
from pybotx.models.status import BotMenu, StatusRecipient
from pybotx.models.sync_smartapp_event import BotAPISyncSmartAppEventResponse
from pybotx.models.system_events.added_to_chat import AddedToChatEvent
from pybotx.models.system_events.chat_created import ChatCreatedEvent
from pybotx.models.system_events.chat_deleted_by_user import ChatDeletedByUserEvent
from pybotx.models.system_events.cts_login import CTSLoginEvent
from pybotx.models.system_events.cts_logout import CTSLogoutEvent
from pybotx.models.system_events.deleted_from_chat import DeletedFromChatEvent
from pybotx.models.system_events.event_edit import EventEdit
from pybotx.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)
from pybotx.models.system_events.left_from_chat import LeftFromChatEvent
from pybotx.models.system_events.smartapp_event import SmartAppEvent

if TYPE_CHECKING:  # To avoid circular import
    from pybotx.bot.bot import Bot


class HandlerCollector:
    VALID_COMMAND_NAME_RE = re.compile(r"^\/[^\s\/]+$", flags=re.UNICODE)

    def __init__(self, middlewares: Optional[Sequence[Middleware]] = None) -> None:
        self._user_commands_handlers: Dict[str, CommandHandler] = {}
        self._default_message_handler: Optional[DefaultMessageHandler] = None
        self._system_events_handlers: Dict[
            Type[BotCommand],
            SystemEventHandlerFunc,
        ] = {}
        self._sync_smartapp_event_handler: Dict[
            Type[SmartAppEvent],
            SyncSmartAppEventHandlerFunc,
        ] = {}
        self._middlewares = optional_sequence_to_list(middlewares)
        self._tasks: "WeakSet[asyncio.Task[None]]" = WeakSet()

    def include(self, *others: "HandlerCollector") -> None:
        """Include other `HandlerCollector`."""
        for collector in others:
            self._include_collector(collector)

    def async_handle_bot_command(
        self,
        bot: "Bot",
        bot_command: BotCommand,
    ) -> "asyncio.Task[None]":
        task = asyncio.create_task(
            self.handle_bot_command(bot_command, bot),
        )
        self._tasks.add(task)

        return task

    async def handle_incoming_message_by_command(
        self,
        message: IncomingMessage,
        bot: "Bot",
        command: str,
    ) -> None:
        message_handler = self._get_command_handler(command)
        if message_handler:
            self._fill_contextvars(message, bot)
            await message_handler(message, bot)

    async def handle_bot_command(self, bot_command: BotCommand, bot: "Bot") -> None:
        if isinstance(bot_command, IncomingMessage):
            message_handler = self._get_incoming_message_handler(bot_command)
            if message_handler:
                self._fill_contextvars(bot_command, bot)
                await message_handler(bot_command, bot)

        elif isinstance(
            bot_command,
            SystemEvent.__args__,  # type: ignore [attr-defined]  # noqa: WPS609
        ):
            event_handler = self._get_system_event_handler_or_none(bot_command)
            if event_handler:
                self._fill_contextvars(bot_command, bot)
                await event_handler(bot_command, bot)

        else:
            raise NotImplementedError(f"Unsupported event type: `{bot_command}`")

    async def handle_sync_smartapp_event(
        self,
        bot: "Bot",
        smartapp_event: SmartAppEvent,
    ) -> BotAPISyncSmartAppEventResponse:
        if not isinstance(smartapp_event, SmartAppEvent):
            raise NotImplementedError(
                f"Unsupported event type for sync smartapp event: `{smartapp_event}`",
            )

        event_handler = self._get_sync_smartapp_event_handler_or_none(smartapp_event)

        if not event_handler:
            raise SyncSmartAppEventHandlerNotFoundError(
                "Handler for sync smartapp event not found",
            )

        self._fill_contextvars(smartapp_event, bot)
        return await event_handler(smartapp_event, bot)

    async def get_bot_menu(
        self,
        status_recipient: StatusRecipient,
        bot: "Bot",
    ) -> BotMenu:
        bot_menu = {}

        for command_name, handler in self._user_commands_handlers.items():
            if handler.visible is True or (
                callable(handler.visible)
                and await handler.visible(status_recipient, bot)
            ):
                bot_menu[command_name] = handler.description

        return BotMenu(bot_menu)

    def command(
        self,
        command_name: str,
        visible: Union[bool, VisibleFunc] = True,
        description: Optional[str] = None,
        middlewares: Optional[Sequence[Middleware]] = None,
    ) -> Callable[[IncomingMessageHandlerFunc], IncomingMessageHandlerFunc]:
        """Decorate command handler."""
        if not self.VALID_COMMAND_NAME_RE.match(command_name):
            raise ValueError("Command should start with '/' and doesn't include spaces")

        def decorator(
            handler_func: IncomingMessageHandlerFunc,
        ) -> IncomingMessageHandlerFunc:
            if command_name in self._user_commands_handlers:
                raise ValueError(
                    f"Handler for command `{command_name}` already registered",
                )

            self._user_commands_handlers[command_name] = self._build_command_handler(
                handler_func,
                visible,
                description,
                self._middlewares + optional_sequence_to_list(middlewares),
            )

            return handler_func

        return decorator

    @overload
    def default_message_handler(
        self,
        handler_func: IncomingMessageHandlerFunc,
    ) -> IncomingMessageHandlerFunc:
        ...  # noqa: WPS428

    @overload
    def default_message_handler(
        self,
        *,
        middlewares: Optional[Sequence[Middleware]] = None,
    ) -> Callable[[IncomingMessageHandlerFunc], IncomingMessageHandlerFunc]:
        ...  # noqa: WPS428

    def default_message_handler(  # noqa: WPS320
        self,
        handler_func: Optional[IncomingMessageHandlerFunc] = None,
        *,
        middlewares: Optional[Sequence[Middleware]] = None,
    ) -> Union[
        IncomingMessageHandlerFunc,
        Callable[[IncomingMessageHandlerFunc], IncomingMessageHandlerFunc],
    ]:
        """Decorate fallback messages handler."""
        if self._default_message_handler:
            raise ValueError("Default command handler already registered")

        def decorator(
            handler_func: IncomingMessageHandlerFunc,  # noqa: WPS442
        ) -> IncomingMessageHandlerFunc:
            self._default_message_handler = DefaultMessageHandler(
                handler_func=handler_func,
                middlewares=self._middlewares + optional_sequence_to_list(middlewares),
            )

            return handler_func

        if callable(handler_func) and not middlewares:
            return decorator(handler_func)

        return decorator

    def chat_created(
        self,
        handler_func: HandlerFunc[ChatCreatedEvent],
    ) -> HandlerFunc[ChatCreatedEvent]:
        """Decorate `chat_created` event handler."""
        self._system_event(ChatCreatedEvent, handler_func)
        return handler_func

    def chat_deleted_by_user(
        self,
        handler_func: HandlerFunc[ChatDeletedByUserEvent],
    ) -> HandlerFunc[ChatDeletedByUserEvent]:
        """Decorate `chat_deleted_by_user` event handler."""
        self._system_event(ChatDeletedByUserEvent, handler_func)
        return handler_func

    def added_to_chat(
        self,
        handler_func: HandlerFunc[AddedToChatEvent],
    ) -> HandlerFunc[AddedToChatEvent]:
        """Decorate `added_to_chat` event handler."""
        self._system_event(AddedToChatEvent, handler_func)
        return handler_func

    def deleted_from_chat(
        self,
        handler_func: HandlerFunc[DeletedFromChatEvent],
    ) -> HandlerFunc[DeletedFromChatEvent]:
        """Decorate `deleted_from_chat` event handler."""
        self._system_event(DeletedFromChatEvent, handler_func)
        return handler_func

    def left_from_chat(
        self,
        handler_func: HandlerFunc[LeftFromChatEvent],
    ) -> HandlerFunc[LeftFromChatEvent]:
        """Decorate `left_from_chat` event handler."""
        self._system_event(LeftFromChatEvent, handler_func)
        return handler_func

    def internal_bot_notification(
        self,
        handler_func: HandlerFunc[InternalBotNotificationEvent],
    ) -> HandlerFunc[InternalBotNotificationEvent]:
        """Decorate `internal_bot_notification` event handler."""
        self._system_event(InternalBotNotificationEvent, handler_func)
        return handler_func

    def cts_login(
        self,
        handler_func: HandlerFunc[CTSLoginEvent],
    ) -> HandlerFunc[CTSLoginEvent]:
        """Decorate `cts_login` event handler."""
        self._system_event(CTSLoginEvent, handler_func)
        return handler_func

    def cts_logout(
        self,
        handler_func: HandlerFunc[CTSLogoutEvent],
    ) -> HandlerFunc[CTSLogoutEvent]:
        """Decorate `cts_logout` event handler."""
        self._system_event(CTSLogoutEvent, handler_func)
        return handler_func

    def event_edit(
        self,
        handler_func: HandlerFunc[EventEdit],
    ) -> HandlerFunc[EventEdit]:
        """Decorate `event edit` event handler."""
        self._system_event(EventEdit, handler_func)
        return handler_func

    def smartapp_event(
        self,
        handler_func: HandlerFunc[SmartAppEvent],
    ) -> HandlerFunc[SmartAppEvent]:
        """Decorate `smartapp` event handler."""
        self._system_event(SmartAppEvent, handler_func)
        return handler_func

    def sync_smartapp_event(
        self,
        handler_func: SyncSmartAppEventHandlerFunc,
    ) -> SyncSmartAppEventHandlerFunc:
        """Decorate `smartapp` sync event handler."""
        self._sync_smartapp_event(SmartAppEvent, handler_func)
        return handler_func

    def insert_exception_middleware(
        self,
        exception_handlers: Optional[ExceptionHandlersDict] = None,
    ) -> None:
        exception_middleware = ExceptionMiddleware(exception_handlers or {})
        self._middlewares.insert(0, exception_middleware.dispatch)

    async def wait_active_tasks(self) -> None:
        if self._tasks:
            await asyncio.wait(
                self._tasks,
                return_when=asyncio.ALL_COMPLETED,
            )

    def _include_collector(self, other: "HandlerCollector") -> None:  # noqa: WPS238
        # - Message handlers -
        command_duplicates = set(self._user_commands_handlers) & set(
            other._user_commands_handlers,
        )
        if command_duplicates:
            raise ValueError(
                f"Handlers for {command_duplicates} commands already registered",
            )

        other_handlers = other._user_commands_handlers
        for handler in other_handlers.values():
            handler.add_middlewares(self._middlewares)

        self._user_commands_handlers.update(other_handlers)

        # - Default message handler -
        if self._default_message_handler and other._default_message_handler:
            raise ValueError("Default message handler already registered")

        if not self._default_message_handler and other._default_message_handler:
            other._default_message_handler.add_middlewares(self._middlewares)
            self._default_message_handler = other._default_message_handler

        # - System events -
        events_duplicates = set(self._system_events_handlers) & set(
            other._system_events_handlers,
        )
        if events_duplicates:
            raise ValueError(
                f"Handlers for {events_duplicates} events already registered",
            )

        self._system_events_handlers.update(other._system_events_handlers)

        # - Sync smartapp event handler -
        sync_events_duplicates: Set[Type[SmartAppEvent]] = set(
            self._sync_smartapp_event_handler,
        ) & set(
            other._sync_smartapp_event_handler,
        )
        if sync_events_duplicates:
            raise ValueError(
                "Handler for sync smartapp event already registered",
            )

        self._sync_smartapp_event_handler.update(other._sync_smartapp_event_handler)

    def _get_incoming_message_handler(
        self,
        message: IncomingMessage,
    ) -> Union[CommandHandler, DefaultMessageHandler, None]:
        return self._get_command_handler(message.body)

    def _get_command_handler(
        self,
        command: str,
    ) -> Union[CommandHandler, DefaultMessageHandler, None]:
        handler: Optional[Union[CommandHandler, DefaultMessageHandler]] = None

        command_name = self._get_command_name(command)
        if command_name:
            handler = self._user_commands_handlers.get(command_name)
            if handler:
                logger.info(f"Found handler for command `{command_name}`")
                return handler

        if self._default_message_handler:
            self._log_default_handler_call(command_name)
            return self._default_message_handler

        logger.warning(f"Handler for message text `{command}` not found")
        return None

    def _get_system_event_handler_or_none(
        self,
        event: SystemEvent,
    ) -> Optional[SystemEventHandlerFunc]:
        event_cls = event.__class__

        handler = self._system_events_handlers.get(event_cls)
        self._log_system_event_handler_call(event_cls.__name__, handler)

        return handler

    def _get_sync_smartapp_event_handler_or_none(
        self,
        event: SmartAppEvent,
    ) -> Optional[SyncSmartAppEventHandlerFunc]:
        event_cls = event.__class__

        handler = self._sync_smartapp_event_handler.get(event_cls)
        self._log_system_event_handler_call(event_cls.__name__, handler)

        return handler

    def _get_command_name(self, body: str) -> Optional[str]:
        if not body:
            return None

        command_name = body.split(maxsplit=1)[0]
        if self.VALID_COMMAND_NAME_RE.match(command_name):
            return command_name

        return None

    def _build_command_handler(
        self,
        handler_func: IncomingMessageHandlerFunc,
        visible: Union[bool, VisibleFunc],
        description: Optional[str],
        middlewares: List[Middleware],
    ) -> CommandHandler:
        if visible is True or callable(visible):
            if not description:
                raise ValueError("Description is required for visible command")

            return VisibleCommandHandler(
                handler_func=handler_func,
                visible=visible,
                description=description,
                middlewares=middlewares,
            )

        return HiddenCommandHandler(
            handler_func=handler_func,
            middlewares=middlewares,
        )

    def _system_event(
        self,
        event_cls_name: Type[BotCommand],
        handler_func: SystemEventHandlerFunc,
    ) -> SystemEventHandlerFunc:
        if event_cls_name in self._system_events_handlers:
            raise ValueError(f"Handler for {event_cls_name} already registered")

        self._system_events_handlers[event_cls_name] = handler_func

        return handler_func

    def _sync_smartapp_event(
        self,
        event_cls_name: Type[SmartAppEvent],
        handler_func: SyncSmartAppEventHandlerFunc,
    ) -> SyncSmartAppEventHandlerFunc:
        if event_cls_name in self._sync_smartapp_event_handler:
            raise ValueError("Handler for sync smartapp event already registered")

        self._sync_smartapp_event_handler[event_cls_name] = handler_func

        return handler_func

    def _fill_contextvars(self, bot_command: BotCommand, bot: "Bot") -> None:
        bot_var.set(bot)
        bot_id_var.set(bot_command.bot.id)

        chat = getattr(bot_command, "chat", None)
        if chat:
            chat_id_var.set(chat.id)

    def _log_system_event_handler_call(
        self,
        event_cls_name: str,
        handler: Any,
    ) -> None:
        if handler:
            logger.info(f"Found handler for `{event_cls_name}`")
        else:
            logger.info(f"Handler for `{event_cls_name}` not found")

    def _log_default_handler_call(self, command_name: Optional[str]) -> None:
        if command_name:
            logger.info(
                f"Handler for command `{command_name}` not found, "
                "using default handler",
            )
        else:
            logger.info("No command found, using default handler")
