from pybotx.constants import BOT_API_VERSION


class UnsupportedBotAPIVersionError(Exception):
    def __init__(self, version: int) -> None:
        self.version = version
        self.message = (
            f"Unsupported Bot API version: `{version}`, expected `{BOT_API_VERSION}`"
        )
        super().__init__(self.message)


class UnknownSystemEventError(Exception):
    def __init__(self, type_name: str) -> None:
        self.type_name = type_name
        self.message = f"Unknown system event: `{type_name}`"
        super().__init__(self.message)
