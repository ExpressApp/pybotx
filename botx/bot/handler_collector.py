import re
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Sequence, Type, Union

from botx.bot.exceptions import HandlerNotFoundError
from botx.bot.handler import (
    CommandHandler,
    DefaultMessageHandler,
    HandlerFunc,
    HiddenCommandHandler,
    IncomingMessageHandlerFunc,
    Middleware,
    SystemEventHandlerFunc,
    VisibleCommandHandler,
    VisibleFunc,
)
from botx.bot.models.commands.commands import BotCommand, SystemEvent
from botx.bot.models.commands.incoming_message import IncomingMessage
from botx.bot.models.commands.system_events.added_to_chat import AddedToChatEvent
from botx.bot.models.commands.system_events.chat_created import ChatCreatedEvent
from botx.bot.models.commands.system_events.deleted_from_chat import (
    DeletedFromChatEvent,
)
from botx.bot.models.status.bot_menu import BotMenu
from botx.bot.models.status.recipient import StatusRecipient
from botx.converters import optional_sequence_to_list

if TYPE_CHECKING:  # To avoid circular import
    from botx.bot.bot import Bot


class HandlerCollector:
    VALID_COMMAND_NAME_RE = re.compile(r"^\/[^\s\/]+$", flags=re.UNICODE)

    def __init__(self, middlewares: Optional[Sequence[Middleware]] = None) -> None:
        self._user_commands_handlers: Dict[str, CommandHandler] = {}
        self._default_message_handler: Optional[DefaultMessageHandler] = None
        self._system_events_handlers: Dict[
            Type[BotCommand],
            SystemEventHandlerFunc,
        ] = {}
        self._middlewares = self._reversed_middlewares(middlewares)

    def include(self, *others: "HandlerCollector") -> None:
        for collector in others:
            self._include_collector(collector)

    async def handle_bot_command(self, bot_command: BotCommand, bot: "Bot") -> None:
        if isinstance(bot_command, IncomingMessage):
            message_handler = self._get_incoming_message_handler(bot_command)
            await message_handler(bot_command, bot)

        elif isinstance(
            bot_command,
            # TODO: Replace `__args__` with `typing.get_origin` on python 3.7 drop.
            SystemEvent.__args__,  # type: ignore [attr-defined]  # noqa: WPS609
        ):
            event_handler = self._get_system_event_handler_or_none(bot_command)
            if event_handler:
                await event_handler(bot_command, bot)

        else:
            raise NotImplementedError(f"Unsupported event type: `{bot_command}`")

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
                self._reversed_middlewares(middlewares) + self._middlewares,
            )

            return handler_func

        return decorator

    def default_message_handler(
        self,
        handler_func: IncomingMessageHandlerFunc,
    ) -> IncomingMessageHandlerFunc:
        if self._default_message_handler:
            raise ValueError("Default command handler already registered")

        self._default_message_handler = DefaultMessageHandler(
            handler_func=handler_func,
            middlewares=self._middlewares,
        )

        return handler_func

    def chat_created(
        self,
        handler_func: HandlerFunc[ChatCreatedEvent],
    ) -> HandlerFunc[ChatCreatedEvent]:
        self._system_event(ChatCreatedEvent, handler_func)

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

    def _reversed_middlewares(
        self,
        middlewares: Optional[Sequence[Middleware]] = None,
    ) -> List[Middleware]:
        middlewares_list = optional_sequence_to_list(middlewares)
        return middlewares_list[::-1]

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

    def _get_incoming_message_handler(
        self,
        message: IncomingMessage,
    ) -> Union[CommandHandler, DefaultMessageHandler]:
        handler: Optional[Union[CommandHandler, DefaultMessageHandler]] = None

        command_name = self._get_command_name(message.body)
        if command_name:
            handler = self._user_commands_handlers.get(command_name)

        if handler is None:
            if self._default_message_handler:
                handler = self._default_message_handler
            else:
                raise HandlerNotFoundError(message.body)

        return handler

    def _get_system_event_handler_or_none(
        self,
        event: SystemEvent,
    ) -> Optional[SystemEventHandlerFunc]:
        event_cls_name = event.__class__

        return self._system_events_handlers.get(event_cls_name)

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
