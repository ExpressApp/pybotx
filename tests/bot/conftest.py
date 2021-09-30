import logging
from typing import Callable, Generator, Optional
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from loguru import logger

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
def chat_created() -> ChatCreatedEvent:
    return ChatCreatedEvent(
        bot_id=uuid4(),
        sync_id=uuid4(),
        chat_id=uuid4(),
        chat_name="Test",
        chat_type=ChatTypes.PERSONAL_CHAT,
        host="cts.example.com",
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


@pytest.fixture()
def loguru_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    # https://github.com/Delgan/loguru/issues/59

    class PropogateHandler(logging.Handler):  # noqa: WPS431
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)
