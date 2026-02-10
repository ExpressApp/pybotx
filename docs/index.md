# pybotx-next

Production-grade Python фреймворк для ботов Express с чистой архитектурой, DI и несколькими веб-адаптерами.

Документация ниже охватывает обновлённую архитектуру и весь функционал, который мы добавили.

## Быстрый старт

### Установка

Используйте нужные extras в зависимости от стека:

- `pybotx[fastapi]`
- `pybotx[aiohttp]`
- `pybotx[django]`
- `pybotx[retry]`
- `pybotx[all]`

### Минимальный бот (FastAPI)

```python
from dependency_injector import providers
from pybotx import BotAccountWithSecret

from example.todo_bot.config import load_settings
from example.todo_bot.container import TodoBotContainer

settings = load_settings()
container = TodoBotContainer()
container.config.bot.accounts.from_value(
    [
        BotAccountWithSecret(
            id=settings.bot_id,
            cts_url=settings.cts_url,
            secret_key=settings.bot_secret,
        )
    ]
)
container.config.bot.auth_version.from_value(settings.auth_version)
container.config.bot.verify_requests.from_value(settings.verify_requests)
container.config.http.backend.from_value(settings.http_backend)
container.config.http.timeout.from_value(settings.http_timeout)
container.config.http.retry.enabled.from_value(settings.retry_enabled)
container.config.http.retry.backend.from_value(settings.retry_backend)
container.config.http.retry.retry_stream.from_value(settings.retry_stream)
container.config.http.retry.max_attempts.from_value(settings.retry_max_attempts)
container.config.http.retry.min_delay.from_value(settings.retry_min_delay)
container.config.http.retry.max_delay.from_value(settings.retry_max_delay)
container.config.http.retry.multiplier.from_value(settings.retry_multiplier)
container.config.http.retry.jitter.from_value(settings.retry_jitter)
container.config.storage.backend.from_value(settings.storage_backend)
container.config.bot.dedup.enabled.from_value(settings.dedup_enabled)
container.config.bot.dedup.ttl.from_value(settings.dedup_ttl)
container.config.bot.dedup.backend.from_value(settings.dedup_backend)
container.config.widgets.state_store.backend.from_value(settings.widget_state_backend)
container.config.widgets.state_store.redis_prefix.from_value(
    settings.widget_state_redis_prefix,
)
container.config.widgets.include_state_in_metadata.from_value(
    settings.widget_include_state_in_metadata,
)
container.config.demo.enabled.from_value(settings.demo_enabled)
container.config.demo.allow_risky.from_value(settings.demo_allow_risky)

if settings.use_raw_http_client:
    if settings.http_backend == "aiohttp":
        from pybotx.infrastructure.aiohttp_client import AioHttpClientAdapter
        raw_http_client = AioHttpClientAdapter(timeout=settings.http_timeout)
    else:
        import httpx
        from pybotx.infrastructure.httpx_client import HttpxClientAdapter
        raw_http_client = HttpxClientAdapter(httpx.AsyncClient(timeout=settings.http_timeout))
    container.raw_http_client.override(providers.Object(raw_http_client))

app = container.fastapi_app()
```

## Что внутри

- Слои и границы по Clean Architecture
- DI через `dependency-injector`
- Переиспользуемые порты и адаптеры
- HTTP backend selection и retry policy
- Явные интерфейсы JWT encoder/verifier
- Builder-паттерны для сообщений
- Bulk операции с ограничением параллелизма
- Виджеты с diff и session-режимом
- Redis-хранилище состояния виджетов
- FastAPI, aiohttp и Django Ninja адаптеры
- Расширенный пример todo-бота

## Навигация

- Архитектура и слои: `architecture.md`
- Dependency Injection: `di.md`
- Bot API: `bot.md`
- Message builders и options: `builders.md`
- Bulk операции: `bulk.md`
- Виджеты и сессии: `widgets.md`
- TextBuilder и mentions: `text.md`
- AttachmentFactory: `attachments.md`
- HTTP, retry и timeouts: `http.md`
- Веб-адаптеры: `adapters.md`
- Todo бот: `examples_todo.md`
- Миграции и breaking changes: `migration.md`
