from typing import List

from botx.bot.models.commands.entities import Mention
from botx.bot.models.commands.enums import MentionTypes


class MentionList(List[Mention]):
    @property
    def contacts(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.CONTACT]

    @property
    def chats(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.CHAT]

    @property
    def channels(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.CHANNEL]

    @property
    def users(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.USER]

    @property
    def all_users_mentioned(self) -> bool:
        for mention in self:
            if mention.type == MentionTypes.ALL:
                return True

        return False
