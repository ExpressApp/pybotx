from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, HandlerCollector, lifespan_wrapper
from pybotx.client.exceptions.users import NoUserKindSelectedError
from pybotx.models.bot_account import BotAccountWithSecret
from pybotx.models.enums import SyncSourceTypes, UserKinds
from pybotx.models.users import UserFromCSV

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__users_as_csv__no_user_kind_selected_error(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    endpoint = respx_mock.get(
        url=f"https://{host}/api/v3/botx/users/users_as_csv",
        headers={"Authorization": "Bearer token"},
        params={"cts_user": False, "unregistered": False, "botx": False},
    ).mock(
        return_value=httpx.Response(
            status_code=HTTPStatus.BAD_REQUEST,
            json={
                "status": "error",
                "reason": "no_user_kind_selected",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    with pytest.raises(NoUserKindSelectedError) as exc:
        async with lifespan_wrapper(built_bot) as bot:
            async with bot.users_as_csv(  # noqa: WPS328
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
    bot_account: BotAccountWithSecret,
) -> None:
    endpoint = respx_mock.get(
        url=f"https://{host}/api/v3/botx/users/users_as_csv",
        headers={"Authorization": "Bearer token"},
        params={"cts_user": True, "unregistered": True, "botx": False},
    ).mock(
        return_value=httpx.Response(
            status_code=HTTPStatus.OK,
            content=(
                b"HUID,AD Login,Domain,AD E-mail,Name,Sync source,Active,Kind,Company,Department,Position\n"
                b"dbc8934f-d0d7-4a9e-89df-d45c137a851c,test_user_17,cts.example.com,,test_user_17,ad,true,cts_user,,,"
            ),
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])
    users_from_csv = []

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        async with bot.users_as_csv(bot_id=bot_id) as users:
            async for user in users:
                users_from_csv.append(user)

    # - Assert -
    assert endpoint.called
    assert users_from_csv == [
        UserFromCSV(
            huid=UUID("dbc8934f-d0d7-4a9e-89df-d45c137a851c"),
            ad_login="test_user_17",
            ad_domain="cts.example.com",
            username="test_user_17",
            sync_source=SyncSourceTypes.AD,
            active=True,
            user_kind=UserKinds.CTS_USER,
            email=None,
            company=None,
            department=None,
            position=None,
        ),
    ]
