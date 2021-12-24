from dataclasses import dataclass
from uuid import UUID


@dataclass
class BotAccount:
    id: UUID
    host: str


@dataclass
class BotAccountWithSecret(BotAccount):
    secret_key: str
