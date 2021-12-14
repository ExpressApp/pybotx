try:
    from typing import Final
except ImportError:
    from typing_extensions import Final  # type: ignore  # noqa: WPS440

CHUNK_SIZE: Final = 1024 * 1024  # 1Mb
BOT_API_VERSION: Final = 4
SMARTAPP_API_VERSION: Final = 1
STICKER_IMAGE_MAX_SIZE: Final = 512 * 1024  # 512Kb
