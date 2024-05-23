from dataclasses import dataclass
from functools import cached_property
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


@dataclass
class BotAccount:
    id: UUID
    host: str


class BotAccountWithSecret(BaseModel):
    id: UUID
    cts_url: AnyHttpUrl
    secret_key: str

    model_config = ConfigDict(frozen=True, ignored_types=(cached_property,))

    @cached_property
    def host(self) -> str:
        if not hasattr(self.cts_url, "host"):  # noqa: WPS421
            raise ValueError("Could not parse host from cts_url.")

        return self.cts_url.host  # type: ignore[return-value]
