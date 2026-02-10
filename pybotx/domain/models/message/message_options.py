from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined


@dataclass(slots=True)
class MessageOptions:
    recipients: Missing[list[UUID]] = Undefined
    silent_response: Missing[bool] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined
    stealth_mode: Missing[bool] = Undefined
    send_push: Missing[bool] = Undefined
    ignore_mute: Missing[bool] = Undefined


NotificationOptions = MessageOptions


__all__ = ("MessageOptions", "NotificationOptions")
