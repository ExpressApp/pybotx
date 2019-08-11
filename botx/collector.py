import re
from functools import partial
from typing import Callable, Dict, List, Optional, Pattern, Union

from .core import (
    DEFAULT_HANDLER_BODY,
    FILE_HANDLER_NAME,
    SYSTEM_FILE_TRANSFER,
    BotXException,
)
from .models import CommandCallback, CommandHandler, Dependency, SystemEventsEnum
from .types import COMMAND_STRING


class HandlersCollector:
    _handlers: Dict[Pattern, CommandHandler]
    dependencies: List[Dependency] = []

    def __init__(self, dependencies: Optional[List[Callable]] = None) -> None:
        self._handlers = {}

        if dependencies:
            self.dependencies = [Dependency(call=call) for call in dependencies]

    @property
    def handlers(self) -> Dict[Pattern, CommandHandler]:
        return self._handlers

    def add_handler(self, handler: CommandHandler, force_replace: bool = False) -> None:
        if handler.command in self._handlers and not force_replace:
            raise BotXException(
                f"can not add 2 handlers for {handler.command !r} command"
            )

        self._handlers[handler.command] = handler

    def include_handlers(
        self, collector: "HandlersCollector", force_replace: bool = False
    ) -> None:
        for handler in collector.handlers.values():
            self.add_handler(handler, force_replace=force_replace)

    def handler(
        self,
        callback: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        command: Optional[COMMAND_STRING] = None,
        commands: Optional[List[COMMAND_STRING]] = None,
        use_as_default_handler: Optional[bool] = False,
        exclude_from_status: Optional[bool] = False,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        if callback:
            transformed_dependencies = (
                [Dependency(call=dep) for dep in dependencies] if dependencies else []
            )

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

                if not command:
                    command = f"/{name}"

                if isinstance(command, str):
                    command = re.escape(f"/{command.strip('/')}")
                else:
                    command = command.pattern

                description = (
                    description or callback.__doc__ or f"{name.capitalize()} handler"
                )

                handler = CommandHandler(
                    command=command,
                    callback=CommandCallback(
                        callback=callback,
                        background_dependencies=self.dependencies
                        + transformed_dependencies,
                    ),
                    name=command_name,
                    description=description,
                    exclude_from_status=exclude_from_status,
                    use_as_default_handler=use_as_default_handler,
                )

                self.add_handler(handler)

            return callback

        return partial(
            self.handler,
            name=name,
            description=description,
            command=command,
            commands=commands,
            exclude_from_status=exclude_from_status,
            use_as_default_handler=use_as_default_handler,
            dependencies=dependencies,
        )

    def regex_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        command: Optional[str] = None,
        commands: Optional[List[str]] = None,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        return self.hidden_command_handler(
            callback=callback,
            name=name,
            command=re.compile(command) if command else None,
            commands=[re.compile(cmd) for cmd in commands] if commands else None,
            dependencies=dependencies,
        )

    def hidden_command_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        command: Optional[COMMAND_STRING] = None,
        commands: Optional[List[COMMAND_STRING]] = None,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        return self.handler(
            callback=callback,
            name=name,
            command=command,
            commands=commands,
            exclude_from_status=True,
            dependencies=dependencies,
        )

    def file_handler(
        self, callback: Callable, dependencies: Optional[List[Callable]] = None
    ) -> Callable:
        return self.handler(
            callback,
            name=FILE_HANDLER_NAME,
            command=SYSTEM_FILE_TRANSFER,
            exclude_from_status=True,
            dependencies=dependencies,
        )

    def default_handler(
        self, callback: Callable, dependencies: Optional[List[Callable]] = None
    ) -> Callable:
        return self.handler(
            callback,
            command=DEFAULT_HANDLER_BODY,
            use_as_default_handler=True,
            dependencies=dependencies,
        )

    def system_event_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        event: Union[str, SystemEventsEnum],
        name: Optional[str] = None,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        if isinstance(event, SystemEventsEnum):
            command = event.value
        else:
            command = event

        return self.regex_handler(
            callback=callback, name=name, command=command, dependencies=dependencies
        )

    def chat_created_handler(
        self, callback: Callable, dependencies: Optional[List[Callable]] = None
    ) -> Callable:
        return self.system_event_handler(
            callback, event=SystemEventsEnum.chat_created, dependencies=dependencies
        )
