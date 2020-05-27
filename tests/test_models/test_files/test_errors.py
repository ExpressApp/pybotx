import pytest
from pydantic import ValidationError

from botx import File


@pytest.mark.parametrize("extension", (".py", ".c", ".java"))
def test_error_with_wrong_extension(extension):
    with pytest.raises(ValidationError):
        _ = File(file_name="tmp{0}".format(extension), data="")
