from typing import Callable

from botx import IncomingMessage, StatusRecipient


def test__status_recipient__from_message(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    incoming_message = incoming_message_factory(
        ad_login="test_login",
        ad_domain="test_domain",
    )
    status_recipient = StatusRecipient.from_incoming_message(incoming_message)

    # - Assert -
    assert status_recipient == StatusRecipient(
        bot_id=incoming_message.bot.id,
        huid=incoming_message.sender.huid,
        ad_login=incoming_message.sender.ad_login,
        ad_domain=incoming_message.sender.ad_domain,
        is_admin=incoming_message.sender.is_chat_admin,
        chat_type=incoming_message.chat.type,
    )
