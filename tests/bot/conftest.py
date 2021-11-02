from typing import Callable, Optional
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from botx import (
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    ExpressApp,
    IncomingMessage,
    UserDevice,
    UserEventSender,
    UserKinds,
)


@pytest.fixture
def correct_handler_trigger() -> Mock:
    return Mock()


@pytest.fixture
def incorrect_handler_trigger() -> Mock:
    return Mock()


@pytest.fixture
def incoming_message_factory(
    bot_id: UUID,
    chat_id: UUID,
) -> Callable[..., IncomingMessage]:
    def decorator(
        *,
        body: str = "",
        ad_login: Optional[str] = None,
        ad_domain: Optional[str] = None,
    ) -> IncomingMessage:
        return IncomingMessage(
            bot_id=bot_id,
            sync_id=uuid4(),
            source_sync_id=None,
            body=body,
            data={},
            metadata={},
            sender=UserEventSender(
                huid=uuid4(),
                ad_login=ad_login,
                ad_domain=ad_domain,
                username=None,
                is_chat_admin=True,
                is_chat_creator=True,
                locale=None,
                device=UserDevice(
                    manufacturer=None,
                    name=None,
                    os=None,
                ),
                express_app=ExpressApp(
                    pushes=None,
                    timezone=None,
                    permissions=None,
                    platform=None,
                    platform_package_id=None,
                    version=None,
                ),
            ),
            chat=Chat(
                id=chat_id,
                type=ChatTypes.PERSONAL_CHAT,
                host="cts.example.com",
            ),
            raw_command=None,
        )

    return decorator


@pytest.fixture
def chat_created(
    bot_id: UUID,
    chat_id: UUID,
) -> ChatCreatedEvent:
    return ChatCreatedEvent(
        bot_id=bot_id,
        sync_id=uuid4(),
        chat_name="Test",
        chat=Chat(
            id=chat_id,
            type=ChatTypes.PERSONAL_CHAT,
            host="cts.example.com",
        ),
        creator_id=uuid4(),
        members=[
            ChatCreatedMember(
                is_admin=False,
                huid=uuid4(),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command=None,
    )
