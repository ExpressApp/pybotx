from typing import TypeVar
from collections.abc import Sequence
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.message.message_options import MessageOptions

TItem = TypeVar("TItem")


def optional_sequence_to_list(
    optional_sequence: Sequence[TItem] | None,
) -> list[TItem]:
    return list(optional_sequence or [])


def resolve_message_options(
    options: MessageOptions | None,
    *,
    recipients: Missing[list[UUID]] = Undefined,
    silent_response: Missing[bool] = Undefined,
    markup_auto_adjust: Missing[bool] = Undefined,
    stealth_mode: Missing[bool] = Undefined,
    send_push: Missing[bool] = Undefined,
    ignore_mute: Missing[bool] = Undefined,
) -> tuple[
    Missing[list[UUID]],
    Missing[bool],
    Missing[bool],
    Missing[bool],
    Missing[bool],
    Missing[bool],
]:
    if options is None:
        return (
            recipients,
            silent_response,
            markup_auto_adjust,
            stealth_mode,
            send_push,
            ignore_mute,
        )

    return (
        recipients if recipients is not Undefined else options.recipients,
        silent_response if silent_response is not Undefined else options.silent_response,
        markup_auto_adjust if markup_auto_adjust is not Undefined else options.markup_auto_adjust,
        stealth_mode if stealth_mode is not Undefined else options.stealth_mode,
        send_push if send_push is not Undefined else options.send_push,
        ignore_mute if ignore_mute is not Undefined else options.ignore_mute,
    )
