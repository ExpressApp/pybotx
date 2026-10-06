from __future__ import annotations

import asyncio
from collections.abc import Iterator
from uuid import UUID, uuid4

import pytest

from pybotx import (
    Bot,
    BotAccountKey,
    BotAccountWithSecret,
    BotXAuthVersion,
    HandlerCollector,
    StaticBotAccountProvider,
    lifespan_wrapper,
)
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.bot.contextvars import bot_account_key_var
from pybotx.bot.exceptions import AmbiguousBotAccountError, UnknownBotAccountError
from pybotx.models.bot_account import BotAccount
from pybotx.models.chats import Chat
from pybotx.models.enums import ChatTypes
from pybotx.models.message.incoming_message import (
    IncomingMessage,
    UserDevice,
    UserSender,
)


class SnapshotAccountProvider:
    def __init__(self, accounts: list[BotAccountWithSecret]) -> None:
        self._accounts: dict[BotAccountKey, BotAccountWithSecret] = {}
        for account in accounts:
            assert account.account_key is not None
            self._accounts[account.account_key] = account

    def get_account(self, key: BotAccountKey) -> BotAccountWithSecret:
        account = self._accounts.get(key)
        if account is None:
            raise UnknownBotAccountError(key.bot_id)
        return account

    def get_account_by_bot_id(self, bot_id: UUID) -> BotAccountWithSecret:
        matches = [account for account in self._accounts.values() if account.id == bot_id]
        if not matches:
            raise UnknownBotAccountError(bot_id)
        if len(matches) > 1:
            raise AmbiguousBotAccountError(bot_id)
        return matches[0]

    def resolve_incoming_account_key(
        self, *, bot_id: UUID, host: str | None
    ) -> BotAccountKey:
        matches = [
            key
            for key, account in self._accounts.items()
            if account.id == bot_id and account.host == host
        ]
        if len(matches) != 1:
            raise UnknownBotAccountError(bot_id)
        return matches[0]

    def iter_bot_accounts(self) -> Iterator[BotAccountWithSecret]:
        yield from self._accounts.values()


@pytest.fixture
def dynamic_accounts(bot_id: UUID) -> tuple[BotAccountWithSecret, BotAccountWithSecret]:
    first_key = BotAccountKey(server_id="cts-a", bot_id=bot_id)
    second_key = BotAccountKey(server_id="cts-b", bot_id=bot_id)
    return (
        BotAccountWithSecret(
            id=bot_id,
            cts_url="https://cts-a.example.com",
            secret_key="secret-a",
            account_key=first_key,
            revision=1,
        ),
        BotAccountWithSecret(
            id=bot_id,
            cts_url="https://cts-b.example.com",
            secret_key="secret-b",
            account_key=second_key,
            revision=2,
        ),
    )


def test__accounts_storage__requires_explicit_context_for_ambiguous_bot_id(
    bot_id: UUID,
    dynamic_accounts: tuple[BotAccountWithSecret, BotAccountWithSecret],
) -> None:
    storage = BotAccountsStorage(account_provider=SnapshotAccountProvider(list(dynamic_accounts)))

    with pytest.raises(AmbiguousBotAccountError):
        storage.get_cts_url(bot_id)


def test__accounts_storage__validates_a_single_account_source(
    bot_account: BotAccountWithSecret,
) -> None:
    provider = StaticBotAccountProvider([bot_account])

    with pytest.raises(ValueError, match="either `bot_accounts` or `account_provider`"):
        Bot(
            collectors=[HandlerCollector()],
            bot_accounts=[bot_account],
            account_provider=provider,
        )

    with pytest.raises(ValueError, match="either `bot_accounts` or `account_provider`"):
        BotAccountsStorage([bot_account], account_provider=provider)


