import json
from uuid import UUID

from pydantic import BaseConfig

from botx.core import BotXObject


class _UUIDJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)

        return super().default(o)


class BotXType(BotXObject):
    class Config(BaseConfig):
        allow_population_by_alias = True

    def json(self, *, by_alias: bool = True, **kwargs):
        return super().json(by_alias=by_alias, **kwargs)

    def dict(self, *, by_alias: bool = True, **kwargs):
        return json.loads(
            json.dumps(super().dict(by_alias=by_alias, **kwargs), cls=_UUIDJSONEncoder)
        )
