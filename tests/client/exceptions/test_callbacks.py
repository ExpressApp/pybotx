import pickle
from uuid import UUID

from pybotx.client.exceptions.callbacks import BotXMethodFailedCallbackReceivedError
from pybotx.models.method_callbacks import BotAPIMethodFailedCallback


def test_botx_method_failed_callback_received_error_reduce() -> None:
    # - Arrange -
    callback = BotAPIMethodFailedCallback(
        sync_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        status="error",
        reason="test_reason",
        errors=["test_error"],
        error_data={},
    )
    error = BotXMethodFailedCallbackReceivedError(callback)

    # - Act -
    # Pickle and unpickle the error
    pickled_error = pickle.dumps(error)
    unpickled_error = pickle.loads(pickled_error)

    # - Assert -
    # Verify that the unpickled error has the same callback
    assert unpickled_error.callback == error.callback
