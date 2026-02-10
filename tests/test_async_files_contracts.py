import importlib
from uuid import uuid4

import pytest

from pybotx.domain.missing import Undefined
from pybotx.domain.models.async_files import Document, Image, Video, Voice
from pybotx.domain.models.enums import AttachmentTypes


def _base_kwargs() -> dict:
    return {
        "filename": "file.txt",
        "size": 123,
        "is_async_file": True,
        "_file_id": uuid4(),
        "_file_url": "https://files.local/file",
        "_file_mimetype": "text/plain",
        "_file_hash": "hash",
        "file_preview": None,
        "file_preview_height": None,
        "file_preview_width": None,
        "file_encryption_algo": None,
        "chunk_size": None,
        "caption": None,
    }


@pytest.mark.parametrize(
    "module_path",
    [
        "pybotx.presentation.contracts.async_files",
        "pybotx.infrastructure.contracts.async_files",
    ],
)
@pytest.mark.parametrize(
    "file_cls, attachment_type, api_cls_name, extra",
    [
        (Image, AttachmentTypes.IMAGE, "ApiAsyncFileImage", {}),
        (Video, AttachmentTypes.VIDEO, "ApiAsyncFileVideo", {"duration": 10}),
        (Document, AttachmentTypes.DOCUMENT, "ApiAsyncFileDocument", {}),
        (Voice, AttachmentTypes.VOICE, "ApiAsyncFileVoice", {"duration": 3}),
    ],
)
def test__async_files__missing_optional_roundtrip(
    module_path: str,
    file_cls,
    attachment_type: AttachmentTypes,
    api_cls_name: str,
    extra: dict,
) -> None:
    module = importlib.import_module(module_path)
    kwargs = _base_kwargs()
    kwargs.update(extra)
    file = file_cls(type=attachment_type, **kwargs)

    api_file = module.convert_async_file_from_domain(file)
    assert isinstance(api_file, getattr(module, api_cls_name))
    assert api_file.file_preview is Undefined

    domain_file = module.convert_async_file_to_domain(api_file)
    assert domain_file.file_preview is None
    assert domain_file.file_preview_height is None
    assert domain_file.file_preview_width is None


@pytest.mark.parametrize(
    "module_path",
    [
        "pybotx.presentation.contracts.async_files",
        "pybotx.infrastructure.contracts.async_files",
    ],
)
def test__async_files__optional_values_roundtrip(module_path: str) -> None:
    module = importlib.import_module(module_path)
    kwargs = _base_kwargs()
    kwargs.update(
        {
            "file_preview": "preview",
            "file_preview_height": 10,
            "file_preview_width": 20,
            "file_encryption_algo": "algo",
            "chunk_size": 512,
            "caption": "caption",
        }
    )
    file = Image(type=AttachmentTypes.IMAGE, **kwargs)

    api_file = module.convert_async_file_from_domain(file)
    assert api_file.file_preview == "preview"

    domain_file = module.convert_async_file_to_domain(api_file)
    assert domain_file.file_preview == "preview"
    assert domain_file.file_preview_height == 10
    assert domain_file.file_preview_width == 20
    assert domain_file.file_encryption_algo == "algo"
    assert domain_file.chunk_size == 512
    assert domain_file.caption == "caption"
