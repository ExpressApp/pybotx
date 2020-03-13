import logging
from typing import Any, Callable

import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger

from botx import (
    Bot,
    Depends,
    ExpressServer,
    IncomingMessage,
    Message,
    ServerCredentials,
)
from botx.testing import MessageBuilder

logger.enable("botx")


@pytest.fixture
def incoming_message() -> IncomingMessage:
    return MessageBuilder().message


@pytest.fixture
def bot(incoming_message: IncomingMessage) -> Bot:
    bot = Bot(
        known_hosts=[
            ExpressServer(
                host=incoming_message.user.host,
                secret_key="",
                server_credentials=ServerCredentials(
                    bot_id=incoming_message.bot_id, token=""
                ),
            )
        ]
    )

    def background_dependency_that_fills_message_and_bot_state(
        message: Message,
    ) -> None:
        ...  # pragma: no cover

    def include_in_status(*_: Any) -> bool:
        return True  # pragma: no cover

    def exclude_from_status(*_: Any) -> bool:
        return False  # pragma: no cover

    @bot.handler
    def regular_handler() -> None:
        ...  # pragma: no cover

    @bot.handler(command="/handler-command")
    def regular_handler_with_command() -> None:
        ...  # pragma: no cover

    @bot.handler(commands=["/handler-command1", "/handler-command2"])
    def regular_handler_with_command_aliases() -> None:
        ...  # pragma: no cover

    @bot.handler(
        command="/handler-command3", commands=["/handler-command4", "/handler-command5"]
    )
    def regular_handler_with_command_and_command_aliases() -> None:
        ...  # pragma: no cover

    @bot.handler(name="regular-handler-with-name")
    def regular_handler_with_custom_name() -> None:
        ...  # pragma: no cover

    @bot.handler(
        dependencies=[Depends(background_dependency_that_fills_message_and_bot_state)]
    )
    def regular_handler_with_background_dependencies() -> None:
        ...  # pragma: no cover

    @bot.handler(include_in_status=False)
    def regular_handler_that_excluded_from_status_and_auto_body() -> None:
        ...  # pragma: no cover

    @bot.handler(
        command="regular-handler-with-excluding-from-status", include_in_status=False
    )
    def regular_handler_that_excluded_from_status_and_passed_body() -> None:
        ...  # pragma: no cover

    @bot.handler(include_in_status=include_in_status)
    def regular_handler_that_included_in_status_by_callable_function() -> None:
        ...  # pragma: no cover

    @bot.handler(include_in_status=exclude_from_status)
    def regular_handler_that_excluded_from_status_by_callable_function() -> None:
        ...  # pragma: no cover

    @bot.default
    def default_handler() -> None:
        ...  # pragma: no cover

    @bot.hidden
    def hidden_handler() -> None:
        ...  # pragma: no cover

    @bot.chat_created
    def chat_created_handler() -> None:
        ...  # pragma: no cover

    @bot.file_transfer
    def file_transfer_handler() -> None:
        ...  # pragma: no cover

    @bot.middleware
    async def middleware_for_handlers(message: Message, executor: Callable) -> None:
        await executor(message)

    return bot


@pytest.fixture
def loguru_caplog(caplog: LogCaptureFixture) -> LogCaptureFixture:
    class PropogateHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)


def handler_function() -> None:
    """Handler with description that does nothing."""
    ...  # pragma: no cover


class HandlerClass:
    def handler_method_snake_case(self) -> None:
        ...  # pragma: no cover

    def handlerMethodPascalCase(self) -> None:
        ...  # pragma: no cover

    def HandlerMethodCamelCase(self) -> None:
        ...  # pragma: no cover

    def __call__(self) -> None:
        ...  # pragma: no cover
