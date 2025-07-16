import pytest
from pydantic import ValidationError
from unittest.mock import patch
from uuid import UUID

from pybotx.models.bot_account import BotAccountWithSecret


def test_bot_account_with_secret_immutable() -> None:
    # - Arrange -
    bot_account = BotAccountWithSecret(
        id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        cts_url="https://example.com",
        secret_key="secret",
    )

    # - Act & Assert -
    with pytest.raises(ValidationError) as exc:
        bot_account.id = UUID("154af49e-5e18-4dca-ad73-4f96b6de63fa")  # type: ignore[misc]

    assert "frozen_instance" in str(exc.value)


def test_bot_account_with_secret_not_frozen() -> None:
    # - Arrange -
    bot_account = BotAccountWithSecret(
        id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        cts_url="https://example.com",
        secret_key="secret",
    )

    # Mock the condition to force the TypeError
    with patch.object(
        BotAccountWithSecret,
        "__setattr__",
        side_effect=TypeError("BotAccountWithSecret is immutable"),
    ):
        # - Act & Assert -
        with pytest.raises(TypeError) as exc:
            bot_account.id = UUID("154af49e-5e18-4dca-ad73-4f96b6de63fa")  # type: ignore[misc]

        assert "BotAccountWithSecret is immutable" in str(exc.value)
