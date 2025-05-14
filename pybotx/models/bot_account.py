from dataclasses import dataclass
from functools import cached_property
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel


@dataclass
class BotAccount:
    id: UUID
    host: Optional[str]


class BotAccountWithSecret(BaseModel):
    id: UUID
    cts_url: AnyHttpUrl
    secret_key: str

    class Config:
        allow_mutation = False
        keep_untouched = (cached_property,)

    @cached_property
    def host(self) -> str:
        hostname = urlparse(self.cts_url).hostname

        if hostname is None:
            raise ValueError("Could not parse host from cts_url.")

        return hostname
