"""Typings for test client and mocks."""

from typing import Union

from botx.models.requests import (
    AddRemoveUsersPayload,
    CommandResult,
    Notification,
    StealthDisablePayload,
    StealthEnablePayload,
    UpdatePayload,
)

APIMessage = Union[
    CommandResult, Notification, UpdatePayload,
]

APIRequest = Union[
    APIMessage, StealthDisablePayload, StealthEnablePayload, AddRemoveUsersPayload
]
