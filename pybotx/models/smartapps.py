from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class SmartApp:
    """SmartApp from list of SmartApps.

    Attributes:
        app_id: Readable SmartApp id.
        enabled: Is the SmartApp enabled or not.
        id: SmartApp uuid.
        name: SmartApp name.
        avatar: SmartApp avatar url.
        avatar_preview: SmartApp avatar preview url.
    """

    app_id: str
    enabled: bool
    id: UUID
    name: str
    avatar: str | None = None
    avatar_preview: str | None = None
