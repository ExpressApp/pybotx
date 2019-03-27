import uuid

from botx import CTS, BotCredentials, CTSCredentials


def test_init(custom_base_bot_class, hostname):
    bot = custom_base_bot_class()
    assert bot._credentials == BotCredentials()

    bot.register_cts(CTS(host=hostname, secret_key="secret_key"))
    credentials = bot.get_cts_credentials()

    bot2 = custom_base_bot_class(credentials=credentials)
    assert bot2._credentials == credentials


def test_cts_registration(custom_base_bot_class, hostname):
    bot = custom_base_bot_class()
    cts = CTS(host=hostname, secret_key="secret_key")
    bot.register_cts(cts)

    assert bot.get_cts_credentials().known_cts[hostname] == (cts, None)


def test_bot_router_nesting(
    custom_base_bot_class, custom_router, custom_handler, custom_default_handler
):
    custom_router.add_handler(custom_default_handler)
    custom_router.add_handler(custom_handler)

    bot = custom_base_bot_class()
    bot.add_commands(custom_router)

    assert len(bot._dispatcher._handlers) == 1
    assert bot._dispatcher._handlers is not None


def test_bot_adding_commands_behaviour(
    custom_base_bot_class, custom_router, custom_handler
):
    custom_router.add_handler(custom_handler)

    bot = custom_base_bot_class()

    @bot.command
    def func(m):
        pass

    bot.add_commands(custom_router)

    assert len(bot._dispatcher._handlers) == 2


def test_bot_storage_credentials_retrieving(custom_base_bot_class, hostname):
    bot = custom_base_bot_class()

    assert not bot._get_token_from_credentials(hostname)

    cts = CTS(host=hostname, secret_key="secret_key")
    bot._credentials.known_cts[cts.host] = (
        cts,
        CTSCredentials(bot_id=uuid.uuid4(), result="token_for_bot"),
    )

    assert bot._get_token_from_credentials(hostname) == "token_for_bot"


def test_bot_credentials_update(custom_base_bot_class, bot_id, hostname, secret):
    bot = custom_base_bot_class(
        credentials=BotCredentials(
            known_cts={
                hostname: [
                    CTS(host=hostname, secret_key=secret),
                    CTSCredentials(bot_id=bot_id, result="result_token_for_operations"),
                ]
            }
        )
    )

    bot.add_cts_credentials(
        BotCredentials(
            known_cts={
                hostname: [
                    CTS(host=hostname, secret_key=secret),
                    CTSCredentials(
                        bot_id=bot_id, result="result_token_for_operations_replaced"
                    ),
                ]
            }
        )
    )

    assert (
        bot.get_cts_credentials().known_cts[hostname][1].result
        == "result_token_for_operations_replaced"
    )

    second_host = hostname + "2"
    bot.add_cts_credentials(
        BotCredentials(
            known_cts={
                second_host: [
                    CTS(host=second_host, secret_key=secret),
                    CTSCredentials(
                        bot_id=bot_id, result="result_token_for_operations_replaced"
                    ),
                ]
            }
        )
    )

    assert len(bot.get_cts_credentials().known_cts) == 2
