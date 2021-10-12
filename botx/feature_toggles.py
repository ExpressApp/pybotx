from typing import Dict

_feature_toggles: Dict[str, bool] = {}


def get_feature_toggle(key: str) -> bool:
    return _feature_toggles[key]


def fill_feature_toggles(toggles: Dict[str, bool]) -> None:
    _feature_toggles.update(toggles)
