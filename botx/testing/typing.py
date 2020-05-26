"""Typings for test client and mocks."""

from typing import Union

from botx.clients.methods.v2.bots.token import Token
from botx.clients.methods.v3.chats.add_user import AddUser
from botx.clients.methods.v3.chats.create import Create
from botx.clients.methods.v3.chats.info import Info
from botx.clients.methods.v3.chats.remove_user import RemoveUser
from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.clients.methods.v3.chats.stealth_set import StealthSet
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin

APIMessage = Union[
    CommandResult, Notification, NotificationDirect, EditEvent,
]

APIRequest = Union[
    # V2
    # bots
    Token,
    # V3
    # chats
    AddUser,
    Info,
    RemoveUser,
    StealthDisable,
    StealthSet,
    Create,
    # command
    CommandResult,
    # notification
    Notification,
    NotificationDirect,
    # events
    EditEvent,
    # users
    ByHUID,
    ByEmail,
    ByLogin,
]
