import uuid

from botx.clients.methods.v2.bots.token import Token


def test_execute_without_explicit_host(client):
    method = Token(bot_id=uuid.uuid4(), signature="signature")
    method.host = "example.cts"
    request = client.bot.sync_client.build_request(method)

    assert client.bot.sync_client.execute(request)
