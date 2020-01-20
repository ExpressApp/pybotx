"""Entities that represent some structs that are used in this library."""

from typing import Any, Optional


class State:
    """An object that can be used to store arbitrary state."""

    _state: dict

    def __init__(self, state: Optional[dict] = None):
        """Init state with required params.

        Arguments:
            state: initial state.
        """
        state = state or {}
        super().__setattr__("_state", state)  # noqa: WPS613

    def __setattr__(self, key: Any, value: Any) -> None:
        """Set state attribute.

        Arguments:
            key: key to set attribute.
            value: value of attribute.
        """
        self._state[key] = value

    # this is not module __getattr__
    def __getattr__(self, key: Any) -> Any:  # noqa: WPS413
        """Get state attribute.

        Arguments:
            key: key of retrieved attribute.

        Returns:
            Stored value.
        """
        try:
            return self._state[key]
        except KeyError:
            raise AttributeError(f"State has no attribute '{key}'")
