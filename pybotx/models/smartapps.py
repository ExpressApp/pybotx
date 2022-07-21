from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
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
    avatar: Optional[str] = None
    avatar_preview: Optional[str] = None
