from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LoggerPort(Protocol):
    def add(self, *args: Any, **kwargs: Any) -> Any: ...  # pragma: no cover

    def remove(self, *args: Any, **kwargs: Any) -> None: ...  # pragma: no cover

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None: ...  # pragma: no cover

    def info(self, message: str, *args: Any, **kwargs: Any) -> None: ...  # pragma: no cover

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None: ...  # pragma: no cover

    def error(self, message: str, *args: Any, **kwargs: Any) -> None: ...  # pragma: no cover

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None: ...  # pragma: no cover

    def opt(self, *args: Any, **kwargs: Any) -> "LoggerPort": ...  # pragma: no cover

    def enable(self, name: str) -> None: ...  # pragma: no cover

    def disable(self, name: str) -> None: ...  # pragma: no cover
