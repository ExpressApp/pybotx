"""Mixin for building attachments."""
from dataclasses import field

from botx.models import attachments as attach
from botx.testing import content as test_content


class BuildAttachmentsMixin:
    """Mixin for building attachments in message."""

    attachments: attach.AttachList = field(default_factory=list)  # type: ignore

    def image(
        self,
        content: str = test_content.PNG_DATA,  # noqa: WPS110
        file_name: str = "image.jpg",
    ) -> None:
        """Add image into incoming message.

        Arguments:
            content: image content in RFC 2397 format.
            file_name: name of file.
        """
        self.attachments.__root__.append(
            attach.ImageAttachment(
                data=attach.Image(content=content, file_name=file_name),
            ),
        )

    def document(
        self,
        content: str = test_content.DOCX_DATA,  # noqa: WPS110
        file_name: str = "document.docx",
    ) -> None:
        """Add document into incoming message.

        Arguments:
            content: document content in RFC 2397 format.
            file_name: name of file.
        """
        self.attachments.__root__.append(
            attach.DocumentAttachment(
                data=attach.Document(content=content, file_name=file_name),
            ),
        )

    def location(
        self,
        location_name: str = "loc_name",
        location_address: str = "loc_address",
        location_lat: int = 0,
        location_lng: int = 0,
    ) -> None:
        """Add location into incoming message.

        Arguments:
            location_name: name of location.
            location_lat: latitude.
            location_lng: longitude.
            location_address: address of location.
        """
        self.attachments.__root__.append(
            attach.LocationAttachment(
                data=attach.Location(
                    location_name=location_name,
                    location_lat=location_lat,
                    location_lng=location_lng,
                    location_address=location_address,
                ),
            ),
        )

    def voice(
        self,
        content: str = test_content.MP3_DATA,  # noqa: WPS110
        duration: int = 10,  # noqa: WPS110
    ) -> None:
        """Add voice into incoming message.

        Arguments:
            content: voice content in RFC 2397 format.
            duration: voice duration.
        """
        self.attachments.__root__.append(
            attach.VoiceAttachment(
                data=attach.Voice(duration=duration, content=content),
            ),
        )

    def video(
        self,
        content: str = test_content.MP4_DATA,  # noqa: WPS110
        file_name: str = "video.mp4",
        duration: int = 10,
    ) -> None:
        """Add video into incoming message.

        Arguments:
            content: voice content in RFC 2397 format.
            file_name: name of file.
            duration: video duration.
        """
        self.attachments.__root__.append(
            attach.VideoAttachment(
                data=attach.Video(
                    content=content,
                    file_name=file_name,
                    duration=duration,
                ),
            ),
        )

    def link(
        self,
        url: str = "https://google.com",
        url_preview: str = "https://image.jpg",
        url_text: str = "foo",
        url_title: str = "bar",
    ) -> None:
        """Add link into incoming message.

        Arguments:
            url: link on resource.
            url_preview: link on url preview.
            url_text: presented text on link.
            url_title: title of link.
        """
        self.attachments.__root__.append(
            attach.LinkAttachment(
                data=attach.Link(
                    url=url,
                    url_preview=url_preview,
                    url_text=url_text,
                    url_title=url_title,
                ),
            ),
        )

    def contact(self, contact_name: str = "Foo") -> None:
        """Add link into incoming message.

        Arguments:
            contact_name: name of contact
        """
        self.attachments.__root__.append(
            attach.ContactAttachment(data=attach.Contact(contact_name=contact_name)),
        )
