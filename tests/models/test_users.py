from uuid import UUID

from pybotx import UserFromSearch, UserKinds


def test__user_from_search__preserves_existing_positional_arguments() -> None:
    user = UserFromSearch(
        UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        "alice",
        "example.com",
        "Alice",
        None,
        None,
        None,
        ["alice@example.com"],
        None,
        UserKinds.CTS_USER,
        "https://example.com/avatar.png",
        "https://example.com/avatar-preview.png",
    )

    assert user.avatar == "https://example.com/avatar.png"
    assert user.avatar_preview == "https://example.com/avatar-preview.png"
    assert user.ad_groups == []
    assert user.openid_roles == []


def test__user_from_search__group_and_role_defaults_are_independent() -> None:
    first = UserFromSearch(
        huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        ad_login=None,
        ad_domain=None,
        username="Alice",
        company=None,
        company_position=None,
        department=None,
        emails=[],
        other_id=None,
        user_kind=UserKinds.CTS_USER,
    )
    second = UserFromSearch(
        huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        ad_login=None,
        ad_domain=None,
        username="Alice",
        company=None,
        company_position=None,
        department=None,
        emails=[],
        other_id=None,
        user_kind=UserKinds.CTS_USER,
    )

    first.ad_groups.append("employees")
    first.openid_roles.append("reader")

    assert second.ad_groups == []
    assert second.openid_roles == []
