from typing import Any


def build_command_accepted_response() -> dict[str, Any]:
    """Build accepted response for BotX.

    It should be sent if the bot started processing a command.

    :return: Built accepted response.
    """

    return {"result": "accepted"}
