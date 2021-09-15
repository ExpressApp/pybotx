from typing import TYPE_CHECKING, Dict, List, Protocol, Type, Union  # pragma: no cover

# https://github.com/python/typing/issues/182
if TYPE_CHECKING:  # JSON is recursive type alias

    class JSONArray(List["JSON"], Protocol):  # type: ignore
        __class__: Type[List["JSON"]]  # type: ignore

    class JSONObject(Dict[str, "JSON"], Protocol):  # type: ignore
        __class__: Type[Dict[str, "JSON"]]  # type: ignore

    JSON = Union[None, float, str, JSONArray, JSONObject]
