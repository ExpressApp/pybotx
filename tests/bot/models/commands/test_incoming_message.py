from typing import Callable

from botx import IncomingMessage


def test__upn_propetry__not_filled(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory()

    # - Assert -
    assert message.sender.upn is None


def test__upn_propetry__filled(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(ad_login="login", ad_domain="domain")

    # - Assert -
    assert message.sender.upn == "login@domain"
