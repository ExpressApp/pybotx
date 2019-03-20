import base64
import hashlib
import hmac

from botx import CTS


def test_cts(hostname, bot_id):
    secret_key = "secret"
    assert (
        CTS(host=hostname, secret_key=secret_key).calculate_signature(bot_id)
        == base64.b16encode(
            hmac.new(
                key=secret_key.encode(),
                msg=str(bot_id).encode(),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()
    )
