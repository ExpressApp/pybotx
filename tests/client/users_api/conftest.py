from typing import Any, Dict
from uuid import UUID

import pytest

from pybotx import UserFromSearch, UserKinds
from tests.client.users_api.convert_to_datetime import convert_to_datetime


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
