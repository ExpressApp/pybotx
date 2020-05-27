from typing import Dict, Optional, Union

from pydantic import BaseModel

PrimitiveDataType = Union[None, str, int, float, bool]


class HTTPRequest(BaseModel):
    method: str
    url: str
    headers: Dict[str, str]
    query_params: Dict[str, PrimitiveDataType]
    request_data: Optional[Union[str, bytes]]
