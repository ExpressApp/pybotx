from typing import Callable
from uuid import UUID, uuid4

import pytest

from botx.bot.models.commands.entities import Mention
from botx.bot.models.commands.enums import MentionTypes
from botx.bot.models.commands.mentions import MentionList


@pytest.fixture
def mention_factory() -> Callable[..., Mention]:
    def factory(
        mention_type: MentionTypes,
        huid: UUID,
        name: str,
    ) -> Mention:
        return Mention(
            type=mention_type,
            huid=huid,
            name=name,
        )

    return factory


def test__mentions_list_properties__filled(
    mention_factory: Callable[..., Mention],
) -> None:
    # - Arrange -
    contacts = [
        mention_factory(
            mention_type=MentionTypes.CONTACT,
            huid=uuid4(),
            name=str(name),
        )
        for name in range(2)
    ]
    chats = [
        mention_factory(
            mention_type=MentionTypes.CHAT,
            huid=uuid4(),
            name=str(name),
        )
        for name in range(2)
    ]
    channels = [
        mention_factory(
            mention_type=MentionTypes.CHANNEL,
            huid=uuid4(),
            name=str(name),
        )
        for name in range(2)
    ]
    users = [
        mention_factory(
            mention_type=MentionTypes.USER,
            huid=uuid4(),
            name=str(name),
        )
        for name in range(2)
    ]

    mentions = MentionList([*contacts, *chats, *channels, *users])

    # - Assert -
    assert mentions.contacts == contacts
    assert mentions.chats == chats
    assert mentions.channels == channels
    assert mentions.users == users
