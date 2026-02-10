import os

import uvicorn


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.todo_bot_django.settings")


if __name__ == "__main__":
    uvicorn.run(
        "example.todo_bot_django.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
