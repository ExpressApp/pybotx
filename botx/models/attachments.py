"""Module with attachments for botx."""

from typing import List, Optional, Union, cast

from pydantic import Field

from botx.models.base import BotXBaseModel
from botx.models.enums import AttachmentsTypes, LinkProtos
from botx.models.files import File

try:
    from typing import Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS433, WPS440, F401


class FileAttachment(BotXBaseModel):
    """Class that represents file in RFC 2397 format."""

    #: name of file.
    file_name: Optional[str]

    #: file content in RFC 2397 format.
    content: str


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


class Voice(BotXBaseModel):
    """Voice model from botx."""

    #: file content in RFC 2397 format.
    content: str

    #: voice duration
    duration: int


class Location(BotXBaseModel):
    """Location model from botx."""

    #: name of location
    location_name: str

    #: address of location
    location_address: str

    #: latitude of location
    location_lat: float

    #: longitude of location
    location_lng: float


class Contact(BotXBaseModel):
    """Contact model from botx."""

    #: name of contact
    contact_name: str


class Link(BotXBaseModel):
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


Attachments = Union[Image, Video, Document, Voice, Location, Contact, Link]


class ImageAttachment(BotXBaseModel):
    """BotX API image attachment container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.image] = Field(default=AttachmentsTypes.image)

    #: content of attachment
    data: Image


class VideoAttachment(BotXBaseModel):
    """BotX API video attachment container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.video] = Field(default=AttachmentsTypes.video)

    #: content of attachment
    data: Video


class DocumentAttachment(BotXBaseModel):
    """BotX API document attachment container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.document] = Field(default=AttachmentsTypes.document)

    #: content of attachment
    data: Document


class VoiceAttachment(BotXBaseModel):
    """BotX API voice attachment container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.voice] = Field(default=AttachmentsTypes.voice)

    #: content of attachment
    data: Voice


class ContactAttachment(BotXBaseModel):
    """BotX API contact attachment container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.contact] = Field(default=AttachmentsTypes.contact)

    #: content of attachment
    data: Contact


class LocationAttachment(BotXBaseModel):
    """BotX API location attachment container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.location] = Field(default=AttachmentsTypes.location)

    #: content of attachment
    data: Location


class LinkAttachment(BotXBaseModel):
    """BotX API link attachment container."""

    #: type of attachment
    type: Literal[AttachmentsTypes.link] = Field(default=AttachmentsTypes.link)

    #: content of attachment
    data: Link


Attachment = Union[
    ImageAttachment,
    VideoAttachment,
    DocumentAttachment,
    VoiceAttachment,
    ContactAttachment,
    LocationAttachment,
    LinkAttachment,
]


class AttachList(BotXBaseModel):  # noqa: WPS214, WPS338
    """Additional wrapped class for use property."""

    __root__: List[Attachment]

    def _get_attach_by_type(self, attach_type: AttachmentsTypes) -> Attachments:
        for attach in self.all_attachments:
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
        for attachment in self.all_attachments:
            if isinstance(attachment.data, FileAttachment):
                return File.construct(
                    file_name=attachment.data.file_name,
                    data=attachment.data.content,
                )
        raise AttributeError

    @property
    def attach_type(self) -> AttachmentsTypes:
        """Get attachment type.

        Returns:
            AttachmentsTypes: Attachment type.
        Raises:
            AttributeError: message has no attachment.
        """
        if self.all_attachments:
            return self.all_attachments[0].type

        raise AttributeError
