"""Definition of errors in processing request from BotX API."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel, validator


class BotDisabledErrorData(BaseModel):
    """Data about occurred error."""

    #: message that will be shown to user.
    status_message: str


class BotDisabledResponse(BaseModel):
    """Response to BotX API if there was an error in handling incoming request."""

    #: error reason. *This should always be `bot_disabled` string.*
    reason: str = "bot_disabled"

    #: data about occurred error that should include `status_message` field in json.
    error_data: Union[Dict[str, Any], BotDisabledErrorData]

    errors: List[str] = []

    @validator("error_data", always=True, whole=True)
    def status_message_in_error_data(
        cls, error_data: Dict[str, Any],  # noqa: N805
    ) -> Union[BotDisabledErrorData, Dict[str, Any]]:
        """Check that value contains `status_message` key or field.

        Arguments:
            cls: this class.
            error_data: value that should be checked.

        Returns:
            Built payload for response.

        Raises:
            ValueError: raised if error_data does not contain status_message.
        """
        if set(error_data.keys()) == {"status_message"}:
            return BotDisabledErrorData(status_message=error_data["status_message"])

        if "status_message" not in error_data:
            raise ValueError("status_message key required in error_data")

        return error_data
