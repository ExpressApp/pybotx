from functools import partial
from typing import Callable, Dict, List, Optional

from .core import (
    DEFAULT_HANDLER_BODY,
    FILE_HANDLER_NAME,
    SYSTEM_CHAT_CREATED,
    SYSTEM_FILE_TRANSFER,
    BotXException,
)
from .models import CommandCallback, CommandHandler


class HandlersCollector:
    _handlers: Dict[str, CommandHandler]

    def __init__(self) -> None:
        self._handlers = {}

    @property
    def handlers(self) -> Dict[str, CommandHandler]:
        return self._handlers

    def add_handler(self, handler: CommandHandler, force_replace: bool = False) -> None:
        if handler.command in self._handlers and not force_replace:
            raise BotXException(
                f"can not add 2 handlers for {handler.command !r} command"
            )

        self._handlers[handler.command] = handler

    def include_handlers(
        self, router: "HandlersCollector", force_replace: bool = False
    ) -> None:
        for handler in router.handlers.values():
            self.add_handler(handler, force_replace=force_replace)

    def handler(
        self,
        callback: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        command: Optional[str] = None,
        commands: Optional[List[str]] = None,
        use_as_default_handler: Optional[bool] = False,
        exclude_from_status: Optional[bool] = False,
        system_command_handler: Optional[bool] = False,
    ) -> Callable:
        if callback:
            if not commands:
                commands = [command or ""]
            elif command:
                commands.append(command)

            for command in commands:
                try:
                    command_name = name or callback.__name__.lower()
                    name = name or callback.__name__.lower().replace("_", "-")
                except AttributeError:
                    raise BotXException(
                        "can not determine name for handler, set it explicitly"
                    )

                if command:
                    if system_command_handler or use_as_default_handler:
                        command = command.strip("/")
                    else:
                        command = f"/{command.strip('/')}"
                else:
                    command = f"/{name}"

                description = (
                    description or callback.__doc__ or f"{name.capitalize()} handler"
                )

                self.add_handler(
                    CommandHandler(
                        command=command,
                        callback=CommandCallback(callback=callback),
                        name=command_name,
                        description=description,
                        exclude_from_status=exclude_from_status,
                        use_as_default_handler=use_as_default_handler,
                        system_command_handler=system_command_handler,
                    )
                )

            return callback

        return partial(
            self.handler,
            name=name,
            description=description,
            command=command,
            commands=commands,
            exclude_from_status=exclude_from_status,
            use_as_default_handler=use_as_default_handler,
            system_command_handler=system_command_handler,
        )

    def hidden_command_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        command: Optional[str] = None,
        commands: Optional[List[str]] = None,
    ) -> Callable:
        return self.handler(
            callback=callback,
            name=name,
            command=command,
            commands=commands,
            exclude_from_status=True,
        )

    def file_handler(self, callback: Callable) -> Callable:
        return self.handler(
            callback,
            name=FILE_HANDLER_NAME,
            command=SYSTEM_FILE_TRANSFER,
            system_command_handler=True,
        )

    def default_handler(self, callback: Callable) -> Callable:
        return self.handler(
            callback, command=DEFAULT_HANDLER_BODY, use_as_default_handler=True
        )

    def system_command_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        command: str,
        name: Optional[str] = None,
    ) -> Callable:
        return self.handler(
            callback=callback,
            name=name,
            command="system:" + command,
            system_command_handler=True,
        )

    def chat_created_handler(self, callback: Callable) -> Callable:
        return self.system_command_handler(callback, command=SYSTEM_CHAT_CREATED)
