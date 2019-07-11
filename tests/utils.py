import re
import typing
import uuid
from random import choice, randint
from string import ascii_lowercase


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
