from typing import List, Optional, Sequence, TypeVar

TItem = TypeVar("TItem")


def optional_sequence_to_list(
    optional_sequence: Optional[Sequence[TItem]],
) -> List[TItem]:
    return list(optional_sequence or [])
