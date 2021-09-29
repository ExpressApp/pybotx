try:
    from typing import Final
except ImportError:
    from typing_extensions import Final  # type: ignore  # noqa: WPS440

BOT_API_VERSION: Final = 4