def test__accounts_storage__ignores_context_for_another_bot_id(
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    storage = BotAccountsStorage([bot_account])
    context_token = bot_account_key_var.set(
        BotAccountKey(server_id="another-cts", bot_id=uuid4())
    )
    try:
        assert storage.get_cts_url(bot_id) == "https://cts.example.com/"
    finally:
        bot_account_key_var.reset(context_token)


def test__static_account_provider__raises_for_an_unknown_account_key(
    bot_account: BotAccountWithSecret,
) -> None:
    provider = StaticBotAccountProvider([bot_account])

    with pytest.raises(UnknownBotAccountError):
        provider.get_account(BotAccountKey(server_id="cts", bot_id=uuid4()))


def test__bot__warns_without_an_account_source(
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    bot = Bot(collectors=[HandlerCollector()])
    try:
        assert "Bot has no bot accounts" in loguru_caplog.text
    finally:
        asyncio.run(bot.shutdown())


def test__accounts_storage__isolates_v1_tokens_by_account_key_and_revision(
    bot_id: UUID,
    dynamic_accounts: tuple[BotAccountWithSecret, BotAccountWithSecret],
) -> None:
    first, second = dynamic_accounts
    assert first.account_key is not None
    assert second.account_key is not None
    storage = BotAccountsStorage(account_provider=SnapshotAccountProvider([first, second]))

    first_token = bot_account_key_var.set(first.account_key)
    try:
        assert storage.get_cts_url(bot_id) == "https://cts-a.example.com/"
        storage.set_token(bot_id, "token-a")
        assert storage.get_token_or_none(bot_id) == "token-a"
    finally:
        bot_account_key_var.reset(first_token)

    second_token = bot_account_key_var.set(second.account_key)
    try:
        assert storage.get_cts_url(bot_id) == "https://cts-b.example.com/"
        assert storage.get_token_or_none(bot_id) is None
        storage.set_token(bot_id, "token-b")
    finally:
        bot_account_key_var.reset(second_token)

    storage.invalidate(first.account_key)
    first_token = bot_account_key_var.set(first.account_key)
    try:
        assert storage.get_token_or_none(bot_id) is None
    finally:
        bot_account_key_var.reset(first_token)
    second_token = bot_account_key_var.set(second.account_key)
    try:
        assert storage.get_token_or_none(bot_id) == "token-b"
    finally:
        bot_account_key_var.reset(second_token)


@pytest.mark.asyncio
async def test__bot__resolves_each_inbound_command_to_its_cts_context(
    bot_id: UUID,
    dynamic_accounts: tuple[BotAccountWithSecret, BotAccountWithSecret],
) -> None:
    collector = HandlerCollector()
    observed_urls: list[str] = []

    @collector.command("/where", description="Resolve the current CTS")
    async def where(message: IncomingMessage, bot: Bot) -> None:
        await asyncio.sleep(0)
        observed_urls.append(bot._bot_accounts_storage.get_cts_url(message.bot.id))

    bot = Bot(
        collectors=[collector],
        account_provider=SnapshotAccountProvider(list(dynamic_accounts)),
    )
    async with lifespan_wrapper(bot):
        tasks = []
        for number, host in enumerate(("cts-a.example.com", "cts-b.example.com"), 1):
            message = IncomingMessage(
                bot=BotAccount(id=bot_id, host=host),
                sync_id=UUID(int=number),
                source_sync_id=None,
                body="/where",
                data={},
                metadata={},
                raw_command=None,
                sender=UserSender(
                    huid=UUID(int=1),
                    udid=None,
                    ad_login=None,
                    ad_domain=None,
                    username=None,
                    is_chat_admin=None,
                    is_chat_creator=None,
                    device=UserDevice(
                        manufacturer=None,
                        device_name=None,
                        os=None,
                        pushes=None,
                        timezone=None,
                        permissions=None,
                        platform=None,
                        platform_package_id=None,
                        app_version=None,
                        locale=None,
                    ),
                ),
                chat=Chat(id=UUID(int=1), type=ChatTypes.GROUP_CHAT),
            )
            tasks.append(bot.async_execute_bot_command(message))
        await asyncio.gather(*tasks)

    assert sorted(observed_urls) == [
        "https://cts-a.example.com/",
        "https://cts-b.example.com/",
    ]


def test__bot__account_scope_supports_background_operation_context(
    bot_id: UUID,
    dynamic_accounts: tuple[BotAccountWithSecret, BotAccountWithSecret],
) -> None:
    first, second = dynamic_accounts
    assert first.account_key is not None
    assert second.account_key is not None
    bot = Bot(
        collectors=[HandlerCollector()],
        account_provider=SnapshotAccountProvider([first, second]),
    )

    with bot.account_scope(first.account_key):
        assert bot._bot_accounts_storage.get_cts_url(bot_id) == "https://cts-a.example.com/"
    with bot.account_scope(second.account_key):
        assert bot._bot_accounts_storage.get_cts_url(bot_id) == "https://cts-b.example.com/"

    with bot.account_scope(first.account_key):
        bot._bot_accounts_storage.set_token(bot_id, "token-a")
    bot.invalidate_account(first.account_key)
    with bot.account_scope(first.account_key):
        assert bot._bot_accounts_storage.get_token_or_none(bot_id) is None


@pytest.mark.asyncio
async def test__bot__fetch_tokens_binds_each_dynamic_account_scope(
    bot_id: UUID,
    dynamic_accounts: tuple[BotAccountWithSecret, BotAccountWithSecret],
) -> None:
    first, second = dynamic_accounts
    assert first.account_key is not None
    assert second.account_key is not None
    bot = Bot(
        collectors=[HandlerCollector()],
        account_provider=SnapshotAccountProvider([first, second]),
        auth_version=BotXAuthVersion.V1,
    )
    requested_urls: list[str] = []

    async def get_token(*, bot_id: UUID) -> str:
        requested_urls.append(bot._bot_accounts_storage.get_cts_url(bot_id))
        return f"token-{len(requested_urls)}"

    bot.get_token = get_token  # type: ignore[method-assign]
    try:
        await bot.fetch_tokens()
        assert requested_urls == [
            "https://cts-a.example.com/",
            "https://cts-b.example.com/",
        ]
        with bot.account_scope(first.account_key):
            assert bot._bot_accounts_storage.get_token_or_none(bot_id) == "token-1"
        with bot.account_scope(second.account_key):
            assert bot._bot_accounts_storage.get_token_or_none(bot_id) == "token-2"
    finally:
        await bot.shutdown()
