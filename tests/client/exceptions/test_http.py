import pickle
import httpx

from pybotx.client.exceptions.http import InvalidBotXResponseError


def test_invalid_botx_response_error_reduce() -> None:
    # - Arrange -
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(
        status_code=400,
        json={"status": "error", "reason": "test_reason", "errors": ["test_error"]},
        request=request,
    )
    error = InvalidBotXResponseError(response)

    # - Act -
    # Pickle and unpickle the error
    pickled_error = pickle.dumps(error)
    unpickled_error = pickle.loads(pickled_error)

    # - Assert -
    # Verify that the unpickled error has the same response
    assert unpickled_error.response.status_code == error.response.status_code
    assert unpickled_error.response.json() == error.response.json()
