from io import BytesIO
from typing import Any, Dict
from uuid import UUID

from botx import File, Message
from botx.models.smartapps import SendingSmartAppEvent, SendingSmartAppNotification

pytest_plugins = ("tests.test_clients.fixtures", "tests.fixtures.smartapps")


def test_sending_smartapp_event(
    ref: UUID,
    smartapp_id: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_data: Dict[str, Any],
):
    sending_smartapp = SendingSmartAppEvent(
        ref=ref,
        smartapp_id=smartapp_id,
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
        data=smartapp_data,
    )

    assert sending_smartapp.ref == ref
    assert sending_smartapp.smartapp_id == smartapp_id
    assert sending_smartapp.smartapp_api_version == smartapp_api_version
    assert sending_smartapp.group_chat_id == group_chat_id
    assert sending_smartapp.data == smartapp_data


def test_sending_smartapp_notification(
    ref: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_counter: int,
):
    sending_smartapp = SendingSmartAppNotification(
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
        smartapp_counter=smartapp_counter,
    )

    assert sending_smartapp.smartapp_api_version == smartapp_api_version
    assert sending_smartapp.group_chat_id == group_chat_id
    assert sending_smartapp.smartapp_counter == smartapp_counter


def test_sending_smartapp_notification_from_message(
    message: Message,
    ref: UUID,
    smartapp_id: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_counter: int,
):
    message.incoming_message.command.data_dict[
        "smartapp_api_version"
    ] = smartapp_api_version
    message.incoming_message.command.data_dict["opts"] = {}
    message.group_chat_id = group_chat_id

    sending_smartapp = SendingSmartAppNotification.from_message(
        smartapp_counter=smartapp_counter,
        message=message,
    )

    assert sending_smartapp.smartapp_api_version == smartapp_api_version
    assert sending_smartapp.group_chat_id == group_chat_id
    assert sending_smartapp.smartapp_counter == smartapp_counter


def test_sending_smartapp_event_from_message(
    message: Message,
    ref: UUID,
    smartapp_id: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_data: Dict[str, Any],
):
    message.incoming_message.command.data_dict[
        "smartapp_api_version"
    ] = smartapp_api_version
    message.incoming_message.command.data_dict["opts"] = {}
    message.incoming_message.command.data_dict["smartapp_id"] = smartapp_id
    message.incoming_message.command.data_dict["ref"] = ref

    message.group_chat_id = group_chat_id

    sending_smartapp = SendingSmartAppEvent.from_message(
        data=smartapp_data,
        message=message,
    )

    assert sending_smartapp.smartapp_api_version == smartapp_api_version
    assert sending_smartapp.group_chat_id == group_chat_id
    assert sending_smartapp.data == smartapp_data


def test_sending_smartapp_event_add_botx_file(
    ref: UUID,
    smartapp_id: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_data: Dict[str, Any],
):
    sending_smartapp = SendingSmartAppEvent(
        ref=ref,
        smartapp_id=smartapp_id,
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
        data=smartapp_data,
    )

    file = File.from_string(b"data", filename="file.txt")
    sending_smartapp.add_file(file)

    assert sending_smartapp.files == [file]


def test_sending_smartapp_event_add_file(
    ref: UUID,
    smartapp_id: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_data: Dict[str, Any],
):
    sending_smartapp = SendingSmartAppEvent(
        ref=ref,
        smartapp_id=smartapp_id,
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
        data=smartapp_data,
    )

    file_data = b"data"
    file = File.from_string(file_data, filename="file.txt")
    sending_smartapp.add_file(BytesIO(file_data), file.file_name)

    assert sending_smartapp.files == [file]
