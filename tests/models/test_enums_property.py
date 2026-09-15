from hypothesis import given, strategies as st

import pytest

from pybotx.models.enums import (
    APIAttachmentTypes,
    APIChatTypes,
    APIUserKinds,
    APISyncSourceTypes,
    AttachmentTypes,
    BotAPIClientPlatforms,
    BotAPIMentionTypes,
    BotAPIConferenceLinkTypes,
    ChatTypes,
    ClientPlatforms,
    ConferenceLinkTypes,
    MentionTypes,
    SyncSourceTypes,
    UserKinds,
    convert_attachment_type_from_domain,
    convert_attachment_type_to_domain,
    convert_chat_type_from_domain,
    convert_chat_type_to_domain,
    convert_client_platform_to_domain,
    convert_conference_link_type_to_domain,
    convert_mention_type_from_domain,
    convert_sync_source_type_to_domain,
    convert_user_kind_to_domain,
)

API_CHAT_VALUES = [chat_type.value for chat_type in APIChatTypes]
API_SYNC_SOURCE_VALUES = [sync_type.value for sync_type in APISyncSourceTypes]


@given(st.sampled_from(list(ChatTypes)))
def test__convert_chat_type_roundtrip__property(chat_type: ChatTypes) -> None:
    api_type = convert_chat_type_from_domain(chat_type)
    assert convert_chat_type_to_domain(api_type) == chat_type


@given(st.sampled_from(list(APIChatTypes)))
def test__convert_chat_type_to_domain__accepts_api_enum(
    api_type: APIChatTypes,
) -> None:
    assert convert_chat_type_to_domain(api_type) in ChatTypes


@given(st.sampled_from(API_CHAT_VALUES))
def test__convert_chat_type_to_domain__accepts_api_string(
    api_value: str,
) -> None:
    assert convert_chat_type_to_domain(api_value) in ChatTypes


@given(st.text(min_size=1).filter(lambda value: value not in API_CHAT_VALUES))
def test__convert_chat_type_to_domain__unknown_strings_become_unsupported(
    api_value: str,
) -> None:
    assert convert_chat_type_to_domain(api_value) == "UNSUPPORTED"


@given(st.sampled_from(list(APIAttachmentTypes)))
def test__convert_attachment_type_to_domain__property(
    api_type: APIAttachmentTypes,
) -> None:
    domain_type = convert_attachment_type_to_domain(api_type)
    assert domain_type in AttachmentTypes
    if domain_type is AttachmentTypes.STICKER:
        with pytest.raises(NotImplementedError):
            convert_attachment_type_from_domain(domain_type)
    else:
        assert convert_attachment_type_from_domain(domain_type) == api_type


@given(st.sampled_from(list(AttachmentTypes)))
def test__convert_attachment_type_from_domain__property(
    domain_type: AttachmentTypes,
) -> None:
    if domain_type is AttachmentTypes.STICKER:
        with pytest.raises(NotImplementedError):
            convert_attachment_type_from_domain(domain_type)
    else:
        api_type = convert_attachment_type_from_domain(domain_type)
        assert convert_attachment_type_to_domain(api_type) == domain_type


@given(st.sampled_from(list(APIUserKinds)))
def test__convert_user_kind_to_domain__property(
    api_kind: APIUserKinds,
) -> None:
    assert convert_user_kind_to_domain(api_kind) in UserKinds


@given(st.sampled_from(list(BotAPIClientPlatforms)))
def test__convert_client_platform_to_domain__property(
    api_platform: BotAPIClientPlatforms,
) -> None:
    assert convert_client_platform_to_domain(api_platform) in ClientPlatforms


@given(st.sampled_from(list(MentionTypes)))
def test__convert_mention_type_from_domain__property(
    domain_mention: MentionTypes,
) -> None:
    assert convert_mention_type_from_domain(domain_mention) in BotAPIMentionTypes


@given(st.sampled_from(list(BotAPIConferenceLinkTypes)))
def test__convert_conference_link_type_to_domain__property(
    api_type: BotAPIConferenceLinkTypes,
) -> None:
    assert convert_conference_link_type_to_domain(api_type) in ConferenceLinkTypes


@given(st.sampled_from(list(APISyncSourceTypes)))
def test__convert_sync_source_type_to_domain__property(
    api_type: APISyncSourceTypes,
) -> None:
    assert convert_sync_source_type_to_domain(api_type) in SyncSourceTypes


@given(st.text(min_size=1))
def test__convert_sync_source_type_to_domain__unknown_strings_become_unsupported(
    api_value: str,
) -> None:
    if api_value not in API_SYNC_SOURCE_VALUES:
        assert convert_sync_source_type_to_domain(api_value) == "UNSUPPORTED"


@given(st.sampled_from(API_SYNC_SOURCE_VALUES))
def test__convert_sync_source_type_to_domain__accepts_api_string(
    api_value: str,
) -> None:
    assert convert_sync_source_type_to_domain(api_value) in SyncSourceTypes
