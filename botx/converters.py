"""Converters for common operations."""

from typing import List, Optional, Sequence, TypeVar

TSequenceElement = TypeVar("TSequenceElement")


def optional_sequence_to_list(
    seq: Optional[Sequence[TSequenceElement]] = None,
) -> List[TSequenceElement]:
    """Convert optional sequence of elements to list.

    Arguments:
        seq: sequence that should be converted to list.

    Returns:
        List of passed elements.
    """
    return list(seq or [])
