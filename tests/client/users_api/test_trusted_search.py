from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from pybotx.client.users_api.search_user_by_email import (
    BotXAPISearchUserByEmailRequestPayload,
)
from pybotx.client.users_api.search_user_by_emails import (
    BotXAPISearchUserByEmailsRequestPayload,
)
from pybotx.client.users_api.search_user_by_huid import (
    BotXAPISearchUserByHUIDRequestPayload,
)
from pybotx.client.users_api.search_user_by_login import (
    BotXAPISearchUserByLoginRequestPayload,
)
from pybotx.client.users_api.search_user_by_other_id import (
    BotXAPISearchUserByOtherIdRequestPayload,
)


@pytest.mark.parametrize(
    "payload_factory",
    [
        lambda: BotXAPISearchUserByEmailRequestPayload.from_domain(
            "user@example.com", partial_response=True
        ),
        lambda: BotXAPISearchUserByEmailsRequestPayload.from_domain(
            ["user@example.com"], partial_response=True
        ),
        lambda: BotXAPISearchUserByHUIDRequestPayload.from_domain(
            UUID("00000000-0000-0000-0000-000000000001"),
            partial_response=True,
        ),
        lambda: BotXAPISearchUserByLoginRequestPayload.from_domain(
            "user", "example.com", partial_response=True
        ),
        lambda: BotXAPISearchUserByOtherIdRequestPayload.from_domain(
            "external-id", partial_response=True
        ),
    ],
)
def test__partial_response_without_trusted_search__raises(
    payload_factory: Callable[[], Any],
) -> None:
    with pytest.raises(
        ValueError,
        match="`partial_response=True` requires `trusts_search=True`",
    ):
        payload_factory()


@pytest.mark.parametrize(
    "payload_factory",
    [
        lambda: BotXAPISearchUserByEmailRequestPayload.from_domain(
            "user@example.com", trusts_search=True
        ),
        lambda: BotXAPISearchUserByEmailsRequestPayload.from_domain(
            ["user@example.com"], trusts_search=True
        ),
        lambda: BotXAPISearchUserByHUIDRequestPayload.from_domain(
            UUID("00000000-0000-0000-0000-000000000001"), trusts_search=True
        ),
        lambda: BotXAPISearchUserByLoginRequestPayload.from_domain(
            "user", "example.com", trusts_search=True
        ),
        lambda: BotXAPISearchUserByOtherIdRequestPayload.from_domain(
            "external-id", trusts_search=True
        ),
    ],
)
def test__trusted_search_without_partial_response__serializes_only_enabled_flag(
    payload_factory: Callable[[], Any],
) -> None:
    payload = payload_factory().jsonable_dict()

    assert payload["trusts_search"] is True
    assert "partial_response" not in payload
