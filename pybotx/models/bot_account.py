from dataclasses import dataclass

from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


@dataclass
class BotAccount:
    id: UUID
    host: Optional[str]


class BotAccountWithSecret(BaseModel):
    id: UUID
    cts_url: AnyHttpUrl
    secret_key: str

    model_config = ConfigDict(frozen=True)

    def __setattr__(self, name: str, value: object) -> None:
        if not getattr(self.model_config, "frozen", True) and name in self.model_fields:
            raise TypeError("BotAccountWithSecret is immutable")  # pragma: no cover
        super().__setattr__(name, value)

    @property
    def host(self) -> str:
        hostname = urlparse(str(self.cts_url)).hostname

        if hostname is None:
            raise ValueError("Could not parse host from cts_url.")

        return hostname
