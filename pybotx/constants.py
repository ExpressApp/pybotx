try:
    from typing import Final
except ImportError:
    from typing_extensions import Final  # type: ignore  # noqa: WPS440

CHUNK_SIZE: Final = 1024 * 1024  # 1Mb
BOT_API_VERSION: Final = 4
SMARTAPP_API_VERSION: Final = 1
STICKER_IMAGE_MAX_SIZE: Final = 512 * 1024  # 512Kb
STICKER_PACKS_PER_PAGE: Final = 10
MAX_NOTIFICATION_BODY_LENGTH: Final = 4096
MAX_FILE_LEN_IN_LOGS: Final = 64
BOTX_DEFAULT_TIMEOUT: Final = 60
