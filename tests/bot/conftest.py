from typing import Callable, Optional
from unittest.mock import Mock
from uuid import uuid4

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
def right_handler_trigger() -> Mock:
    return Mock()


@pytest.fixture
def wrong_handler_trigger() -> Mock:
    return Mock()


@pytest.fixture
def incoming_message_factory() -> Callable[..., IncomingMessage]:
    def decorator(
        *,
        body: str = "",
        ad_login: Optional[str] = None,
        ad_domain: Optional[str] = None,
    ) -> IncomingMessage:
        return IncomingMessage(
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
                id=uuid4(),
                bot_id=uuid4(),
                type=ChatTypes.PERSONAL_CHAT,
                host="cts.example.com",
            ),
            raw_command=None,
        )

    return decorator


@pytest.fixture
def chat_created() -> ChatCreatedEvent:
    return ChatCreatedEvent(
        sync_id=uuid4(),
        chat_id=uuid4(),
        bot_id=uuid4(),
        host="cts.example.com",
        chat_name="Test",
        chat_type=ChatTypes.PERSONAL_CHAT,
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
