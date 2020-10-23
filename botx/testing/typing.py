"""Typings for test client and mocks."""

from typing import Union

from botx.clients.methods.v2.bots import token
from botx.clients.methods.v3.chats import (
    add_admin_role,
    add_user,
    create,
    info,
    remove_user,
    stealth_disable,
    stealth_set,
)
from botx.clients.methods.v3.command import command_result
from botx.clients.methods.v3.events import edit_event
from botx.clients.methods.v3.notification import direct_notification, notification
from botx.clients.methods.v3.users import by_email, by_huid, by_login

APIMessage = Union[
    command_result.CommandResult,
    notification.Notification,
    direct_notification.NotificationDirect,
    edit_event.EditEvent,
]

APIRequest = Union[
    # V2
    # bots
    token.Token,
    # V3
    # chats
    add_admin_role.AddAdminRole,
    add_user.AddUser,
    info.Info,
    remove_user.RemoveUser,
    stealth_disable.StealthDisable,
    stealth_set.StealthSet,
    create.Create,
    # command
    command_result.CommandResult,
    # notification
    notification.Notification,
    direct_notification.NotificationDirect,
    # events
    edit_event.EditEvent,
    # users
    by_huid.ByHUID,
    by_email.ByEmail,
    by_login.ByLogin,
]
