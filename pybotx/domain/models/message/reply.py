from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.message.mentions import MentionList


@dataclass(slots=True)
class Reply:
    author_id: UUID
    sync_id: UUID
    body: str
    mentions: MentionList
