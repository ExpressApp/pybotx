import pytest
from pydantic import ValidationError

from botx import BotDisabledErrorData, BotDisabledResponse


class TestBotDisabledResponseValidation:
    def test_error_when_status_message_not_present_in_error_data_when_dict(
        self,
    ) -> None:
        with pytest.raises(ValidationError):
            _ = BotDisabledResponse(error_data={})

    def test_doing_nothing_when_passed_error_data_model(self) -> None:
        response = BotDisabledResponse(
            error_data=BotDisabledErrorData(status_message="test")
        )
        assert response.error_data.status_message == "test"

    def test_leaving_dict_as_error_data_when_status_message_present(self) -> None:
        assert BotDisabledResponse(
            error_data={"status_message": "test", "extra": True}
        ).error_data == {"status_message": "test", "extra": True}
