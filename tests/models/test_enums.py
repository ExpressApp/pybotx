import pytest
from unittest.mock import Mock

from pybotx.models.enums import (
    APIChatTypes,
    BotAPIClientNetworkContours,
    ClientNetworkContours,
    ChatTypes,
    convert_chat_type_from_domain,
    convert_chat_type_to_domain,
    convert_client_network_contour_to_domain,
)


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


def test__convert_chat_type_to_domain__notes_maps_to_personal_chat() -> None:
    assert convert_chat_type_to_domain(APIChatTypes.NOTES) == ChatTypes.PERSONAL_CHAT
    assert convert_chat_type_to_domain("notes") == ChatTypes.PERSONAL_CHAT


def test__convert_client_network_contour_to_domain__successful_conversion() -> None:
    assert (
        convert_client_network_contour_to_domain(BotAPIClientNetworkContours.INTERNAL)
        == ClientNetworkContours.INTERNAL
    )
    assert (
        convert_client_network_contour_to_domain(BotAPIClientNetworkContours.EXTERNAL)
        == ClientNetworkContours.EXTERNAL
    )


def test__convert_client_network_contour_to_domain__unsupported_contour_raises_error() -> (
    None
):
    unsupported_client_network_contour = Mock(spec=BotAPIClientNetworkContours)

    with pytest.raises(NotImplementedError, match="Unsupported client network contour"):
        convert_client_network_contour_to_domain(unsupported_client_network_contour)
