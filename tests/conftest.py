import pytest


@pytest.fixture
def test_command_data():
    return {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {"body": "/cmd #6", "data": {}},
        "file": {
            "data": "data:image/png;base64,eDnXAc1FEUB0VFEFctII3lRlRBcetROeFfduPmXxE/8=",
            "file_name": "card.png",
        },
        "from": {
            "user_huid": "ab103983-6001-44e9-889e-d55feb295494",
            "group_chat_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
            "ad_login": "example_login",
            "ad_domain": "example.com",
            "username": "Bob",
            "chat_type": "group_chat",
            "host": "cts.ccteam.ru",
        },
        "bot_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
    }
