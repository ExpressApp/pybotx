from typing import Any, Dict


def build_accepted_response() -> Dict[str, Any]:  # pragma: no cover
    """Build accepted response to BotX API.

    Returns:
        built accpeted response.

    It should be sent if the bot started processing a command.
    """
    return {"result": "accepted"}
