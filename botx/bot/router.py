from collections import OrderedDict
from functools import partial
from typing import Callable, Dict, Optional

from .dispatcher.command_handler import CommandHandler


class CommandRouter:
    _handlers: Dict[str, CommandHandler]

    def __init__(self):
        self._handlers = OrderedDict()

    @property
    def handlers(self):
        return self._handlers

    def add_handler(self, handler: CommandHandler):
        self._handlers[handler.command] = handler

    def add_commands(self, router: "CommandRouter"):
        self._handlers.update(router.handlers)

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
    ):
        if func:
            command_name = name or func.__name__.lower()

            name = name or "".join(
                func.__name__.lower().rsplit("command", 1)[0].split("_")
            )
            body = (
                (body if body.startswith("/") or system_command_handler else f"/{body}")
                if body
                else f"/{name}"
            )
            description = description or func.__doc__ or f"{name} command"

            handler = CommandHandler(
                command=body,
                func=func,
                name=command_name,
                description=description,
                exclude_from_status=exclude_from_status,
                use_as_default_handler=use_as_default_handler,
                system_command_handler=system_command_handler,
            )

            self.add_handler(handler)

            return handler

        return partial(
            self.command,
            name=name,
            description=description,
            body=body,
            exclude_from_status=exclude_from_status,
            use_as_default_handler=use_as_default_handler,
            system_command_handler=system_command_handler,
        )

    def file_handler(self, func):
        return self.command(
            func,
            name="file_receiver",
            body="file_transfer",
            exclude_from_status=True,
            system_command_handler=True,
        )

    def default_handler(self, func):
        return self.command(func, use_as_default_handler=True)

    def chat_created(self, func):
        return self.command(
            func, body="system:chat_created", system_command_handler=True
        )
