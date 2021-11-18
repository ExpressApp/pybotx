from typing import Any, TypeVar, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class _UndefinedType:
    """For fields that can be skipped."""

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "Undefined"


RequiredType = TypeVar("RequiredType")
Undefined = _UndefinedType()

Missing = Union[RequiredType, _UndefinedType]
MissingOptional = Union[RequiredType, None, _UndefinedType]


def not_undefined(*args: Any) -> Any:
    for arg in args:
        if arg is not Undefined:
            return arg

    raise ValueError("All arguments have `Undefined` type")