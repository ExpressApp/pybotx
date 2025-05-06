import uuid
from typing import Any, Dict, List, Optional

from factory.base import DictFactory
from factory.declarations import SubFactory


class DeviceMetaFactory(DictFactory):

    permissions: Optional[str] = None
    pushes: Optional[str] = None
    timezone: Optional[str] = None


class FromFactory(DictFactory):
    user_huid: Optional[str] = None
    group_chat_id: str = "8dada2c8-67a6-4434-9dec-570d244e78ee"
    ad_login: Optional[str] = None
    ad_domain: Optional[str] = None
    username: Optional[str] = None
    chat_type: str = "group_chat"
    manufacturer: Optional[str] = None
    device: Optional[str] = None
    device_software: Optional[str] = None
    device_meta: Dict[str, Any] = SubFactory(DeviceMetaFactory)  # type: ignore # noqa: F821
    platform: Optional[str] = None
    platform_package_id: Optional[str] = None
    is_admin: Optional[bool] = None
    is_creator: Optional[bool] = None
    app_version: Optional[str] = None
    locale: str = "en"
    host: str = "cts.ccteam.ru"


class CommandDataFactory(DictFactory):

    added_members: List[str] = [uuid.uuid4().hex, uuid.uuid4().hex]


class CommandFactory(DictFactory):

    body: str = "system:user_joined_to_chat"
    command_type: str = "system"
    data: Dict[str, Any] = SubFactory(CommandDataFactory)  # type: ignore # noqa: F821
    metadata: Dict[str, Any] = {}

    class Meta:
        model = dict


class BotAPIJoinToChatFactory(DictFactory):

    sync_id: str = uuid.uuid4().hex
    command: Dict[str, Any] = SubFactory(CommandFactory)  # type: ignore # noqa: F821
    async_files: List[str] = []
    attachments: List[str] = []
    entities: List[str] = []
    from_: Dict[str, Any] = SubFactory(
        FromFactory,
    )  # type: ignore # noqa: F821
    bot_id: str = uuid.uuid4().hex
    proto_version: int = 4
    source_sync_id: Optional[str] = None

    class Meta:
        rename = {"from_": "from"}
