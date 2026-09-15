from datetime import datetime
from uuid import UUID

from factory.base import Factory, DictFactory
from factory.declarations import LazyFunction, SubFactory

from pybotx import ChatInfo, ChatInfoMember, ChatTypes, UserKinds


class ChatInfoMemberFactory(Factory[ChatInfoMember]):
    class Meta:
        model = ChatInfoMember

    is_admin = False
    huid = LazyFunction(lambda: UUID("705df263-6bfd-536a-9d51-13524afaab5c"))  # type: ignore[no-untyped-call]
    kind = UserKinds.BOT


class ChatInfoFactory(Factory[ChatInfo]):
    class Meta:
        model = ChatInfo

    chat_type = ChatTypes.GROUP_CHAT
    creator_id = LazyFunction(lambda: UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"))  # type: ignore[no-untyped-call]
    description = "Desc"
    chat_id = LazyFunction(lambda: UUID("740cf331-d833-5250-b5a5-5b5cbc697ff5"))  # type: ignore[no-untyped-call]
    created_at = LazyFunction(
        lambda: datetime.fromisoformat("2019-08-29T11:22:48.358586Z")
    )  # type: ignore[no-untyped-call]
    members = LazyFunction(
        lambda: [
            ChatInfoMemberFactory(  # type: ignore[no-untyped-call]
                is_admin=True,
                huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                kind=UserKinds.RTS_USER,
            ),
            ChatInfoMemberFactory(),  # type: ignore[no-untyped-call]
        ]
    )
    name = "Chat Name"
    shared_history = False


class APIChatMemberFactory(DictFactory):
    admin = False
    user_huid = "705df263-6bfd-536a-9d51-13524afaab5c"
    user_kind = "botx"


class APIPersonalChatResultFactory(DictFactory):
    chat_type = "group_chat"
    creator = "6fafda2c-6505-57a5-a088-25ea5d1d0364"
    description = "Desc"
    group_chat_id = "740cf331-d833-5250-b5a5-5b5cbc697ff5"
    inserted_at = "2019-08-29T11:22:48.358586Z"
    members = LazyFunction(
        lambda: [
            APIChatMemberFactory(  # type: ignore[no-untyped-call]
                admin=True,
                user_huid="6fafda2c-6505-57a5-a088-25ea5d1d0364",
                user_kind="user",
            ),
            APIChatMemberFactory(),  # type: ignore[no-untyped-call]
        ]
    )
    name = "Chat Name"
    shared_history = False


class APIPersonalChatResponseFactory(DictFactory):
    status = "ok"
    result = SubFactory(APIPersonalChatResultFactory)  # type: ignore[no-untyped-call]
