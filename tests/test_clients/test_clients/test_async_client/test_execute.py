import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import ConnectError, Request, Response

from botx.clients.methods.v2.bots.token import Token
from botx.exceptions import BotXConnectError, BotXJSONDecodeError

try:
    from unittest.mock import AsyncMock
except ImportError:
    from unittest.mock import MagicMock

    # Used for compatibility with python 3.7
    class AsyncMock(MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.fixture()
def token_method():
    return Token(host="example.cts", bot_id=uuid.uuid4(), signature="signature")


@pytest.fixture()
def mock_http_client():
    return AsyncMock()


@pytest.mark.asyncio()
async def test_raising_connection_error(client, token_method, mock_http_client):
    request = Request(token_method.http_method, token_method.url)
    mock_http_client.request.side_effect = ConnectError("Test error", request=request)

    client.bot.client.http_client = mock_http_client
    botx_request = client.bot.client.build_request(token_method)

    with pytest.raises(BotXConnectError):
        await client.bot.client.execute(botx_request)


@pytest.mark.asyncio()
async def test_raising_decode_error(client, token_method, mock_http_client):
    response = Response(status_code=418, text="Wrong json")
    mock_http_client.request.return_value = response

    client.bot.client.http_client = mock_http_client
    botx_request = client.bot.client.build_request(token_method)

    with pytest.raises(BotXJSONDecodeError):
        await client.bot.client.execute(botx_request)
