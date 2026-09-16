from typing import Optional


class Undefined:
    _instance: Optional["Undefined"] = None

    def __new__(cls) -> "Undefined":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


undefined = Undefined()
