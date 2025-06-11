from http import HTTPStatus
from typing import Any, Dict, List
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, HandlerCollector, SyncSourceTypes, UserFromCSV, lifespan_wrapper
from pybotx.client.exceptions.users import NoUserKindSelectedError
from pybotx.models.bot_account import BotAccountWithSecret

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


def assert_csv_user_consist_csv_data(  # noqa:  WPS218
    csv_user: UserFromCSV,
    original_row: Dict[str, str],
) -> None:
    """Verify that a UserFromCSV object contains the correct data from a CSV row.

    This function performs assertions to check that all fields in the UserFromCSV object
    match the corresponding values in the original CSV row dictionary.

    Args:
        csv_user: A UserFromCSV object created from CSV data
        original_row: A dictionary containing the original CSV row data
    """
    assert csv_user.username == original_row["Name"]
    assert csv_user.ad_domain == original_row["Domain"]
    assert csv_user.email == original_row["AD E-mail"]
    assert str(csv_user.active).lower() == original_row["Active"]
    assert str(csv_user.huid) == original_row["HUID"]
    assert csv_user.user_kind.value.lower() == original_row["Kind"]
    if isinstance(csv_user.sync_source, SyncSourceTypes):
        assert str(csv_user.sync_source.value).lower() == original_row["Sync source"]
    else:
        assert str(csv_user.sync_source).lower() == original_row["Sync source"]

    if original_row["Manager HUID"]:
        assert str(csv_user.manager_huid) == original_row["Manager HUID"]
    else:
        assert csv_user.manager_huid is None

    string_fields = [
        "AD Login",
        "User DN",
        "Company",
        "Department",
        "Position",
        "Manager",
        "Manager HUID",
        "Manager DN",
        "Personnel number",
        "Description",
        "IP phone",
        "Other IP phone",
        "Phone",
        "Other phone",
        "Avatar",
        "Office",
        "Avatar preview",
    ]

    for string_field_name in string_fields:
        object_field_name = string_field_name.lower().replace(" ", "_")
        if original_row[string_field_name]:
            assert original_row[string_field_name] == getattr(
                csv_user,
                object_field_name,
            )
        else:
            assert getattr(csv_user, object_field_name) is None


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
    csv_users_from_api: List[Dict[str, Any]],
    users_csv_response: httpx.Response,
) -> None:
    """Test successful retrieval of users as CSV.

    This test verifies that the users_as_csv method correctly retrieves users
    in CSV format from the BotX API and converts them to UserFromCSV objects.
    """
    endpoint = respx_mock.get(
        url=f"https://{host}/api/v3/botx/users/users_as_csv",
        headers={"Authorization": "Bearer token"},
        params={"cts_user": True, "unregistered": True, "botx": False},
    ).mock(return_value=users_csv_response)

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])
    users_from_csv = []

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        async with bot.users_as_csv(bot_id=bot_id) as users:
            async for user in users:
                users_from_csv.append(user)

    # - Assert -
    assert endpoint.called

    for generated_user, original_user in zip(users_from_csv, csv_users_from_api):
        assert_csv_user_consist_csv_data(generated_user, original_user)
