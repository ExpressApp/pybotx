from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx.client.exceptions.users import NoUserKindSelectedError
from pybotx.models.enums import SyncSourceTypes, UserKinds
from pybotx.models.users import UserFromCSV
from tests.testkit import BotXRequest, assert_deep_equal, error_payload, mock_botx

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__users_as_csv__no_user_kind_selected_error(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    request = BotXRequest(
        method="GET",
        path="/api/v3/botx/users/users_as_csv",
        params={"cts_user": False, "unregistered": False, "botx": False},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        error_payload("no_user_kind_selected"),
        HTTPStatus.BAD_REQUEST,
    )

    # - Act -
    with pytest.raises(NoUserKindSelectedError) as exc:
        async with bot_factory() as bot:
            async with bot.users_as_csv(
                bot_id=bot_id,
                cts_user=False,
                unregistered=False,
                botx=False,
            ):
                pass

    # - Assert -
    assert endpoint.called
    assert "no_user_kind_selected" in str(exc.value)


async def test__users_as_csv__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    request = BotXRequest(
        method="GET",
        path="/api/v3/botx/users/users_as_csv",
        params={"cts_user": True, "unregistered": True, "botx": False},
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        response_json=None,
        status=HTTPStatus.OK,
        response_content=(
            b"HUID,AD Login,Domain,AD E-mail,Name,Sync source,Active,Kind,Company,Department,Position,Manager,Manager HUID,Personnel number,Description,IP phone,Other IP phone,Phone,Other phone,Avatar,Office,Avatar preview\n"
            b"dbc8934f-d0d7-4a9e-89df-d45c137a851c,test_user_17,cts.example.com,,test_user_17,ad,false,cts_user,Company,Department,Position,Manager John,13a6909c-bce1-4dbf-8359-efb7ef8e5b34,Some number,Description,IP phone,Other IP phone,Phone,Other_phone,Avatar,Office,Avatar_preview\n"
            b"13a6909c-bce1-4dbf-8359-efb7ef8e5b34,test_user_18,cts.example.com,,test_user_18,unsupported,true,cts_user,,,,,,,,,,,,,,"
        ),
    )
    users_from_csv = []

    # - Act -
    async with bot_factory() as bot:
        async with bot.users_as_csv(bot_id=bot_id) as users:
            async for user in users:
                users_from_csv.append(user)

    # - Assert -
    assert endpoint.called
    assert_deep_equal(
        users_from_csv,
        [
        UserFromCSV(
            huid=UUID("dbc8934f-d0d7-4a9e-89df-d45c137a851c"),
            ad_login="test_user_17",
            ad_domain="cts.example.com",
            username="test_user_17",
            sync_source=SyncSourceTypes.AD,
            active=False,
            user_kind=UserKinds.CTS_USER,
            email=None,
            company="Company",
            department="Department",
            position="Position",
            personnel_number="Some number",
            manager="Manager John",
            manager_huid=UUID("13a6909c-bce1-4dbf-8359-efb7ef8e5b34"),
            description="Description",
            ip_phone="IP phone",
            other_ip_phone="Other IP phone",
            phone="Phone",
            other_phone="Other_phone",
            avatar="Avatar",
            office="Office",
            avatar_preview="Avatar_preview",
        ),
        UserFromCSV(
            huid=UUID("13a6909c-bce1-4dbf-8359-efb7ef8e5b34"),
            ad_login="test_user_18",
            ad_domain="cts.example.com",
            username="test_user_18",
            sync_source="UNSUPPORTED",
            active=True,
            user_kind=UserKinds.CTS_USER,
            email=None,
            company=None,
            department=None,
            position=None,
            manager=None,
            manager_huid=None,
            personnel_number=None,
            description=None,
            ip_phone=None,
            other_ip_phone=None,
            phone=None,
            other_phone=None,
            avatar=None,
            office=None,
            avatar_preview=None,
        ),
        ],
    )
