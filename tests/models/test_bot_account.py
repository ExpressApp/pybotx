from uuid import UUID

import pytest

from pybotx import BotAccountWithSecret


def test__bot_account__could_not_parse_host(bot_id: UUID, cts_url: str) -> None:
    # - Arrange -
    bot_account = BotAccountWithSecret(
        id=bot_id,
        cts_url=cts_url,
        secret_key="secret_key",
    )
    bot_account.model_config["frozen"] = False
    bot_account.cts_url = "cts_url"  # type: ignore

    # - Assert -
    with pytest.raises(ValueError):
        bot_account.host
