"""Definition of entities for using in tests."""

from botx.testing.building.builder import MessageBuilder

try:
    from botx.testing.testing_client.client import TestClient  # noqa: WPS433
except ImportError:
    TestClient = None  # type: ignore  # noqa: WPS440

__all__ = ("TestClient", "MessageBuilder")  # noqa: WPS410
