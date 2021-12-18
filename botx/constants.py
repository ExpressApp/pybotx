try:
    from typing import Final
except ImportError:
    from typing_extensions import Final  # type: ignore  # noqa: WPS440

CHUNK_SIZE: Final[int] = 1024 * 1024  # 1Mb
BOT_API_VERSION: Final[int] = 4
SMARTAPP_API_VERSION: Final[int] = 1
STICKER_IMAGE_MAX_SIZE: Final[int] = 512 * 1024  # 512Kb
STICKER_PACKS_PER_PAGE: Final[int] = 10
