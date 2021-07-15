import uuid
from unittest.mock import Mock

import pytest
from httpx import ConnectError, Request, Response

from botx.clients.methods.v2.bots.token import Token
from botx.exceptions import BotXConnectError, BotXJSONDecodeError


@pytest.fixture()
def token_method():
    return Token(host="example.cts", bot_id=uuid.uuid4(), signature="signature")


@pytest.fixture()
def mock_http_client():
    return Mock()


def test_execute_without_explicit_host(client, token_method):
    request = client.bot.sync_client.build_request(token_method)

    assert client.bot.sync_client.execute(request)


def test_raising_connection_error(client, token_method, mock_http_client):
    request = Request(token_method.http_method, token_method.url)
    mock_http_client.request.side_effect = ConnectError("Test error", request=request)

    client.bot.sync_client.http_client = mock_http_client
    botx_request = client.bot.sync_client.build_request(token_method)

    with pytest.raises(BotXConnectError):
        client.bot.sync_client.execute(botx_request)


def test_raising_decode_error(client, token_method, mock_http_client):
    response = Response(status_code=418, text="Wrong json")
    mock_http_client.request.return_value = response

    client.bot.sync_client.http_client = mock_http_client
    botx_request = client.bot.sync_client.build_request(token_method)

    with pytest.raises(BotXJSONDecodeError):
        client.bot.sync_client.execute(botx_request)
