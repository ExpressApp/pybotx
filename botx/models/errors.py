"""Definition of errors in processing request from BotX API."""

from typing import Any, Dict, Union

from pydantic import BaseModel, validator


class BotDisabledErrorData(BaseModel):
    """Data about occurred error."""

    status_message: str
    """message that will be shown to user."""


class BotDisabledResponse(BaseModel):
    """Response to BotX API if there was an error in handling incoming request."""

    reason: str = "bot_disabled"
    """error reason. *This should always be `bot_disabled` string.*"""
    error_data: Union[Dict[str, Any], BotDisabledErrorData]
    """data about occurred error that should include `status_message`
    field in json."""

    @validator("error_data", always=True, whole=True)
    def status_message_in_error_data(
        cls, value: Dict[str, Any]  # noqa: N805
    ) -> Union[BotDisabledErrorData, Dict[str, Any]]:
        """Check that value contains `status_message` key or field.

        Arguments:
            value: value that should be checked.

        Returns:
            Built payload for response.
        """
        if set(value.keys()) == {"status_message"}:
            return BotDisabledErrorData(status_message=value["status_message"])

        if "status_message" not in value:
            raise ValueError("status_message key required in error_data")

        return value
