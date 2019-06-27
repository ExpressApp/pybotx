import json
from typing import TYPE_CHECKING, Any, Callable, Optional

from pydantic import BaseConfig, BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from pydantic.main import SetStr, DictStrAny


class BotXType(BaseModel):
    class Config(BaseConfig):
        allow_population_by_alias = True

    def json(
        self,
        *,
        include: "SetStr" = None,
        exclude: "SetStr" = None,
        by_alias: bool = True,
        skip_defaults: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        **dumps_kwargs: Any,
    ) -> str:
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            encoder=encoder,
            **dumps_kwargs,
        )

    def dict(  # noqa: A003
        self,
        *,
        include: "SetStr" = None,
        exclude: "SetStr" = None,
        by_alias: bool = True,
        skip_defaults: bool = False,
    ) -> "DictStrAny":
        return json.loads(
            json.dumps(
                super().dict(
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    skip_defaults=skip_defaults,
                ),
                default=str,
            )
        )
