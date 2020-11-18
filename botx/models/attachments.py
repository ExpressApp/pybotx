"""Module with attachments for botx."""

from typing import List, Optional, Union

from pydantic import BaseModel

from botx.exceptions import MissingAttributeError
from botx.models.enums import AttachmentsTypes

MAIL_PROTO_STR = "mailto:"
TELEPHONE_PROTO_STR = "tel://"


class FileData(BaseModel):
    """Class that represents file in RFC 2397 format."""

    #: name of file.
    file_name: Optional[str]

    #: file content in RFC 2397 format.
    content: str  # noqa: WPS110


class Image(FileData):
    """Image model from botx."""

    file_name: str = "image.jpg"


class Video(FileData):
    """Image model from botx."""

    file_name: str = "video.mp4"
    #: video duration
    duration: int


class Document(FileData):
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
        return self.url.startswith(MAIL_PROTO_STR)

    def is_telephone(self) -> bool:
        """Confirm that is telephone link."""
        return self.url.startswith(TELEPHONE_PROTO_STR)

    def is_link(self) -> bool:
        """Confirm that is link on resource."""
        return not (self.is_mail() or self.is_telephone())

    @property
    def mailto(self) -> str:
        """Property that retuning email address without protocol."""
        if not self.is_mail():
            raise MissingAttributeError(attribute_name="mailto")
        # fmt: off
        return self.url[len(MAIL_PROTO_STR):]
        # fmt: on

    @property
    def tel(self) -> str:
        """Property that retuning telephone number without protocol."""
        if not self.is_telephone():
            raise MissingAttributeError(attribute_name="telephone number")
        # fmt: off
        return self.url[len(TELEPHONE_PROTO_STR):]
        # fmt: on


AttachmentMapping = {
    AttachmentsTypes.image: Image,
    AttachmentsTypes.video: Video,
    AttachmentsTypes.document: Document,
    AttachmentsTypes.voice: Voice,
    AttachmentsTypes.contact: Contact,
    AttachmentsTypes.location: Location,
    AttachmentsTypes.link: Link,
}

Attachments = Union[
    Video, Voice, Contact, Location, Link, Image, Document,
]


class Attachment(BaseModel):
    """Attachment with main attach and type of this attachment."""

    #: type of attachment
    type: str  # noqa: WPS125

    #: content of attachment
    data: Attachments  # noqa: WPS110


class AttachList(BaseModel):  # noqa: WPS214
    """Additional wrapped class for use property."""

    __root__: List[Attachment]

    @property
    def image(self) -> Image:
        """Parse attachments.

        Return:
            Image.
        """
        for attach in self.__root__:
            if attach.type == AttachmentsTypes.image:
                return attach.data  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.image)

    @property
    def document(self) -> Document:
        """Parse attachments.

        Return:
            Document.
        """
        for attach in self.__root__:
            if attach.type == AttachmentsTypes.document:
                return attach.data  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.document)

    @property
    def location(self) -> Location:
        """Parse attachments.

        Return:
            Location.
        """
        for attach in self.__root__:
            if attach.type == AttachmentsTypes.location:
                return attach.data  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.location)

    @property
    def contact(self) -> Contact:
        """Parse attachments.

        Return:
            Contact.
        """
        for attach in self.__root__:
            if attach.type == AttachmentsTypes.contact:
                return attach.data  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.contact)

    @property
    def voice(self) -> Voice:
        """Parse attachments.

        Return:
            Voice.
        """
        for attach in self.__root__:
            if attach.type == AttachmentsTypes.voice:
                return attach.data  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.voice)

    @property
    def video(self) -> Video:
        """Parse attachments.

        Return:
            Video.
        """
        for attach in self.__root__:
            if attach.type == AttachmentsTypes.video:
                return attach.data  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.video)

    @property
    def link(self) -> Link:
        """Parse attachments.

        Return:
            Link to resource.
        """
        for attach in self.__root__:
            is_link_by_type = attach.type == AttachmentsTypes.link
            if is_link_by_type and attach.data.is_link():  # type: ignore
                return attach.data  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.link)

    @property
    def email(self) -> Optional[str]:
        """Parse attachments.

        Return:
            Email.
        """
        for attach in self.__root__:
            is_link_by_type = attach.type == AttachmentsTypes.link
            if is_link_by_type and attach.data.is_mail():  # type: ignore
                return attach.data.mailto  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.link)

    @property
    def telephone(self) -> Optional[str]:
        """Parse attachments.

        Return:
            Telephone number.
        """
        for attach in self.__root__:
            is_link_by_type = attach.type == AttachmentsTypes.link
            if is_link_by_type and attach.data.is_telephone():  # type: ignore
                return attach.data.tel  # type: ignore
        raise MissingAttributeError(attribute_name=AttachmentsTypes.link)
