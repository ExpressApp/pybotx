# Веб-адаптеры

## FastAPI

```python
from fastapi import FastAPI
from pybotx import Bot, wrap_asgi_app
from pybotx.presentation.fastapi import FastAPIAdapter

adapter = FastAPIAdapter(bot, verify_requests=True)
app = FastAPI(title="Todo Bot")
app.include_router(adapter.router)
app = wrap_asgi_app(app, bot)
```

Если не используете `wrap_asgi_app`, подключите lifecycle вручную:

```python
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)
```

## aiohttp

```python
from aiohttp import web
from pybotx.presentation.aiohttp import AiohttpAdapter

adapter = AiohttpAdapter(bot, verify_requests=True)
app = web.Application()
app.add_routes(adapter.routes)
```

## Django Ninja (ASGI)

```python
from ninja import NinjaAPI
from pybotx.presentation.django_ninja import DjangoNinjaAdapter

api = NinjaAPI()
adapter = DjangoNinjaAdapter(bot, verify_requests=True)
api.add_router("/", adapter.router)
```

Для ASGI убедитесь, что `bot.startup()` и `bot.shutdown()` вызываются в lifecycle.

