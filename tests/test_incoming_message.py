from typing import Callable

from botx import IncomingMessage


def test_upn_propetry_not_filled(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory()

    # - Assert -
    assert message.sender.upn is None


def test_upn_propetry_filled(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(ad_login="login", ad_domain="domain")

    # - Assert -
    assert message.sender.upn == "login@domain"
