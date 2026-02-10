from __future__ import annotations

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "todo-bot-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
]

MIDDLEWARE = []

ROOT_URLCONF = "example.todo_bot_django.urls"
ASGI_APPLICATION = "example.todo_bot_django.asgi.application"

USE_TZ = True
TIME_ZONE = "UTC"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
