import inspect
import re
from functools import partial
from typing import Any, Callable, Dict, List, Mapping, Optional, Union

from .core import (
    DEFAULT_HANDLER_BODY,
    FILE_HANDLER_NAME,
    PRIMITIVE_TYPES,
    SYSTEM_FILE_TRANSFER,
)
from .exceptions import BotXException, BotXValidationError
from .models import CommandCallback, CommandHandler, Dependency, SystemEventsEnum

PARAM_REGEX = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)}")


def get_name(handler: Callable) -> str:
    if inspect.isfunction(handler) or inspect.isclass(handler):
        return handler.__name__

    return handler.__class__.__name__


def get_regex_for_command(
    command: str, params: Dict[str, Union[str, bool, float, int]]
) -> str:
    command_regex = "^"

    idx = 0
    for match in PARAM_REGEX.finditer(command):
        param_name = match.groups()[0]

        assert param_name in params, f"undefined parameter name {param_name !r}"

        command_regex += command[idx : match.start()]
        command_regex += f"(?P<{param_name}>\\w+)"

        idx = match.end()

    command_regex += command[idx:]

    return command_regex


def replace_params(
    command: str, passed_params: Dict[str, Any], required_params: Dict[str, Any]
) -> str:
    filled_params = set()
    for key, value in list(passed_params.items()):
        if "{" + key + "}" in command:
            filled_params.add(key)
            command = command.replace("{" + key + "}", str(value))
            passed_params.pop(key)
            continue

        raise BotXValidationError(f"unknown passed parameter {key}")

    missed_params = set(required_params).difference(filled_params)
    if missed_params:
        raise BotXValidationError(f"missed required command params: {missed_params}")

    return command


class HandlersCollector:
    _handlers: Dict[str, CommandHandler]
    dependencies: List[Dependency] = []

    def __init__(self, dependencies: Optional[List[Callable]] = None) -> None:
        self._handlers = {}

        if dependencies:
            self.dependencies = [Dependency(call=call) for call in dependencies]

    def command_for(self, command_name: str, **params: Any) -> str:
        for handler in self._handlers.values():
            if handler.name == command_name:
                return replace_params(
                    handler.command, params, handler.callback.command_params
                )
        else:
            raise BotXException(f"handler with name {command_name} does not exist")

    @property
    def handlers(self) -> Dict[str, CommandHandler]:
        return self._handlers

    def add_handler(self, handler: CommandHandler, force_replace: bool = False) -> None:
        if handler.menu_command in self._handlers and not force_replace:
            raise BotXException(
                f"can not add 2 handlers for {handler.menu_command !r} command"
            )

        self._handlers[handler.menu_command] = handler

    def include_handlers(
        self, collector: "HandlersCollector", force_replace: bool = False
    ) -> None:
        for handler in collector.handlers.values():
            handler.callback.background_dependencies = (
                self.dependencies + handler.callback.background_dependencies
            )
            self.add_handler(handler, force_replace=force_replace)

    def handler(
        self,
        callback: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        command: Optional[str] = None,
        commands: Optional[List[str]] = None,
        use_as_default_handler: Optional[bool] = False,
        exclude_from_status: Optional[bool] = False,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        if callback:
            assert inspect.isfunction(callback) or inspect.ismethod(
                callback
            ), "A callback must be function or method"

            transformed_dependencies = (
                [Dependency(call=dep) for dep in dependencies] if dependencies else []
            )

            if not commands:
                commands = [command or ""]
            elif command:
                commands.append(command)

            for command in commands:
                command_name = name or get_name(callback)

                if not command:
                    command_body = (name or get_name(callback)).replace("_", "-")
                    command = command_body

                if not (exclude_from_status or use_as_default_handler):
                    command = "/" + command.strip("/")

                description = description or inspect.cleandoc(callback.__doc__ or "")
                full_description = full_description or description

                signature: inspect.Signature = inspect.signature(callback)
                params: Mapping[str, inspect.Parameter] = signature.parameters
                handler_params = {}
                for param_name, param in params.items():
                    if param.annotation in PRIMITIVE_TYPES:
                        handler_params[param_name] = param.annotation

                regex = get_regex_for_command(command, handler_params)
                menu_command = command.split(" ", 1)[0]

                handler = CommandHandler(
                    regex_command=regex,
                    command=command,
                    menu_command=menu_command,
                    callback=CommandCallback(
                        callback=callback,
                        background_dependencies=(
                            self.dependencies + transformed_dependencies
                        ),
                        command_params=handler_params,
                    ),
                    name=command_name,
                    description=description,
                    full_description=full_description,
                    exclude_from_status=exclude_from_status,
                    use_as_default_handler=use_as_default_handler,
                )

                self.add_handler(handler)

            return callback

        return partial(
            self.handler,
            name=name,
            description=description,
            full_description=full_description,
            command=command,
            commands=commands,
            exclude_from_status=exclude_from_status,
            use_as_default_handler=use_as_default_handler,
            dependencies=dependencies,
        )

    def hidden_command_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        command: Optional[str] = None,
        commands: Optional[List[str]] = None,
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
        self,
        callback: Optional[Callable] = None,
        *,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        return self.handler(
            callback=callback,
            name=FILE_HANDLER_NAME,
            command=SYSTEM_FILE_TRANSFER,
            exclude_from_status=True,
            dependencies=dependencies,
        )

    def default_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        return self.handler(
            callback=callback,
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

        return self.hidden_command_handler(
            callback=callback, name=name, command=command, dependencies=dependencies
        )

    def chat_created_handler(
        self,
        callback: Optional[Callable] = None,
        *,
        dependencies: Optional[List[Callable]] = None,
    ) -> Callable:
        return self.system_event_handler(
            callback=callback,
            event=SystemEventsEnum.chat_created,
            dependencies=dependencies,
        )
