"""Entities that represent some structs that are used in this library."""

from typing import Any, Optional


class State:
    """An object that can be used to store arbitrary state."""

    _state: dict

    def __init__(self, state: Optional[dict] = None):
        """Init state with required query_params.

        Arguments:
            state: initial state.
        """
        state = state or {}
        super().__setattr__("_state", state)  # noqa: WPS613

    def __setattr__(self, key: Any, new_value: Any) -> None:
        """Set state attribute.

        Arguments:
            key: key to set attribute.
            new_value: value of attribute.
        """
        self._state[key] = new_value

    def __getattr__(self, key: Any) -> Any:
        """Get state attribute.

        Arguments:
            key: key of retrieved attribute.

        Returns:
            Stored value.

        Raises:
            AttributeError: raised if attribute was not found in state.
        """
        try:
            return self._state[key]
        except KeyError:
            raise AttributeError("state has no attribute '{0}'".format(key))
