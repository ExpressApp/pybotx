import re
from typing import TYPE_CHECKING, Callable, Dict, Optional

from botx.exceptions import HandlerNotFoundException
from botx.handler import BotXCommandHandler, HandlerFunc
from botx.incoming_message import IncomingMessage
from botx.system_events.chat_created import ChatCreatedEvent
from botx.system_events.typing import SystemEvent
from botx.typing import BotXCommand

if TYPE_CHECKING:
    from botx.bot import Bot

IncomingMessageHandler = HandlerFunc[IncomingMessage]


class HandlerCollector:
    VALID_COMMAND_NAME_RE = re.compile(r"^\/[^\s\/]+$", flags=re.UNICODE)

    def __init__(self) -> None:
        self._user_commands_handlers: Dict[str, BotXCommandHandler] = {}
        self._default_message_handler: Optional[BotXCommandHandler] = None
        self._system_events_handlers: Dict[str, BotXCommandHandler] = {}

    def include(self, *others: "HandlerCollector") -> None:
        for collector in others:
            self._include_collector(collector)

    async def handle_botx_command(self, botx_command: BotXCommand, bot: "Bot") -> None:
        handler: Optional[BotXCommandHandler]

        if isinstance(botx_command, IncomingMessage):
            handler = self._get_incoming_message_handler(botx_command)
        elif isinstance(botx_command, SystemEvent):
            handler = self._get_system_event_handler_or_none(botx_command)
            if handler is None:
                return

        else:
            raise NotImplementedError(f"Unsupported event type: `{botx_command}`")

        await handler(botx_command, bot)

    def command(
        self,
        command_name: str,
    ) -> Callable[[IncomingMessageHandler], IncomingMessageHandler]:
        if not self.VALID_COMMAND_NAME_RE.match(command_name):
            raise ValueError("Command should start with '/' and doesn't include spaces")

        def decorator(handler_func: IncomingMessageHandler) -> IncomingMessageHandler:
            if command_name in self._user_commands_handlers:
                raise ValueError(
                    f"Handler for command `{command_name}` already registered",
                )

            self._user_commands_handlers[command_name] = BotXCommandHandler(
                handler_func=handler_func,
            )

            return handler_func

        return decorator

    def default_message_handler(
        self,
        handler_func: IncomingMessageHandler,
    ) -> IncomingMessageHandler:
        if self._default_message_handler:
            raise ValueError("Default command handler already registered")

        self._default_message_handler = BotXCommandHandler(handler_func=handler_func)

        return handler_func

    def chat_created(
        self,
        handler_func: HandlerFunc[ChatCreatedEvent],
    ) -> HandlerFunc[ChatCreatedEvent]:
        self._system_event(ChatCreatedEvent.__name__, handler_func)

        return handler_func

    def _include_collector(self, other: "HandlerCollector") -> None:
        # - Message handlers -
        command_duplicates = set(self._user_commands_handlers) & set(
            other._user_commands_handlers,
        )
        if command_duplicates:
            raise ValueError(
                f"Handlers for {command_duplicates} commands already registered",
            )

        self._user_commands_handlers.update(other._user_commands_handlers)

        # - Default message handler -
        if self._default_message_handler and other._default_message_handler:
            raise ValueError("Default message handler already registered")

        if not self._default_message_handler:
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

    def _get_incoming_message_handler(
        self,
        message: IncomingMessage,
    ) -> BotXCommandHandler:
        handler: Optional[BotXCommandHandler] = None

        command_name = self._get_command_name(message.body)
        if command_name:
            handler = self._user_commands_handlers.get(command_name)

        if handler is None:
            if self._default_message_handler:
                handler = self._default_message_handler
            else:
                raise HandlerNotFoundException(message.body)

        return handler

    def _get_system_event_handler_or_none(
        self,
        event: SystemEvent,
    ) -> Optional[BotXCommandHandler]:
        event_cls_name = event.__class__.__name__

        return self._system_events_handlers.get(event_cls_name)

    def _get_command_name(self, body: str) -> Optional[str]:
        if not body:
            return None

        command_name = body.split(maxsplit=1)[0]
        if self.VALID_COMMAND_NAME_RE.match(command_name):
            return command_name

        return None

    def _system_event(
        self,
        event_cls_name: str,
        handler_func: HandlerFunc[SystemEvent],
    ) -> HandlerFunc[SystemEvent]:
        if event_cls_name in self._system_events_handlers:
            raise ValueError(f"Handler for {event_cls_name} already registered")

        self._system_events_handlers[event_cls_name] = BotXCommandHandler(
            handler_func=handler_func,
        )
        return handler_func
