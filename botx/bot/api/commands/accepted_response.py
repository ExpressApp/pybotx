from typing import Any, Dict


def build_accepted_response() -> Dict[str, Any]:  # pragma: no cover
    """Build accepted response for BotX.

    It should be sent if the bot started processing a command.

    Returns:
        built accepted response.
    """
    return {"result": "accepted"}
