import uuid
from typing import Any, Dict, List, Optional

from factory.base import DictFactory  # type: ignore
from factory.declarations import SubFactory  # type: ignore


class DeviceMetaFactory(DictFactory):  # type: ignore[misc]

    permissions: Optional[str] = None
    pushes: Optional[str] = None
    timezone: Optional[str] = None


class FromFactory(DictFactory):  # type: ignore[misc]
    user_huid: Optional[str] = None
    group_chat_id: str = "8dada2c8-67a6-4434-9dec-570d244e78ee"
    ad_login: Optional[str] = None
    ad_domain: Optional[str] = None
    username: Optional[str] = None
    chat_type: str = "group_chat"
    manufacturer: Optional[str] = None
    device: Optional[str] = None
    device_software: Optional[str] = None
    device_meta: Dict[str, Any] = SubFactory(DeviceMetaFactory)  # noqa: F821
    platform: Optional[str] = None
    platform_package_id: Optional[str] = None
    is_admin: Optional[bool] = None
    is_creator: Optional[bool] = None
    app_version: Optional[str] = None
    locale: str = "en"
    host: str = "cts.ccteam.ru"


class CommandDataFactory(DictFactory):  # type: ignore[misc]

    added_members: List[str] = [uuid.uuid4().hex, uuid.uuid4().hex]


class CommandFactory(DictFactory):  # type: ignore[misc]

    body: str = "system:user_joined_to_chat"
    command_type: str = "system"
    data: Dict[str, Any] = SubFactory(CommandDataFactory)  # noqa: F821
    metadata: Dict[str, Any] = {}


class BotAPIJoinToChatFactory(DictFactory):  # type: ignore[misc]

    sync_id: str = uuid.uuid4().hex
    command: Dict[str, Any] = SubFactory(CommandFactory)  # noqa: F821
    async_files: List[str] = []
    attachments: List[str] = []
    entities: List[str] = []
    from_: Dict[str, Any] = SubFactory(
        FromFactory,
    )  # noqa: F821
    bot_id: str = uuid.uuid4().hex
    proto_version: int = 4
    source_sync_id: Optional[str] = None

    class Meta:
        rename = {"from_": "from"}


class ConferenceChangedDataFactory(DictFactory):  # type: ignore[misc]

    access_code = None
    actor = None
    added_users = ["5c053f2a-0bdf-4ab1-9bc9-256fee9db7ba"]
    admins = ["b394c9a0-7636-4316-beb1-d5a92038501c"]
    call_id = "eb6bf5d6-100c-42d8-9efd-549d5a70e38c"
    deleted_users = ["440d82da-2046-43df-8dae-598336906090"]
    end_at = "2025-04-15T12:00:39.634000Z"
    link = "https://xlnk.ms/join/room/NGUyODE1MzAtYTcyNy01MzQ4LTkxNjktNzkzO1N2UtNWI4OS04NmM0LTFmY2FkMzkwNDE2OTpjMzgwNjVhNy1jOTc5LTU0MzgtYmNlYS05NTNhNjNhZDEwNzQ="
    link_id = "b5dbd3ae-ab4a-42b9-b17d-6714b9e82bdb"
    link_type = "public"
    members = [
        "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "b394c9a0-7636-4316-beb1-d5a92038501c",
        "5c053f2a-0bdf-4ab1-9bc9-256fee9db7ba",
    ]
    name = "conference name"
    operation = "change_conference_info"
    sip_number = 12345678
    start_at = "2025-04-15T11:00:39.634000Z"
