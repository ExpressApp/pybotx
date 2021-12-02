try:
    from typing import Final
except ImportError:
    from typing_extensions import Final  # type: ignore  # noqa: WPS440

CHUNK_SIZE: Final = 1024 * 1024  # 1Mb
BOT_API_VERSION: Final = 4
