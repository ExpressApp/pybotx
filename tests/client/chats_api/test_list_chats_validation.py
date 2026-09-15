from datetime import datetime
from uuid import UUID

from pybotx.client.chats_api.list_chats import (
    BotXAPIListChatResponsePayload,
    BotXAPIListChatResult,
)
from pybotx.models.enums import APIChatTypes


class MockValidationInfo:
    """Mock class for ValidationInfo protocol."""

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name


def test_validate_result_non_dict() -> None:
    # - Arrange -
    # Create a non-dict result
    non_dict_result = BotXAPIListChatResult(
        group_chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        chat_type=APIChatTypes.GROUP_CHAT,
        name="Test Chat",
        description="Test Description",
        members=[UUID("154af49e-5e18-4dca-ad73-4f96b6de63fa")],
        inserted_at=datetime.now(),
        updated_at=datetime.now(),
        shared_history=True,
    )

    # - Act -
    # Call validate_result with a list containing a non-dict item
    result = BotXAPIListChatResponsePayload.validate_result(
        [non_dict_result],
        MockValidationInfo(field_name="result"),
    )

    # - Assert -
    # Verify that the non-dict item is included in the result
    assert non_dict_result in result
