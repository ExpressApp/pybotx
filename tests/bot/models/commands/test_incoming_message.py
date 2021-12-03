from typing import Callable, Tuple

import pytest

from botx import IncomingMessage


def test__upn_property__not_filled(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory()

    # - Assert -
    assert message.sender.upn is None


def test__upn_property__filled(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(ad_login="login", ad_domain="domain")

    # - Assert -
    assert message.sender.upn == "login@domain"


@pytest.mark.parametrize(
    "body,argument_answer",
    [
        ("", ""),
        ("/command", ""),
    ],
)
def test__argument__not_filled(
    incoming_message_factory: Callable[..., IncomingMessage],
    body: str,
    argument_answer: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=body)

    # - Assert -
    assert message.argument == argument_answer


@pytest.mark.parametrize(
    "body,argument_answer",
    [
        ("/command arg1 ", "arg1"),
        ("/command arg1  arg2", "arg1  arg2"),
    ],
)
def test__argument__filled(
    incoming_message_factory: Callable[..., IncomingMessage],
    body: str,
    argument_answer: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=body)

    # - Assert -
    assert message.argument == argument_answer


@pytest.mark.parametrize(
    "body,argument_answer",
    [
        ("", ()),
        ("/command", ()),
    ],
)
def test__arguments__not_filled(
    incoming_message_factory: Callable[..., IncomingMessage],
    body: str,
    argument_answer: Tuple[str, ...],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=body)

    # - Assert -
    assert message.arguments == argument_answer


@pytest.mark.parametrize(
    "body,argument_answer",
    [
        ("/command arg1 ", ("arg1",)),
        ("/command arg1  arg2", ("arg1", "arg2")),
    ],
)
def test__arguments__filled(
    incoming_message_factory: Callable[..., IncomingMessage],
    body: str,
    argument_answer: Tuple[str, ...],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=body)

    # - Assert -
    assert message.arguments == argument_answer
