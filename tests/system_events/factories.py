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
