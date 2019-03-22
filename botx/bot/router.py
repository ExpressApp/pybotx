from collections import OrderedDict
from functools import partial
from typing import Callable, Dict, NoReturn, Optional

from .dispatcher.commandhandler import CommandHandler


class CommandRouter:
    _handlers: Dict[str, CommandHandler]

    def __init__(self):
        self._handlers = OrderedDict()

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        self._handlers[handler.command] = handler

    def add_commands(self, router: "CommandRouter") -> NoReturn:
        self._handlers.update(router._handlers)

    def command(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        body: Optional[str] = None,
        use_as_default_handler: bool = False,
        exclude_from_status: bool = False,
        system_command_handler: bool = False,
    ) -> Callable:
        if func:
            name = name or "".join(
                func.__name__.lower().rsplit("command", 1)[0].rsplit("_", 1)
            )
            body = (
                (body if body.startswith("/") or system_command_handler else f"/{body}")
                if body
                else f"/{name}"
            )
            description = description or func.__doc__ or f"{name} command"

            self.add_handler(
                CommandHandler(
                    command=body,
                    func=func,
                    name=name.capitalize(),
                    description=description,
                    exclude_from_status=exclude_from_status,
                    use_as_default_handler=use_as_default_handler,
                    system_command_handler=system_command_handler,
                )
            )

            return func
        else:
            return partial(
                self.command,
                name=name,
                description=description,
                body=body,
                exclude_from_status=exclude_from_status,
                use_as_default_handler=use_as_default_handler,
                system_command_handler=system_command_handler,
            )
