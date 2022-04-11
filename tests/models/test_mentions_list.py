from uuid import uuid4

from pybotx import MentionBuilder, MentionList


def test__mentions_list_properties__filled() -> None:
    # - Arrange -
    contacts = [
        MentionBuilder.contact(
            entity_id=uuid4(),
            name=str(name),
        )
        for name in range(2)
    ]
    chats = [
        MentionBuilder.chat(
            entity_id=uuid4(),
            name=str(name),
        )
        for name in range(2)
    ]
    channels = [
        MentionBuilder.channel(
            entity_id=uuid4(),
            name=str(name),
        )
        for name in range(2)
    ]
    users = [
        MentionBuilder.user(
            entity_id=uuid4(),
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


def test__mentions_list_all_users_mentioned__filled() -> None:
    # - Arrange -
    user_mention = MentionBuilder.contact(
        entity_id=uuid4(),
    )
    all_mention = MentionBuilder.all()

    one_all_mention = MentionList([user_mention, all_mention])
    two_all_mentions = MentionList([all_mention, all_mention])

    # - Assert -
    assert one_all_mention.all_users_mentioned
    assert two_all_mentions.all_users_mentioned

    assert not MentionList([]).all_users_mentioned
