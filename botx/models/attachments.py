"""Module with attachments for botx."""

from typing import List, Optional, Union, cast

from pydantic import BaseModel

from botx.models.enums import AttachmentsTypes, LinkProtos
from botx.models.files import File


class FileAttachment(BaseModel):
    """Class that represents file in RFC 2397 format."""

    #: name of file.
    file_name: Optional[str]

    #: file content in RFC 2397 format.
    content: str  # noqa: WPS110


class Image(FileAttachment):
    """Image model from botx."""

    file_name: str = "image.jpg"


class Video(FileAttachment):
    """Video model from botx."""

    file_name: str = "video.mp4"

    #: video duration
    duration: int


class Document(FileAttachment):
    """Document model from botx."""

    file_name: str = "document.docx"


class Voice(BaseModel):
    """Voice model from botx."""

    #: file content in RFC 2397 format.
    content: str  # noqa: WPS110

    #: voice duration
    duration: int


class Location(BaseModel):
    """Location model from botx."""

    #: name of location
    location_name: str

    #: address of location
    location_address: str

    #: latitude of location
    location_lat: float

    #: longitude of location
    location_lng: float


class Contact(BaseModel):
    """Contact model from botx."""

    #: name of contact
    contact_name: str


class Link(BaseModel):
    """Class that marked as Link from botx."""

    #: url of link
    url: str

    #: title of url
    url_title: Optional[str] = None

    #: link on preview of this link
    url_preview: Optional[str] = None

    #: text on preview
    url_text: Optional[str] = None

    def is_mail(self) -> bool:
        """Confirm that is email link."""
        return self.url.startswith(LinkProtos.email)

    def is_telephone(self) -> bool:
        """Confirm that is telephone link."""
        return self.url.startswith(LinkProtos.telephone)

    def is_link(self) -> bool:
        """Confirm that is link on resource."""
        return not (self.is_mail() or self.is_telephone())

    @property
    def mailto(self) -> str:
        """Property that retuning email address without protocol."""
        if not self.is_mail():
            raise AttributeError("mailto")
        return self.url[len(LinkProtos.email) :]  # noqa: E203

    @property
    def tel(self) -> str:
        """Property that retuning telephone number without protocol."""
        if not self.is_telephone():
            raise AttributeError("telephone number")
        return self.url[len(LinkProtos.telephone) :]  # noqa: E203


Attachments = Union[
    Video, Voice, Contact, Location, Link, Image, Document,
]


class Attachment(BaseModel):
    """Attachment with main attach and type of this attachment."""

    #: type of attachment
    type: str  # noqa: WPS125

    #: content of attachment
    data: Attachments  # noqa: WPS110


class AttachList(BaseModel):  # noqa: WPS214, WPS338
    """Additional wrapped class for use property."""

    __root__: List[Attachment]

    def _get_attach_by_type(self, attach_type: AttachmentsTypes) -> Attachments:
        for attach in self.__root__:
            if attach.type == attach_type:
                return attach.data
        raise AttributeError(attach_type)

    @property
    def image(self) -> Image:
        """Parse attachments.

        Returns:
            Image: image from attachments.
        Raises:
            AttributeError: message has no image.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.image)
        return cast(Image, attach)

    @property
    def document(self) -> Document:
        """Parse attachments.

        Returns:
            Document: document from attachments.
        Raises:
            AttributeError: message has no document.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.document)
        return cast(Document, attach)

    @property
    def location(self) -> Location:
        """Parse attachments.

        Returns:
            Location: location from attachments.
        Raises:
            AttributeError: message has no location.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.location)
        return cast(Location, attach)

    @property
    def contact(self) -> Contact:
        """Parse attachments.

        Returns:
            Contact: contact from attachments.
        Raises:
            AttributeError: message has no contact.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.contact)
        return cast(Contact, attach)

    @property
    def voice(self) -> Voice:
        """Parse attachments.

        Returns:
            Voice: voice from attachments
        Raises:
            AttributeError: message has no voice.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.voice)
        return cast(Voice, attach)

    @property
    def video(self) -> Video:
        """Parse attachments.

        Returns:
            Video: video from attachments.
        Raises:
            AttributeError: message has no video.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.video)
        return cast(Video, attach)

    @property
    def link(self) -> Link:
        """Parse attachments.

        Returns:
            Link: lint to resource from attachments.
        Raises:
            AttributeError: message has no link.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.link)
        if attach.is_link():  # type: ignore
            return cast(Link, attach)
        raise AttributeError(AttachmentsTypes.link)

    @property
    def email(self) -> str:
        """Parse attachments.

        Returns:
            str: email from attachments.
        Raises:
            AttributeError: message has no email.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.link)
        if attach.is_mail():  # type: ignore
            return attach.mailto  # type: ignore
        raise AttributeError(AttachmentsTypes.link)

    @property
    def telephone(self) -> str:
        """Parse attachments.

        Returns:
            str: telephone number from attachments.
        Raises:
            AttributeError: message has no telephone.
        """
        attach = self._get_attach_by_type(AttachmentsTypes.link)
        if attach.is_telephone():  # type: ignore
            return attach.tel  # type: ignore
        raise AttributeError(AttachmentsTypes.link)

    @property
    def all_attachments(self) -> List[Attachment]:
        """Search attachments in message.

        Returns:
            List of attachments.
        """
        return self.__root__

    @property
    def file(self) -> File:
        """Search file in message's attachments.

        Returns:
            Botx file from video, image or document.
        Raises:
            AttributeError: message has no file.
        """
        for attachment in self.__root__:
            if isinstance(attachment.data, FileAttachment):
                return File(
                    file_name=attachment.data.file_name, data=attachment.data.content,
                )
        raise AttributeError
