from typing import Any, Dict


def build_command_accepted_response() -> Dict[str, Any]:
    """Build accepted response for BotX.

    It should be sent if the bot started processing a command.

    :return: Built accepted response.
    """

    return {"result": "accepted"}
