from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

from example.todo_bot_django.bootstrap import bot
from pybotx import wrap_asgi_app


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.todo_bot_django.settings")


django_app = get_asgi_application()
application = wrap_asgi_app(django_app, bot)
