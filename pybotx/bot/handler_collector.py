import asyncio
import re
from contextvars import Context, ContextVar, Token
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    overload,
)
from collections.abc import Callable, Sequence
from weakref import WeakSet

from pybotx.bot.command_processing import (
    BotCommandOverloadAction,
    BotCommandProcessingConfig,
)
from pybotx.bot.contextvars import (
    bot_id_var,
    bot_var,
    chat_id_var,
    request_id_var,
    trace_id_var,
)
from pybotx.bot.exceptions import BotCommandRejectedError
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
from pybotx.bot.ingress_observability import (
    BotIngressMetricsCollector,
    IngressCommandMetadata,
    IngressCommandResult,
    NoopIngressMetricsCollector,
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
from pybotx.models.system_events.conference_changed import ConferenceChangedEvent
from pybotx.models.system_events.conference_created import ConferenceCreatedEvent
from pybotx.models.system_events.conference_deleted import ConferenceDeletedEvent
from pybotx.models.system_events.cts_login import CTSLoginEvent
from pybotx.models.system_events.cts_logout import CTSLogoutEvent
from pybotx.models.system_events.deleted_from_chat import DeletedFromChatEvent
from pybotx.models.system_events.event_delete import EventDeleted
from pybotx.models.system_events.event_edit import EventEdit
from pybotx.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)
from pybotx.models.system_events.left_from_chat import LeftFromChatEvent
from pybotx.models.system_events.smartapp_event import SmartAppEvent
from pybotx.models.system_events.user_joined_to_chat import JoinToChatEvent

if TYPE_CHECKING:  # To avoid circular import
    from pybotx.bot.bot import Bot

MessageHandlerDecorator = Callable[
    [IncomingMessageHandlerFunc],
    IncomingMessageHandlerFunc,
]


@dataclass(slots=True)
class _QueuedBotCommand:
    bot: "Bot"
    bot_command: BotCommand
    completion: asyncio.Future[None]
    request_id: str | None
    trace_id: str | None
    ingress_metadata: IngressCommandMetadata

    async def execute(self, collector: "HandlerCollector") -> None:
        await collector.handle_bot_command(self.bot_command, self.bot)


