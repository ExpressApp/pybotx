from __future__ import annotations

from pybotx.infrastructure.contracts.api_base import UnverifiedPayloadBaseModel
from pybotx.domain.models.attachments import (
    IncomingFileAttachment,
    OutgoingAttachment,
    DEFAULT_MIMETYPE,
    EXTENSIONS_TO_MIMETYPES,
    encode_rfc2397,
)


class BotXAPIAttachment(UnverifiedPayloadBaseModel):
    file_name: str
    data: str

    @classmethod
    def from_file_attachment(
        cls,
        attachment: IncomingFileAttachment | OutgoingAttachment,
    ) -> "BotXAPIAttachment":
        assert attachment.content is not None

        mimetype = EXTENSIONS_TO_MIMETYPES.get(
            attachment.filename.split(".")[-1],
            DEFAULT_MIMETYPE,
        )

        return cls(
            file_name=attachment.filename,
            data=encode_rfc2397(attachment.content, mimetype),
        )


__all__ = ("BotXAPIAttachment",)
