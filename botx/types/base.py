from typing import Dict, Any, Set

from pydantic import BaseConfig

from botx.base import BotXObject


class BotXType(BotXObject):
    class Config(BaseConfig):
        allow_population_by_alias = True

    def dict(
        self,
        *,
        include: Set[str] = None,
        exclude: Set[str] = None,
        by_alias: bool = True,
    ) -> Dict[str, Any]:
        if not exclude:
            exclude = set()
        return super().dict(include=include, exclude=exclude, by_alias=by_alias)

    def json(
        self,
        *,
        include: Set[str] = None,
        exclude: Set[str] = None,
        by_alias: bool = True,
        encoder=None,
        **dumps_kwargs,
    ) -> str:
        if not exclude:
            exclude = set()
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            encoder=encoder,
            **dumps_kwargs,
        )
