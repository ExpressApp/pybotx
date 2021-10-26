from typing import TypeVar, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class _UndefinedType:
    """For fields that can be skipped."""

    def __bool__(self) -> Literal[False]:
        return False


RequiredType = TypeVar("RequiredType")
Undefined = _UndefinedType()

Missing = Union[RequiredType, _UndefinedType]
MissingOptional = Union[RequiredType, None, _UndefinedType]
