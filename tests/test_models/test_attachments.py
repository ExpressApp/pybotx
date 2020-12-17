import pytest

from botx import MessageBuilder
from botx.models.attachments import Video, Voice


def test_is_link_in_attachment():
    builder = MessageBuilder()
    builder.link()
    assert builder.message.attachments.__root__[0].data.is_link()


def test_is_mail_in_attachment():
    builder = MessageBuilder()
    mailto_url = "mailto:mail@mail.com"
    builder.link(url=mailto_url)
    assert builder.message.attachments.__root__[0].data.is_mail()


def test_is_telephone_number_in_attachment():
    builder = MessageBuilder()
    tel_url = "tel://+77777777777"
    builder.link(url=tel_url)
    assert builder.message.attachments.__root__[0].data.is_telephone()


def test_mailto_property_in_attachment():
    builder = MessageBuilder()
    mailto_url = "mailto:mail@mail.com"
    builder.link(mailto_url)
    assert builder.message.attachments.__root__[0].data.mailto == "mail@mail.com"


def test_raising_missing_mailto():
    builder = MessageBuilder()
    builder.link()
    with pytest.raises(AttributeError):
        builder.message.attachments.__root__[0].data.mailto


def test_tel_property_in_attachment():
    builder = MessageBuilder()
    tel_url = "tel://+77777777777"
    builder.link(url=tel_url)
    assert builder.message.attachments.__root__[0].data.tel == "+77777777777"


def test_raising_missing_tel():
    builder = MessageBuilder()
    builder.link()
    with pytest.raises(AttributeError):
        builder.message.attachments.__root__[0].data.tel


def test_image_in_attachments():
    builder = MessageBuilder()
    builder.document()
    builder.image()
    assert builder.message.attachments.image


def test_missing_image_in_attachments():
    builder = MessageBuilder()
    with pytest.raises(AttributeError):
        builder.message.attachments.image


def test_document_in_attachments():
    builder = MessageBuilder()
    builder.image()
    builder.document()
    assert builder.message.attachments.document


def test_missing_document_in_attachments():
    builder = MessageBuilder()
    with pytest.raises(AttributeError):
        builder.message.attachments.document


def test_location_in_attachments():
    builder = MessageBuilder()
    builder.image()
    builder.location()
    assert builder.message.attachments.location


def test_missing_location_in_attachments():
    builder = MessageBuilder()
    with pytest.raises(AttributeError):
        builder.message.attachments.location


def test_contact_in_attachments():
    builder = MessageBuilder()
    builder.image()
    builder.contact()
    assert builder.message.attachments.contact


def test_missing_contact_in_attachments():
    builder = MessageBuilder()
    with pytest.raises(AttributeError):
        builder.message.attachments.contact


def test_voice_in_attachments():
    builder = MessageBuilder()
    builder.image()
    builder.voice()
    assert builder.message.attachments.voice


def test_missing_voice_in_attachments():
    builder = MessageBuilder()
    with pytest.raises(AttributeError):
        builder.message.attachments.voice


def test_video_in_attachments():
    builder = MessageBuilder()
    builder.image()
    builder.video()
    assert builder.message.attachments.video


def test_missing_video_in_attachments():
    builder = MessageBuilder()
    with pytest.raises(AttributeError):
        builder.message.attachments.video


def test_link_in_attachments():
    builder = MessageBuilder()
    builder.image()
    builder.link()
    assert builder.message.attachments.link


def test_missing_link_in_attachments():
    builder = MessageBuilder()
    builder.link(url="mailto:mail@mail.com")
    with pytest.raises(AttributeError):
        builder.message.attachments.link


def test_email_in_attachments():
    builder = MessageBuilder()
    mailto_url = "mailto:mail@mail.com"
    builder.image()
    builder.link(url=mailto_url)
    assert builder.message.attachments.email == "mail@mail.com"


def test_missing_email_in_attachments():
    builder = MessageBuilder()
    builder.link(url="https://any.com")
    with pytest.raises(AttributeError):
        builder.message.attachments.email


def test_telephone_in_attachments():
    builder = MessageBuilder()
    tel_url = "tel://+77777777777"
    builder.image()
    builder.link(url=tel_url)
    assert builder.message.attachments.telephone == "+77777777777"


def test_missing_telephone_in_attachments():
    builder = MessageBuilder()
    builder.link(url="mailto:mail@mail.com")
    with pytest.raises(AttributeError):
        builder.message.attachments.telephone


@pytest.mark.parametrize(
    "attach", [lambda x: x.document, lambda x: x.image, lambda x: x.video],
)
def test_file_in_attachments(attach):
    builder = MessageBuilder()
    attach(builder)()
    assert builder.message.attachments.file


def test_no_file_in_message():
    builder = MessageBuilder()
    builder.link()
    with pytest.raises(AttributeError):
        builder.message.attachments.file


def test_file_with_unsupported_extension():
    builder = MessageBuilder()
    builder.document(file_name="test.py")
    assert builder.message.attachments.file


@pytest.mark.parametrize("len_of_attachments", [1, 2, 3])
def test_get_all_attachments(len_of_attachments):
    builder = MessageBuilder()
    for _ in range(len_of_attachments):
        builder.document()
    assert len(builder.message.attachments.all_attachments) == len_of_attachments


def test_video_attach_has_video_type():
    builder = MessageBuilder()
    builder.video()
    assert isinstance(builder.message.attachments.video, Video)


def test_voice_attach_has_voice_type():
    builder = MessageBuilder()
    builder.voice()
    assert isinstance(builder.message.attachments.voice, Voice)
