from typing import TypeVar, Union


class _UndefinedType:
    """For fields that can be skipped."""


RequiredType = TypeVar("RequiredType")
Undefined = _UndefinedType()

Missing = Union[RequiredType, _UndefinedType]
