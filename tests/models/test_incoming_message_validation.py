
from pybotx.models.message.incoming_message import BotAPIIncomingMessage
from pybotx.models.message.mentions import BotAPIMention


class MockValidationInfo:
    """Mock class for ValidationInfo protocol."""

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name


def test_validate_items_dict() -> None:
    # - Arrange -
    # Create a dict entity that will be processed
    entity_dict = {
        "type": "mention",
        "data": {
            "mention_type": "user",
            "mention_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "mention_data": None,
        },
    }

    # - Act -
    # Call validate_items with a list containing a dict item
    result = BotAPIIncomingMessage.validate_items(
        [entity_dict], MockValidationInfo(field_name="entities")  # type: ignore[call-arg, arg-type]
    )

    # - Assert -
    # Verify that the dict item was processed and added to the result list
    assert len(result) == 1
    assert isinstance(result[0], BotAPIMention)


def test_validate_items_non_dict() -> None:
    # - Arrange -
    # Create a non-dict entity
    non_dict_entity = "not a dict"

    # - Act -
    # Call validate_items with a list containing a non-dict item
    # The non-dict item will not be processed and not added to the result list
    result = BotAPIIncomingMessage.validate_items(
        [non_dict_entity], MockValidationInfo(field_name="entities")  # type: ignore[call-arg, arg-type]
    )

    # - Assert -
    # Verify that the non-dict item was not added to the result list
    assert len(result) == 0
