import pytest
from unittest.mock import Mock

from pybotx.models.enums import convert_chat_type_from_domain, ChatTypes, APIChatTypes


def test__convert_chat_type_from_domain__successful_conversion() -> None:
    """Test that convert_chat_type_from_domain successfully converts ChatTypes to APIChatTypes."""
    assert convert_chat_type_from_domain(ChatTypes.PERSONAL_CHAT) == APIChatTypes.CHAT
    assert (
        convert_chat_type_from_domain(ChatTypes.GROUP_CHAT) == APIChatTypes.GROUP_CHAT
    )
    assert convert_chat_type_from_domain(ChatTypes.CHANNEL) == APIChatTypes.CHANNEL
    assert convert_chat_type_from_domain(ChatTypes.THREAD) == APIChatTypes.THREAD


def test__convert_chat_type_from_domain__unsupported_chat_type_raises_error() -> None:
    """Test that convert_chat_type_from_domain raises NotImplementedError for unsupported chat types."""
    # Create a mock chat type that's not in the mapping
    unsupported_chat_type = Mock(spec=ChatTypes)

    # - Act & Assert -
    with pytest.raises(NotImplementedError, match="Unsupported chat type"):
        convert_chat_type_from_domain(unsupported_chat_type)
