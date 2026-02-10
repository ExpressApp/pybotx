from uuid import uuid4

from pybotx.domain.converters import resolve_message_options
from pybotx.domain.missing import Undefined
from pybotx.domain.models.message.message_options import MessageOptions


def test__resolve_message_options__none_pass_through() -> None:
    recipients = [uuid4()]
    result = resolve_message_options(
        None,
        recipients=recipients,
        silent_response=True,
        markup_auto_adjust=False,
        stealth_mode=True,
        send_push=False,
        ignore_mute=True,
    )

    assert result == (
        recipients,
        True,
        False,
        True,
        False,
        True,
    )


def test__resolve_message_options__fills_undefined() -> None:
    recipients = [uuid4()]
    options = MessageOptions(
        recipients=recipients,
        silent_response=True,
        markup_auto_adjust=False,
        stealth_mode=True,
        send_push=False,
        ignore_mute=True,
    )

    result = resolve_message_options(options)

    assert result == (
        recipients,
        True,
        False,
        True,
        False,
        True,
    )


def test__resolve_message_options__explicit_overrides_options() -> None:
    options = MessageOptions(silent_response=True, markup_auto_adjust=True)

    result = resolve_message_options(
        options,
        silent_response=False,
        markup_auto_adjust=False,
    )

    assert result[0] is Undefined
    assert result[1] is False
    assert result[2] is False
