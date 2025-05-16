import csv
from http import HTTPStatus
from io import StringIO
from typing import Any, Dict, List
from uuid import UUID

import httpx
import pytest

from pybotx import UserFromSearch, UserKinds
from tests.client.users_api.convert_to_datetime import convert_to_datetime
from tests.client.users_api.factories import CsvUserResponseValues


@pytest.fixture()
def user_from_search_with_data_json() -> Dict[str, Any]:
    return {
        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
        "ad_login": "ad_user_login",
        "ad_domain": "cts.com",
        "name": "Bob",
        "company": "Bobs Co",
        "company_position": "Director",
        "department": "Owners",
        "emails": ["ad_user@cts.com"],
        "user_kind": "cts_user",
        "active": True,
        "created_at": "2023-03-26T14:36:08.740618Z",
        "cts_id": "e0140f4c-4af2-5a2e-9ad1-5f37fceafbaf",
        "description": "Director in Owners dep",
        "ip_phone": "1271020",
        "manager": "Alice",
        "office": "SUN",
        "other_ip_phone": "32593",
        "other_phone": "1254218",
        "public_name": "Bobby",
        "rts_id": "f46440a4-d930-58d4-b3f5-8110ab846ee3",
        "updated_at": "2023-03-26T14:36:08.740618Z",
    }


@pytest.fixture
def user_from_search_with_data() -> UserFromSearch:
    return UserFromSearch(
        huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        ad_login="ad_user_login",
        ad_domain="cts.com",
        username="Bob",
        company="Bobs Co",
        company_position="Director",
        department="Owners",
        emails=["ad_user@cts.com"],
        other_id=None,
        user_kind=UserKinds.CTS_USER,
        active=True,
        created_at=convert_to_datetime("2023-03-26T14:36:08.740618Z"),
        cts_id=UUID("e0140f4c-4af2-5a2e-9ad1-5f37fceafbaf"),
        description="Director in Owners dep",
        ip_phone="1271020",
        manager="Alice",
        office="SUN",
        other_ip_phone="32593",
        other_phone="1254218",
        public_name="Bobby",
        rts_id=UUID("f46440a4-d930-58d4-b3f5-8110ab846ee3"),
        updated_at=convert_to_datetime("2023-03-26T14:36:08.740618Z"),
    )


@pytest.fixture
def user_from_search_without_data_json() -> Dict[str, Any]:
    return {
        "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
        "ad_login": "ad_user_login",
        "ad_domain": "cts.com",
        "name": "Bob",
        "company": "Bobs Co",
        "company_position": "Director",
        "department": "Owners",
        "emails": ["ad_user@cts.com"],
        "user_kind": "cts_user",
        "active": None,
        "created_at": None,
        "cts_id": None,
        "description": None,
        "ip_phone": None,
        "manager": None,
        "office": None,
        "other_ip_phone": None,
        "other_phone": None,
        "public_name": None,
        "rts_id": None,
        "updated_at": None,
    }


@pytest.fixture
def user_from_search_without_data() -> UserFromSearch:
    return UserFromSearch(
        huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        ad_login="ad_user_login",
        ad_domain="cts.com",
        username="Bob",
        company="Bobs Co",
        company_position="Director",
        department="Owners",
        emails=["ad_user@cts.com"],
        other_id=None,
        user_kind=UserKinds.CTS_USER,
        active=None,
        created_at=None,
        cts_id=None,
        description=None,
        ip_phone=None,
        manager=None,
        office=None,
        other_ip_phone=None,
        other_phone=None,
        public_name=None,
        rts_id=None,
        updated_at=None,
    )


@pytest.fixture
def csv_users_from_api() -> list[dict[str, str]]:
    """Generate a list of user dictionaries for CSV testing.

    This fixture creates a list of dictionaries representing user data as it would
    appear in a CSV response from the BotX API.

    return: A list of dictionaries where each dictionary represents
        a user with CSV column names as keys and corresponding values as strings.
    """
    return [
        CsvUserResponseValues(
            Manager_DN=f"manager_dn_{index}",
            User_DN=f"user_dn_{index}",
        )
        for index in range(2)
    ]


@pytest.fixture
def users_csv_response(csv_users_from_api: List[Dict[str, str]]) -> httpx.Response:
    """
    Create a mock HTTP response with CSV user data.

    This fixture takes the user data from ``csv_users_from_api`` and converts it into
    CSV format. It then returns an ``httpx.Response`` object containing the CSV content.

    :param: A list of dictionaries containing user data for CSV conversion.

    :return: An HTTP response object with status code 200 (OK) and CSV-formatted
        user data as content.
    """

    csv_columns = [
        "HUID",
        "AD Login",
        "Domain",
        "AD E-mail",
        "Name",
        "Sync source",
        "Active",
        "Kind",
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

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=csv_columns)
    writer.writeheader()

    for user in csv_users_from_api:
        ordered_row_values = {
            column_name: user[column_name] for column_name in csv_columns
        }
        writer.writerow(ordered_row_values)

    return httpx.Response(
        status_code=HTTPStatus.OK,
        content=output.getvalue().encode("utf-8"),
    )
