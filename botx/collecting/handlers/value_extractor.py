"""Extractor for field from validated validated_values."""
from typing import Any


def get_value(value_name: str, values_storage: dict) -> Any:
    """Extract value from validated validated_values.

    Arguments:
        value_name: name of value that should be extracted.
        values_storage: already validated validated_values.

    Returns:
        Extracted value.

    Raises:
        ValueError: raised if value was not found.
    """
    if value_name not in values_storage:
        raise ValueError("{0} not found in validated_values".format(value_name))

    return values_storage[value_name]
