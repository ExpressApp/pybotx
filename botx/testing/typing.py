"""Typings for test client and mocks."""

from typing import Union

from botx.clients.methods.v3.chats.add_user import AddUser
from botx.clients.methods.v3.chats.remove_user import RemoveUser
from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.clients.methods.v3.chats.stealth_set import StealthSet
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.methods.v3.notification.notification import Notification

APIMessage = Union[
    CommandResult, Notification, EditEvent,
]

APIRequest = Union[
    APIMessage, StealthDisable, StealthSet, AddUser, RemoveUser
]
