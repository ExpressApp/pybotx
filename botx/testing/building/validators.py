"""Validators and converters for fields in builder."""

from typing import Any, BinaryIO, Optional, TextIO, Union

from botx.models import enums, events, files
from botx.models.messages.incoming_message import Sender


def validate_body_corresponds_command(body: str, values: dict) -> str:  # noqa: WPS110
    """Check that passed body can be proceed.

    Arguments:
        body: passed body.
        values: already validated validated_values.

    Returns:
        Checked passed body.
    """
    _check_system_command_properties(
        body, values.get("system_command", False), values["command_data"], values,
    )
    return body


def validate_command_type_corresponds_command(
    is_system_command: bool, values: dict,  # noqa: WPS110
) -> bool:
    """Check that command type corresponds body.

    Arguments:
        is_system_command: is command marked as system command.
        values: already validated validated_values.

    Returns:
        Checked flag.
    """
    if is_system_command:
        _check_system_command_properties(
            values["body"], is_system_command, values["command_data"], values,
        )

    return is_system_command


def convert_to_acceptable_file(
    file: Optional[Union[files.File, BinaryIO, TextIO]],
) -> Optional[files.File]:
    """Convert file to File that can be passed into message.

    Arguments:
        file: passed file.

    Returns:
        Converted file.
    """
    if isinstance(file, files.File) or file is None:
        return file

    new_file = files.File.from_file(file, filename="temp.txt")
    new_file.file_name = file.name
    return new_file


def _check_system_command_properties(
    body: str, is_system_command: bool, command_data: dict, validated_values: dict,
) -> None:
    if is_system_command:
        event = enums.SystemEvents(body)  # check that is real system event
        event_shape = events.EVENTS_SHAPE_MAP.get(event)
        if event_shape is not None:
            event_shape.parse_obj(command_data)  # check event data
        _event_checkers[event](**validated_values)  # type: ignore


def _check_common_system_event(user: Sender, **_kwargs: Any) -> None:
    error_field = ""
    if user.user_huid is not None:
        error_field = "user_huid"
    elif user.ad_login is not None:
        error_field = "ad_login"
    elif user.ad_domain is not None:
        error_field = "ad_domain"
    elif user.username is not None:
        error_field = "username"

    if error_field:
        raise ValueError(
            "user in system:chat_created can not have {0}".format(error_field),
        )


def _check_file_transfer_event(file: Optional[files.File], **_kwargs: Any) -> None:
    if file is None:
        raise ValueError("file_transfer event should have attached file")


_event_checkers = {
    enums.SystemEvents.chat_created: _check_common_system_event,
    enums.SystemEvents.added_to_chat: _check_common_system_event,
    enums.SystemEvents.file_transfer: _check_file_transfer_event,
}
