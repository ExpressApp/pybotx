from typing import Any, Literal, TypeAlias, TypeVar


class _UndefinedType:
    """For fields that can be skipped."""

    _instances: list["_UndefinedType"] = []

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

Missing: TypeAlias = RequiredType | _UndefinedType
MissingOptional: TypeAlias = RequiredType | None | _UndefinedType
