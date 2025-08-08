import uuid
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


import pybotx.client.chats_api.personal_chat as personal_chat_module
from pybotx.client.chats_api.personal_chat import (
    BotXAPIPersonalChatRequestPayload,
    BotXAPIPersonalChatResult,
    BotXAPIPersonalChatMember,
    BotXAPIPersonalChatResponsePayload,
)
from pybotx.models.enums import APIUserKinds, APIChatTypes


def test_request_payload_as_query_params_returns_string_uuid() -> None:
    """Проверяем, что as_query_params сериализует UUID в строку."""
    huid = uuid.uuid4()
    payload = BotXAPIPersonalChatRequestPayload.from_domain(huid)
    params = payload.as_query_params()
    assert isinstance(params["user_huid"], str)
    assert params["user_huid"] == str(huid)


def test_parse_members_various_types() -> None:
    """Проверяем все ветки _parse_members: dict → модель, готовый экземпляр и неизвестный тип."""
    uid = uuid.uuid4()

    dict_valid: Dict[str, Any] = {
        "admin": True,
        "user_huid": str(uid),
        "user_kind": APIUserKinds.USER.value,
    }
    member_instance = BotXAPIPersonalChatMember(
        admin=False, user_huid=uid, user_kind=APIUserKinds.USER
    )
    unknown_item: Any = 12345

    parsed = BotXAPIPersonalChatResult._parse_members(
        [dict_valid, member_instance, unknown_item]
    )

    assert len(parsed) == 2
    assert isinstance(parsed[0], BotXAPIPersonalChatMember)
    assert parsed[1] is member_instance


def test_to_domain_handles_conversion_error(monkeypatch: Any) -> None:
    """Если convert_user_kind_to_domain падает — to_domain игнорирует участника."""
    uid = UUID("00000000-0000-0000-0000-000000000001")
    member = BotXAPIPersonalChatMember(
        admin=True, user_huid=uid, user_kind=APIUserKinds.USER
    )
    result = BotXAPIPersonalChatResult(
        chat_type=APIChatTypes.CHAT,
        creator=None,
        description=None,
        group_chat_id=uid,
        inserted_at=datetime.utcnow(),
        members=[member],
        name="test",
        shared_history=False,
    )
    payload = BotXAPIPersonalChatResponsePayload(status="ok", result=result)

    def fake_convert(kind: Any) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        personal_chat_module,
        "convert_user_kind_to_domain",
        fake_convert,
    )

    chat_info = payload.to_domain()
    assert chat_info.members == []
    assert chat_info.chat_id == uid


def test_to_domain_skips_unsupported_member_type() -> None:
    """Если в result.members передан не-BotXAPIPersonalChatMember — пропускаем."""
    uid = UUID("00000000-0000-0000-0000-000000000002")
    unsupported: Dict[str, Any] = {"foo": "bar"}
    result = BotXAPIPersonalChatResult(
        chat_type=APIChatTypes.CHAT,
        creator=None,
        description=None,
        group_chat_id=uid,
        inserted_at=datetime.utcnow(),
        members=[unsupported],
        name="test",
        shared_history=False,
    )
    payload = BotXAPIPersonalChatResponsePayload(status="ok", result=result)

    chat_info = payload.to_domain()
    assert chat_info.members == []
    assert chat_info.chat_id == uid
