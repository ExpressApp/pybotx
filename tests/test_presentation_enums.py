import pytest

from pybotx.domain.models.enums import (
    AttachmentTypes,
    ChatTypes,
    ClientPlatforms,
    MentionTypes,
    SyncSourceTypes,
    UserKinds,
)
from pybotx.presentation.contracts.enums import (
    APIAttachmentTypes,
    APIChatTypes,
    APISyncSourceTypes,
    APIUserKinds,
    BotAPIClientPlatforms,
    BotAPIMentionTypes,
    convert_attachment_type_from_domain,
    convert_attachment_type_to_domain,
    convert_chat_type_from_domain,
    convert_chat_type_to_domain,
    convert_client_platform_to_domain,
    convert_mention_type_from_domain,
    convert_sync_source_type_to_domain,
    convert_user_kind_to_domain,
)


@pytest.mark.parametrize(
    "platform, expected",
    [
        (BotAPIClientPlatforms.WEB, ClientPlatforms.WEB),
        (BotAPIClientPlatforms.ANDROID, ClientPlatforms.ANDROID),
        (BotAPIClientPlatforms.IOS, ClientPlatforms.IOS),
        (BotAPIClientPlatforms.DESKTOP, ClientPlatforms.DESKTOP),
        (BotAPIClientPlatforms.AURORA, ClientPlatforms.AURORA),
    ],
)
def test__convert_client_platform_to_domain(platform, expected) -> None:
    assert convert_client_platform_to_domain(platform) == expected


@pytest.mark.parametrize(
    "mention, expected",
    [
        (MentionTypes.USER, BotAPIMentionTypes.USER),
        (MentionTypes.CONTACT, BotAPIMentionTypes.CONTACT),
        (MentionTypes.CHAT, BotAPIMentionTypes.CHAT),
        (MentionTypes.CHANNEL, BotAPIMentionTypes.CHANNEL),
        (MentionTypes.ALL, BotAPIMentionTypes.ALL),
    ],
)
def test__convert_mention_type_from_domain(mention, expected) -> None:
    assert convert_mention_type_from_domain(mention) == expected


@pytest.mark.parametrize(
    "attachment, expected",
    [
        (APIAttachmentTypes.IMAGE, AttachmentTypes.IMAGE),
        (APIAttachmentTypes.VIDEO, AttachmentTypes.VIDEO),
        (APIAttachmentTypes.DOCUMENT, AttachmentTypes.DOCUMENT),
        (APIAttachmentTypes.VOICE, AttachmentTypes.VOICE),
        (APIAttachmentTypes.LOCATION, AttachmentTypes.LOCATION),
        (APIAttachmentTypes.CONTACT, AttachmentTypes.CONTACT),
        (APIAttachmentTypes.LINK, AttachmentTypes.LINK),
        (APIAttachmentTypes.STICKER, AttachmentTypes.STICKER),
    ],
)
def test__convert_attachment_type_to_domain(attachment, expected) -> None:
    assert convert_attachment_type_to_domain(attachment) == expected


@pytest.mark.parametrize(
    "attachment, expected",
    [
        (AttachmentTypes.IMAGE, APIAttachmentTypes.IMAGE),
        (AttachmentTypes.VIDEO, APIAttachmentTypes.VIDEO),
        (AttachmentTypes.DOCUMENT, APIAttachmentTypes.DOCUMENT),
        (AttachmentTypes.VOICE, APIAttachmentTypes.VOICE),
        (AttachmentTypes.LOCATION, APIAttachmentTypes.LOCATION),
        (AttachmentTypes.CONTACT, APIAttachmentTypes.CONTACT),
        (AttachmentTypes.LINK, APIAttachmentTypes.LINK),
    ],
)
def test__convert_attachment_type_from_domain(attachment, expected) -> None:
    assert convert_attachment_type_from_domain(attachment) == expected


@pytest.mark.parametrize(
    "chat_type, expected",
    [
        (ChatTypes.PERSONAL_CHAT, APIChatTypes.CHAT),
        (ChatTypes.GROUP_CHAT, APIChatTypes.GROUP_CHAT),
        (ChatTypes.CHANNEL, APIChatTypes.CHANNEL),
        (ChatTypes.THREAD, APIChatTypes.THREAD),
    ],
)
def test__convert_chat_type_from_domain(chat_type, expected) -> None:
    assert convert_chat_type_from_domain(chat_type) == expected


@pytest.mark.parametrize(
    "chat_type, expected",
    [
        (APIChatTypes.CHAT, ChatTypes.PERSONAL_CHAT),
        (APIChatTypes.NOTES, ChatTypes.PERSONAL_CHAT),
        (APIChatTypes.GROUP_CHAT, ChatTypes.GROUP_CHAT),
        (APIChatTypes.CHANNEL, ChatTypes.CHANNEL),
        (APIChatTypes.THREAD, ChatTypes.THREAD),
    ],
)
def test__convert_chat_type_to_domain(chat_type, expected) -> None:
    assert convert_chat_type_to_domain(chat_type) == expected


def test__convert_chat_type_to_domain__unsupported_str() -> None:
    assert convert_chat_type_to_domain("unknown") == "UNSUPPORTED"


@pytest.mark.parametrize(
    "user_kind, expected",
    [
        (APIUserKinds.USER, UserKinds.RTS_USER),
        (APIUserKinds.CTS_USER, UserKinds.CTS_USER),
        (APIUserKinds.BOTX, UserKinds.BOT),
        (APIUserKinds.UNREGISTERED, UserKinds.UNREGISTERED),
        (APIUserKinds.GUEST, UserKinds.GUEST),
    ],
)
def test__convert_user_kind_to_domain(user_kind, expected) -> None:
    assert convert_user_kind_to_domain(user_kind) == expected


@pytest.mark.parametrize(
    "sync_type, expected",
    [
        (APISyncSourceTypes.AD, SyncSourceTypes.AD),
        (APISyncSourceTypes.ADMIN, SyncSourceTypes.ADMIN),
        (APISyncSourceTypes.EMAIL, SyncSourceTypes.EMAIL),
        (APISyncSourceTypes.OPENID, SyncSourceTypes.OPENID),
        (APISyncSourceTypes.BOTX, SyncSourceTypes.BOTX),
    ],
)
def test__convert_sync_source_type_to_domain(sync_type, expected) -> None:
    assert convert_sync_source_type_to_domain(sync_type) == expected


def test__convert_sync_source_type_to_domain__unsupported_str() -> None:
    assert convert_sync_source_type_to_domain("unknown") == "UNSUPPORTED"
