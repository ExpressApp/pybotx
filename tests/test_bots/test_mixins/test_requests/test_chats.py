import uuid

import pytest

from botx import ChatTypes

pytestmark = pytest.mark.asyncio


async def test_creating_chat(client, message):
    await client.bot.create_chat(
        message.credentials,
        name="test",
        members=[message.user_huid],
        chat_type=ChatTypes.group_chat,
    )

    assert client.requests[0].name == "test"


async def test_enable_stealth_mode(bot, client, message):
    await bot.enable_stealth_mode(
        message.credentials,
        chat_id=message.group_chat_id,
        burn_in=60,
    )
    assert client.requests[0].burn_in == 60


async def test_disable_stealth_mode(bot, client, message):
    await bot.disable_stealth_mode(
        message.credentials,
        chat_id=message.group_chat_id,
    )
    assert client.requests[0].group_chat_id == message.group_chat_id


async def test_adding_user_to_chat(bot, client, message):
    users = [uuid.uuid4()]
    await bot.add_users(
        message.credentials,
        chat_id=message.group_chat_id,
        user_huids=users,
    )
    request = client.requests[0]
    assert request.group_chat_id == message.group_chat_id
    assert request.user_huids == users


async def test_remove_user(bot, client, message):
    users = [uuid.uuid4()]
    await bot.remove_users(
        message.credentials,
        chat_id=message.group_chat_id,
        user_huids=users,
    )
    request = client.requests[0]
    assert request.group_chat_id == message.group_chat_id
    assert request.user_huids == users


async def test_retrieving_chat_info(bot, client, message):
    chat_id = uuid.uuid4()
    info = await bot.get_chat_info(message.credentials, chat_id=chat_id)
    assert info.group_chat_id == chat_id


async def test_promoting_users_to_admins(bot, client, message):
    users = [uuid.uuid4()]
    await bot.add_admin_roles(
        message.credentials,
        chat_id=message.group_chat_id,
        user_huids=users,
    )
    request = client.requests[0]
    assert request.group_chat_id == message.group_chat_id
    assert request.user_huids == users
