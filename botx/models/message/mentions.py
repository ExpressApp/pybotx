import re
from typing import Dict, List, Tuple, Union
from uuid import UUID, uuid4

from botx.missing import Missing, Undefined
from botx.models.api_base import UnverifiedPayloadBaseModel
from botx.models.enums import (
    BotAPIMentionTypes,
    MentionTypes,
    convert_mention_type_from_domain,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIPersonalMentionData(UnverifiedPayloadBaseModel):
    user_huid: UUID
    name: Missing[str]


class BotXAPIUserMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.USER]
    mention_id: UUID
    mention_data: BotXAPIPersonalMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"@{{mention:{self.mention_id}}}"


class BotXAPIContactMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.CONTACT]
    mention_id: UUID
    mention_data: BotXAPIPersonalMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"@@{{mention:{self.mention_id}}}"


class BotXAPIGroupMentionData(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    name: Missing[str]


class BotXAPIChatMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.CHAT]
    mention_id: UUID
    mention_data: BotXAPIGroupMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"##{{mention:{self.mention_id}}}"


class BotXAPIChannelMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.CHANNEL]
    mention_id: UUID
    mention_data: BotXAPIGroupMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"##{{mention:{self.mention_id}}}"


class BotXAPIAllMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.ALL]
    mention_id: UUID

    def to_botx_embed_mention_format(self) -> str:
        return f"@{{mention:{self.mention_id}}}"


BotXAPIMention = Union[
    BotXAPIUserMention,
    BotXAPIContactMention,
    BotXAPIChatMention,
    BotXAPIChannelMention,
    BotXAPIAllMention,
]


def build_botx_api_embed_mention(
    mention_dict: Dict[str, str],
) -> BotXAPIMention:
    mention_type = MentionTypes(mention_dict["mention_type"])
    mentioned_entity_id = mention_dict["mentioned_entity_id"]
    # re match will have "" if mention_name not passed
    mention_name = mention_dict["mention_name"] or Undefined

    if mention_type == MentionTypes.USER:
        return BotXAPIUserMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIPersonalMentionData(
                user_huid=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.CONTACT:
        return BotXAPIContactMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIPersonalMentionData(
                user_huid=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.CHAT:
        return BotXAPIChatMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIGroupMentionData(
                group_chat_id=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.CHANNEL:
        return BotXAPIChannelMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIGroupMentionData(
                group_chat_id=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.ALL:
        return BotXAPIAllMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
        )

    raise NotImplementedError


EMBED_MENTION_RE = re.compile(
    (
        "<embed_mention>"
        "(?P<mention_type>.+?):"
        r"(?P<mentioned_entity_id>[0-9a-f\-]*?):"
        "(?P<mention_name>.*?)"
        r"<\/embed_mention>"
    ),
)


def find_and_replace_embed_mentions(body: str) -> Tuple[str, List[BotXAPIMention]]:
    mentions = []

    for match in EMBED_MENTION_RE.finditer(body):
        mention_dict = match.groupdict()
        embed_mention = match.group(0)

        mention = build_botx_api_embed_mention(mention_dict)
        body = body.replace(embed_mention, mention.to_botx_embed_mention_format(), 1)

        mentions.append(mention)

    return body, mentions
