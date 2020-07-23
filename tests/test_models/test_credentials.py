from uuid import UUID

from botx import ExpressServer


def test_calculating_signature_for_token(host) -> None:
    bot_id = UUID("8dada2c8-67a6-4434-9dec-570d244e78ee")
    server = ExpressServer(host=host, secret_key="secret")
    signature = "904E39D3BC549C71F4A4BDA66AFCDA6FC90D471A64889B45CC8D2288E56526AD"
    assert server.calculate_signature(bot_id) == signature
