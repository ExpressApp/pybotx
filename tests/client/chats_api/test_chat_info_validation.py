
from uuid import UUID

from pybotx.client.chats_api.chat_info import (
    BotXAPIChatInfoResult,
    BotXAPIChatInfoMember,
)
from pybotx.models.enums import APIUserKinds


class MockValidationInfo:
    """Mock class for ValidationInfo protocol."""

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name


def test_validate_members_non_dict() -> None:
    # - Arrange -
    # Create a non-dict member
    non_dict_member = BotXAPIChatInfoMember(
        admin=True,
        user_huid=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        user_kind=APIUserKinds.BOTX,
    )

    # - Act -
    # Call validate_members with a list containing a non-dict item
    result = BotXAPIChatInfoResult.validate_members([non_dict_member], MockValidationInfo(field_name="members"))  # type: ignore[call-arg, arg-type]

    # - Assert -
    # Verify that the non-dict item is included in the result
    assert non_dict_member in result
