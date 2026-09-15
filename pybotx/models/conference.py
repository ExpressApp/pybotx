from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class Conference:
    id: UUID
    name: str
    link: str
    members: list[UUID]
