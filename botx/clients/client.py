from typing import List, Optional, Sequence

import httpx

from botx.utils import optional_sequence_to_list


class AsyncClient:
    def __init__(self, interceptors: Optional[Sequence] = None) -> None:
        self.http_client = httpx.AsyncClient()
        self.interceptors: List = optional_sequence_to_list(interceptors)
