from typing import Any, List, Literal, TypeVar, Union


class _UndefinedType:
    """For fields that can be skipped."""

    _instances: List["_UndefinedType"] = []

    def __new__(cls, *args: Any) -> "_UndefinedType":
        if not cls._instances:
            cls._instances.append(super().__new__(cls, *args))
        return cls._instances[-1]

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "Undefined"


RequiredType = TypeVar("RequiredType")
Undefined = _UndefinedType()

Missing = Union[RequiredType, _UndefinedType]
MissingOptional = Union[RequiredType, None, _UndefinedType]
