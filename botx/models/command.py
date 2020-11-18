from typing import Optional, Sequence

from pydantic import BaseModel


class CommandDescriptor(BaseModel):
    """Bot command descriptor.

    Used when defining a handler.
    """

    #: command body that will trigger command execution.
    command: Optional[str] = None

    #: list of body command templates.
    commands: Optional[Sequence[str]] = None

    #: command name.
    name: Optional[str] = None

    #: command description that will be shown in a menu.
    description: Optional[str] = None

    #: full description that can be used for example in `/help`
    full_description: Optional[str] = None
