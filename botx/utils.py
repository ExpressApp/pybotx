"""Some helper functions that are used in library."""

import inspect
from typing import Callable, List, Optional, Sequence, TypeVar
from uuid import UUID

from httpx import Response

from botx.models import messages
from botx.models.files import File
from botx.models.sending import MessagePayload, SendingCredentials, UpdatePayload

TSequenceElement = TypeVar("TSequenceElement")


def optional_sequence_to_list(
    seq: Optional[Sequence[TSequenceElement]] = None,
) -> List[TSequenceElement]:
    """Convert optional sequence of elements to list.

    Arguments:
        seq: sequence that should be converted to list.

    Returns:
        List of passed elements.
    """
    return list(seq or [])


def get_name_from_callable(handler: Callable) -> str:
    """Get auto name from given callable object.

    Arguments:
        handler: callable object that will be used to retrieve auto name for handler.

    Returns:
        Name obtained from callable.
    """
    is_function = inspect.isfunction(handler)
    is_method = inspect.ismethod(handler)
    is_class = inspect.isclass(handler)
    if is_function or is_method or is_class:
        return handler.__name__
    return handler.__class__.__name__


class LogsShapeBuilder:  # noqa: WPS214
    """Helper for obtaining dictionaries for loguru payload."""

    @classmethod
    def get_token_request_shape(cls, host: str, bot_id: UUID, signature: str) -> dict:
        """Get shape for obtaining token request.

        Arguments:
            host: host for sending request.
            bot_id: bot_id for token.
            signature: query param with bot signature.

        Returns:
            Shape for logging in loguru.
        """
        return {"host": host, "bot_id": bot_id, "signature": signature}

    @classmethod
    def get_response_shape(cls, response: Response) -> dict:
        """Get shape for response from BotX API.

        Arguments:
            response: response from BotX API.

        Returns:
            Shape for logging in loguru.
        """
        response_content = response.json()

        return {
            "status_code": response.status_code,
            "request_url": response.request.url if response.request else None,
            "response_content": response_content,
        }

    @classmethod
    def get_notification_shape(
        cls, credentials: SendingCredentials, payload: MessagePayload
    ) -> dict:
        """Get shape for notification that will be sent to BotX API.

        Arguments:
            credentials: credentials for notification.
            payload: notification payload.

        Returns:
            Shape for logging in loguru.
        """
        return {
            "credentials": credentials.dict(exclude={"token", "sync_id", "chat_id"}),
            "payload": cls.get_payload_shape(payload),
        }

    @classmethod
    def get_command_result_shape(
        cls, credentials: SendingCredentials, payload: MessagePayload
    ) -> dict:
        """Get shape for command result that will be sent to BotX API.

        Arguments:
            credentials: credentials for command result.
            payload: command result payload.

        Returns:
            Shape for logging in loguru.
        """
        return {
            "credentials": credentials.dict(exclude={"token", "chat_ids", "chat_id"}),
            "payload": cls.get_payload_shape(payload),
        }

    @classmethod
    def get_edition_shape(
        cls, credentials: SendingCredentials, payload: UpdatePayload
    ) -> dict:
        """Get shape for event edition that will be send to BotX API.

        Arguments:
            credentials: credentials for event edition.
            payload: event edition payload.

        Returns:
            Shape for logging in loguru.
        """
        return {
            "credentials": credentials.dict(
                exclude={"token", "bot_id", "chat_ids", "chat_id"}
            ),
            "payload": payload.copy(
                update={
                    "text": cls._convert_text_to_logs_format(payload.text)
                    if payload.text
                    else None
                }
            ).dict(exclude_none=True),
        }

    @classmethod
    def get_payload_shape(cls, payload: MessagePayload) -> dict:
        """Get shape for payload that will be sent to BotX API.

        Arguments:
            payload: payload.

        Returns:
            Shape for logging in loguru.
        """
        return payload.copy(
            update={
                "text": cls._convert_text_to_logs_format(payload.text),
                "file": cls._convert_file_to_logs_format(payload.file),
            }
        ).dict()

    @classmethod
    def get_message_shape(cls, message: messages.Message) -> dict:
        """Get shape for incoming message from BotX API.

        Arguments:
            message: incoming message.

        Returns:
            Shape for logging in loguru.
        """
        return message.incoming_message.copy(
            update={
                "body": cls._convert_text_to_logs_format(message.body),
                "file": cls._convert_file_to_logs_format(message.file),
            }
        ).dict()

    @classmethod
    def _convert_text_to_logs_format(cls, text: str) -> str:
        """Convert text into format that is suitable for logs.

        Arguments:
            text: text that should be formatted.

        Returns:
            Shape for logging in loguru.
        """
        max_log_text_length = 50
        start_text_index = 15
        end_text_index = 5

        return (
            "...".join((text[:start_text_index], text[-end_text_index:]))
            if len(text) > max_log_text_length
            else text
        )

    @classmethod
    def _convert_file_to_logs_format(cls, file: Optional[File]) -> Optional[dict]:
        """Convert file to a new file that will be showed in logs.

        Arguments:
            file: file that should be converted.

        Returns:
            New file or nothing.
        """
        return file.copy(update={"data": "[file content]"}).dict() if file else None
