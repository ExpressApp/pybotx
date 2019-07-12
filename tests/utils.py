import re
import typing
import uuid
from random import choice, randint
from string import ascii_lowercase

from starlette.requests import Request
from starlette.responses import JSONResponse

from botx import CommandCallback


def get_route_path_from_template(url_template: str) -> str:
    return url_template.split("{host}", 1)[1]


def generate_acsii_name() -> str:
    return "".join(choice(ascii_lowercase) for i in range(randint(5, 10)))


def generate_username() -> str:
    return " ".join(
        (generate_acsii_name().capitalize(), generate_acsii_name().capitalize())
    )


def generate_user(host: str, admin: bool = False, chat_creator: bool = False):
    return {
        "ad_domain": "domain.com",
        "ad_login": generate_acsii_name(),
        "chat_type": "chat",
        "group_chat_id": uuid.uuid4(),
        "host": host,
        "is_creator": chat_creator,
        "is_admin": admin,
        "user_huid": uuid.uuid4(),
        "username": generate_username(),
    }


def re_from_str(string: str) -> typing.Pattern:
    return re.compile(re.escape(string))


def create_callback(
    func: typing.Callable, *args: typing.Any, **kwargs: typing.Any
) -> CommandCallback:
    return CommandCallback(callback=func, args=args, kwargs=kwargs)


def get_test_route(
    array: typing.Optional[typing.List[typing.Any]] = None
) -> typing.Callable:
    async def testing_route(request: Request) -> JSONResponse:
        if array is not None:
            if request.method != "GET":
                if request.headers["Content-Type"] != "application/json":
                    array.append(await request.form())
                else:
                    array.append(await request.json())
            else:
                array.append(True)
        return JSONResponse({"status": "ok", "result": "token"})

    return testing_route