class HandlerCollector:
    VALID_COMMAND_NAME_RE = re.compile(r"^\/[^\s\/]+$", flags=re.UNICODE)
    _STOP_QUEUE_ITEM: "_QueuedBotCommand | None" = None

    def __init__(
        self,
        middlewares: Sequence[Middleware] | None = None,
        command_processing_config: BotCommandProcessingConfig | None = None,
        ingress_metrics_collector: BotIngressMetricsCollector | None = None,
    ) -> None:
        self._user_commands_handlers: dict[str, CommandHandler] = {}
        self._default_message_handler: DefaultMessageHandler | None = None
        self._system_events_handlers: dict[
            type[BotCommand],
            SystemEventHandlerFunc,
        ] = {}
        self._sync_smartapp_event_handler: dict[
            type[SmartAppEvent],
            SyncSmartAppEventHandlerFunc,
        ] = {}
        self._middlewares = optional_sequence_to_list(middlewares)
        self._command_processing_config = (
            command_processing_config or BotCommandProcessingConfig()
        )
        self._overload_strategy = (
            self._command_processing_config.get_overload_strategy()
        )
        self._command_queue: asyncio.Queue[_QueuedBotCommand | None] = asyncio.Queue(
            maxsize=self._command_processing_config.max_queue_size,
        )
        self._processing_semaphore = asyncio.Semaphore(
            self._command_processing_config.max_concurrency,
        )
        self._workers: set[asyncio.Task[None]] = set()
        self._is_shutting_down = False
        self._tasks: WeakSet[asyncio.Task[None]] = WeakSet()
        self._ingress_metrics_collector = (
            ingress_metrics_collector or NoopIngressMetricsCollector()
        )
        self._ingress_metrics_collector.on_queue_depth(self._command_queue.qsize())

    def include(self, *others: "HandlerCollector") -> None:
        """Include other `HandlerCollector`."""
        for collector in others:
            self._include_collector(collector)

    def async_handle_bot_command(
        self,
        bot: "Bot",
        bot_command: BotCommand,
    ) -> "asyncio.Task[None]":
        ingress_metadata = self._build_ingress_command_metadata(bot_command)
        request_id = self._get_optional_context_value(request_id_var)
        if request_id is None:
            request_id = self._extract_request_id_from_command(bot_command)
        trace_id = self._get_optional_context_value(trace_id_var) or request_id
        completion = asyncio.get_running_loop().create_future()
        queued_command = _QueuedBotCommand(
            bot=bot,
            bot_command=bot_command,
            completion=completion,
            request_id=request_id,
            trace_id=trace_id,
            ingress_metadata=ingress_metadata,
        )
        self._enqueue_or_reject(queued_command)

        task = asyncio.create_task(self._wait_for_completion(completion))
        task.add_done_callback(self._log_unhandled_task_exception)
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
            context_tokens = self._set_contextvars(message, bot)
            try:
                await message_handler(message, bot)
            finally:
                self._reset_contextvars(context_tokens)

    async def handle_bot_command(self, bot_command: BotCommand, bot: "Bot") -> None:
        if isinstance(bot_command, IncomingMessage):
            message_handler = self._get_incoming_message_handler(bot_command)
            if message_handler:
                context_tokens = self._set_contextvars(bot_command, bot)
                try:
                    await message_handler(bot_command, bot)
                finally:
                    self._reset_contextvars(context_tokens)

        elif isinstance(
            bot_command,
            SystemEvent.__args__,
        ):
            event_handler = self._get_system_event_handler_or_none(bot_command)
            if event_handler:
                context_tokens = self._set_contextvars(bot_command, bot)
                try:
                    await event_handler(bot_command, bot)
                finally:
                    self._reset_contextvars(context_tokens)

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

        context_tokens = self._set_contextvars(smartapp_event, bot)
        started_at = asyncio.get_running_loop().time()
        handler_error: Exception | None = None
        try:
            return await event_handler(smartapp_event, bot)
        except Exception as exc:
            handler_error = exc
            raise
        finally:
            duration_ms = int((asyncio.get_running_loop().time() - started_at) * 1000)
            self._ingress_metrics_collector.on_command_finished(
                IngressCommandMetadata(
                    command_kind="sync_smartapp_event",
                    command_name=smartapp_event.__class__.__name__,
                ),
                IngressCommandResult(
                    duration_ms=max(duration_ms, 0),
                    error=handler_error,
                ),
                queue_depth=self._command_queue.qsize(),
            )
            self._reset_contextvars(context_tokens)

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
        visible: bool | VisibleFunc = True,
        description: str | None = None,
        middlewares: Sequence[Middleware] | None = None,
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
    ) -> IncomingMessageHandlerFunc: ...  # pragma: no cover

    @overload
    def default_message_handler(
        self,
        *,
        middlewares: Sequence[Middleware] | None = None,
    ) -> MessageHandlerDecorator: ...  # pragma: no cover

    def default_message_handler(
        self,
        handler_func: IncomingMessageHandlerFunc | None = None,
        *,
        middlewares: Sequence[Middleware] | None = None,
    ) -> IncomingMessageHandlerFunc | Callable[[IncomingMessageHandlerFunc], IncomingMessageHandlerFunc]:
        """Decorate fallback messages handler."""
        if self._default_message_handler:
            raise ValueError("Default command handler already registered")

        def decorator(
            handler_func: IncomingMessageHandlerFunc,
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

    def user_joined_to_chat(
        self,
        handler_func: HandlerFunc[JoinToChatEvent],
    ) -> HandlerFunc[JoinToChatEvent]:
        """Decorate `user_joined_to_chat` event handler."""
        self._system_event(JoinToChatEvent, handler_func)
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

    def event_deleted(
        self,
        handler_func: HandlerFunc[EventDeleted],
    ) -> HandlerFunc[EventDeleted]:
        """Decorate `event deleted` event handler."""
        self._system_event(EventDeleted, handler_func)
        return handler_func

    def conference_changed(
        self,
        handler_func: HandlerFunc[ConferenceChangedEvent],
    ) -> HandlerFunc[ConferenceChangedEvent]:
        """Decorate `conference changed` event handler."""
        self._system_event(ConferenceChangedEvent, handler_func)
        return handler_func

    def conference_created(
        self,
        handler_func: HandlerFunc[ConferenceCreatedEvent],
    ) -> HandlerFunc[ConferenceCreatedEvent]:
        """Decorate `conference created` event handler."""
        self._system_event(ConferenceCreatedEvent, handler_func)
        return handler_func

    def conference_deleted(
        self,
        handler_func: HandlerFunc[ConferenceDeletedEvent],
    ) -> HandlerFunc[ConferenceDeletedEvent]:
        """Decorate `conference deleted` event handler."""
        self._system_event(ConferenceDeletedEvent, handler_func)
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
        exception_handlers: ExceptionHandlersDict | None = None,
    ) -> None:
        exception_middleware = ExceptionMiddleware(exception_handlers or {})
        self._middlewares.insert(0, exception_middleware.dispatch)

    async def wait_active_tasks(self) -> None:
        self._is_shutting_down = True
        await self._command_queue.join()

        if self._tasks:
            await asyncio.wait(
                self._tasks,
                return_when=asyncio.ALL_COMPLETED,
            )

        await self._stop_workers()

    def _include_collector(self, other: "HandlerCollector") -> None:
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
        sync_events_duplicates: set[type[SmartAppEvent]] = set(
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
    ) -> CommandHandler | DefaultMessageHandler | None:
        return self._get_command_handler(message.body)

    def _get_command_handler(
        self,
        command: str,
    ) -> CommandHandler | DefaultMessageHandler | None:
        handler: CommandHandler | DefaultMessageHandler | None = None

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
    ) -> SystemEventHandlerFunc | None:
        event_cls = event.__class__

        handler = self._system_events_handlers.get(event_cls)
        self._log_system_event_handler_call(event_cls.__name__, handler)

        return handler

    def _get_sync_smartapp_event_handler_or_none(
        self,
        event: SmartAppEvent,
    ) -> SyncSmartAppEventHandlerFunc | None:
        event_cls = event.__class__

        handler = self._sync_smartapp_event_handler.get(event_cls)
        self._log_system_event_handler_call(event_cls.__name__, handler)

        return handler

    def _get_command_name(self, body: str) -> str | None:
        if not body:
            return None

        command_name = body.split(maxsplit=1)[0]
        if self.VALID_COMMAND_NAME_RE.match(command_name):
            return command_name

        return None

    def _build_command_handler(
        self,
        handler_func: IncomingMessageHandlerFunc,
        visible: bool | VisibleFunc,
        description: str | None,
        middlewares: list[Middleware],
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
        event_cls_name: type[BotCommand],
        handler_func: SystemEventHandlerFunc,
    ) -> SystemEventHandlerFunc:
        if event_cls_name in self._system_events_handlers:
            raise ValueError(f"Handler for {event_cls_name} already registered")

        self._system_events_handlers[event_cls_name] = handler_func

        return handler_func

    def _sync_smartapp_event(
        self,
        event_cls_name: type[SmartAppEvent],
        handler_func: SyncSmartAppEventHandlerFunc,
    ) -> SyncSmartAppEventHandlerFunc:
        if event_cls_name in self._sync_smartapp_event_handler:
            raise ValueError("Handler for sync smartapp event already registered")

        self._sync_smartapp_event_handler[event_cls_name] = handler_func

        return handler_func

    def _set_contextvars(
        self,
        bot_command: BotCommand,
        bot: "Bot",
    ) -> list[tuple[ContextVar[Any], Token[Any]]]:
        context_tokens: list[tuple[ContextVar[Any], Token[Any]]] = [
            (bot_var, bot_var.set(bot)),
            (bot_id_var, bot_id_var.set(bot_command.bot.id)),
        ]

        chat = getattr(bot_command, "chat", None)
        if chat is not None:
            context_tokens.append((chat_id_var, chat_id_var.set(chat.id)))

        return context_tokens

    def _reset_contextvars(
        self,
        context_tokens: list[tuple[ContextVar[Any], Token[Any]]],
    ) -> None:
        for context_var, token in reversed(context_tokens):
            context_var.reset(token)

    def _log_system_event_handler_call(
        self,
        event_cls_name: str,
        handler: Any,
    ) -> None:
        if handler:
            logger.info(f"Found handler for `{event_cls_name}`")
        else:
            logger.info(f"Handler for `{event_cls_name}` not found")

    def _log_default_handler_call(self, command_name: str | None) -> None:
        if command_name:
            logger.info(
                f"Handler for command `{command_name}` not found, "
                "using default handler",
            )
        else:
            logger.info("No command found, using default handler")

    async def _wait_for_completion(
        self,
        completion: asyncio.Future[None],
    ) -> None:
        await completion

    def _enqueue_or_reject(self, queued_command: _QueuedBotCommand) -> None:
        if self._is_shutting_down:
            self._reject_queued_command(
                queued_command,
                reason="bot_shutting_down",
            )
            return

        self._ensure_workers_started()

        try:
            self._command_queue.put_nowait(queued_command)
            self._ingress_metrics_collector.on_queue_depth(self._command_queue.qsize())
            return
        except asyncio.QueueFull:
            pass

        action = self._overload_strategy.on_queue_overflow(
            queue_size=self._command_queue.qsize(),
            queue_max_size=self._command_queue.maxsize,
        )
        if action is BotCommandOverloadAction.DROP_OLDEST:
            dropped_command = self._drop_oldest_queued_command()
            if dropped_command is not None:
                self._reject_queued_command(
                    dropped_command,
                    reason="queue_overflow_drop_oldest",
                )
                self._command_queue.task_done()
                self._command_queue.put_nowait(queued_command)
                self._ingress_metrics_collector.on_queue_depth(self._command_queue.qsize())
                logger.warning(
                    "Bot command queue overflow: dropped oldest queued command and "
                    "accepted newest command",
                )
                return

        self._reject_queued_command(
            queued_command,
            reason="queue_overflow_reject_new",
        )
        logger.warning(
            "Bot command queue overflow: rejected incoming command",
        )

    def _drop_oldest_queued_command(self) -> _QueuedBotCommand | None:
        while True:
            try:
                queued_item = self._command_queue.get_nowait()
            except asyncio.QueueEmpty:
                return None

            if queued_item is self._STOP_QUEUE_ITEM:
                self._command_queue.task_done()
                continue

            return queued_item

    def _reject_queued_command(
        self,
        queued_command: _QueuedBotCommand,
        *,
        reason: str,
    ) -> None:
        if queued_command.completion.done():
            return
        queued_command.completion.set_exception(BotCommandRejectedError(reason))
        self._ingress_metrics_collector.on_command_rejected(
            queued_command.ingress_metadata,
            reason=reason,
            queue_depth=self._command_queue.qsize(),
        )

    def _ensure_workers_started(self) -> None:
        if self._workers:
            return

        for index in range(self._command_processing_config.max_concurrency):
            worker_task = Context().run(asyncio.create_task, self._command_worker())
            worker_task.set_name(f"pybotx-command-worker-{index + 1}")
            self._workers.add(worker_task)

    async def _stop_workers(self) -> None:
        if not self._workers:
            return

        workers_count = len(self._workers)
        for _ in range(workers_count):
            await self._command_queue.put(self._STOP_QUEUE_ITEM)

        workers = tuple(self._workers)
        await asyncio.wait(workers, return_when=asyncio.ALL_COMPLETED)
        self._workers.clear()

    async def _command_worker(self) -> None:
        while True:
            queued_command = await self._command_queue.get()
            self._ingress_metrics_collector.on_queue_depth(self._command_queue.qsize())
            if queued_command is None:
                self._command_queue.task_done()
                self._ingress_metrics_collector.on_queue_depth(self._command_queue.qsize())
                return

            ingress_context_tokens = self._set_ingress_contextvars(queued_command)
            loop = asyncio.get_running_loop()
            started_at = loop.time()
            handler_error: Exception | None = None
            try:
                async with self._processing_semaphore:
                    await queued_command.execute(self)
            except Exception as exc:
                handler_error = exc
                if not queued_command.completion.done():
                    queued_command.completion.set_exception(exc)
            else:
                if not queued_command.completion.done():
                    queued_command.completion.set_result(None)
            finally:
                duration_ms = int((loop.time() - started_at) * 1000)
                self._ingress_metrics_collector.on_command_finished(
                    queued_command.ingress_metadata,
                    IngressCommandResult(
                        duration_ms=max(duration_ms, 0),
                        error=handler_error,
                    ),
                    queue_depth=self._command_queue.qsize(),
                )
                self._reset_contextvars(ingress_context_tokens)
                self._command_queue.task_done()
                self._ingress_metrics_collector.on_queue_depth(self._command_queue.qsize())

    def _log_unhandled_task_exception(self, task: asyncio.Task[None]) -> None:
        if task.cancelled():
            return

        error = task.exception()
        if error is None:
            return
        if isinstance(error, BotCommandRejectedError):
            logger.warning("Bot command has been rejected: {reason}", reason=error.reason)
            return

        logger.opt(exception=error).error("Bot command task failed")

    def _build_ingress_command_metadata(
        self,
        bot_command: BotCommand,
    ) -> IngressCommandMetadata:
        if isinstance(bot_command, IncomingMessage):
            command_name = self._get_command_name(bot_command.body) or "__default__"
            return IngressCommandMetadata(
                command_kind="incoming_message",
                command_name=command_name,
            )

        return IngressCommandMetadata(
            command_kind="system_event",
            command_name=bot_command.__class__.__name__,
        )

    def _extract_request_id_from_command(self, bot_command: BotCommand) -> str | None:
        sync_id = getattr(bot_command, "sync_id", None)
        if sync_id is None:
            return None
        return str(sync_id)

    def _set_ingress_contextvars(
        self,
        queued_command: _QueuedBotCommand,
    ) -> list[tuple[ContextVar[Any], Token[Any]]]:
        context_tokens: list[tuple[ContextVar[Any], Token[Any]]] = []
        if queued_command.request_id is not None:
            context_tokens.append(
                (request_id_var, request_id_var.set(queued_command.request_id)),
            )
        if queued_command.trace_id is not None:
            context_tokens.append(
                (trace_id_var, trace_id_var.set(queued_command.trace_id)),
            )
        return context_tokens

    def _get_optional_context_value(self, context_var: ContextVar[str]) -> str | None:
        try:
            return context_var.get()
        except LookupError:
            return None
