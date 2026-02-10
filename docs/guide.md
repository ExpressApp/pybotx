# Полный гайд по pybotx-next

Этот документ собирает в одном месте все ключевые возможности библиотеки и показывает
минимальные рабочие примеры. Он предназначен для сборки в MkDocs и дублирует ссылки
на отдельные страницы, но с единой сквозной логикой.

## Быстрый старт

### Установка

Выберите нужные extras:

- `pybotx[fastapi]`
- `pybotx[aiohttp]`
- `pybotx[django]`
- `pybotx[retry]`
- `pybotx[all]`

### Минимальный запуск FastAPI

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
container.config.widgets.state_store.serializer.from_value(settings.widget_state_serializer)
container.config.widgets.state_store.serializer_version.from_value(
    settings.widget_state_serializer_version,
)
container.config.widgets.include_state_in_metadata.from_value(
    settings.widget_include_state_in_metadata,
)
container.config.demo.enabled.from_value(settings.demo_enabled)
container.config.demo.allow_risky.from_value(settings.demo_allow_risky)

app = container.fastapi_app()
```

## Архитектура и слои

- Domain: модели, правила, исключения, ports
- Application: mixins, use-cases, widgets, orchestration
- Infrastructure: адаптеры HTTP, retry, dedup, storage
- Presentation: web-адаптеры (FastAPI, aiohttp, Django Ninja), контракты

Подробности в `docs/architecture.md`.

## DI через dependency-injector

Основная точка сборки — контейнер. DI связывает порты и конкретные адаптеры.

```python
from dependency_injector import containers, providers
from pybotx import build_bot, BotXAuthVersion
from pybotx.infrastructure.retry_policy import TenacityRetryPolicy

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    retry_policy = providers.Singleton(
        TenacityRetryPolicy,
        enabled=config.http.retry.enabled.as_(bool),
        max_attempts=config.http.retry.max_attempts.as_int(),
        min_delay=config.http.retry.min_delay.as_float(),
        max_delay=config.http.retry.max_delay.as_float(),
        multiplier=config.http.retry.multiplier.as_float(),
        jitter=config.http.retry.jitter.as_(bool),
    )
    bot = providers.Factory(
        build_bot,
        bot_accounts=config.bot.accounts,
        auth_version=config.bot.auth_version.as_(BotXAuthVersion),
        http_backend=config.http.backend,
        retry_policy=retry_policy,
        retry_enabled=config.http.retry.enabled.as_(bool),
    )
```

Подробности в `docs/di.md`.

## Bot API: send, reply, edit

Базовые операции:

```python
await bot.send_message(
    bot_id=bot_id,
    chat_id=chat_id,
    body="Hello",
)

await bot.reply_message(
    bot_id=bot_id,
    sync_id=sync_id,
    body="Reply",
)

await bot.edit_message(
    bot_id=bot_id,
    sync_id=sync_id,
    body="Updated",
)
```

Удобные методы без явных id:

```python
await bot.reply_to(message, body="Reply without ids")
await bot.edit_from(message, body="Edit source message")
```

Подробнее в `docs/bot.md`.

## MessageOptions

`MessageOptions` объединяет delivery-параметры:

```python
from pybotx import MessageOptions

options = MessageOptions(
    silent_response=True,
    markup_auto_adjust=True,
    stealth_mode=True,
    send_push=False,
    ignore_mute=True,
)
```

Можно использовать в `send_message/reply_message/edit_message` и bulk-операциях.

## Builders для сообщений

```python
from pybotx import OutgoingMessageBuilder, ReplyMessageBuilder, EditMessageBuilder

outgoing = (
    OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="Hi")
    .silent()
    .auto_adjust_buttons()
    .build()
)
await bot.send(message=outgoing)

reply = ReplyMessageBuilder.for_incoming_message(message, body="Reply").build()
await bot.reply(message=reply)

edit = EditMessageBuilder.for_incoming_source_id(message).with_body("Edit").build()
await bot.edit(message=edit)
```

Полный список в `docs/builders.md`.

## Bulk операции

```python
messages = [
    OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="1").build(),
    OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="2").build(),
]
result = await bot.bulk_send(messages=messages, max_concurrency=3)
```

Есть `bulk_reply` и `bulk_edit`, а также общий `MessageOptions`.
Подробнее в `docs/bulk.md`.

## TextBuilder и mentions

```python
from pybotx import TextBuilder

text = (
    TextBuilder()
    .append("Hi ")
    .mention_user_named("Alice", user_id)
    .append(", welcome!")
    .build()
)
```

Подробнее в `docs/text.md`.

## AttachmentFactory

```python
from pybotx import AttachmentFactory

factory = AttachmentFactory(...)
attachment = await factory.from_path("/tmp/report.pdf")
message = OutgoingMessageBuilder(
    bot_id=bot_id,
    chat_id=chat_id,
    body="Report",
).with_file(attachment).build()
await bot.send(message=message)
```

Также доступны `from_bytes` и `from_file`.
Подробнее в `docs/attachments.md`.

## Виджеты

### WidgetFactory

```python
from pybotx import WidgetFactory

factory = WidgetFactory(include_state_in_metadata=False)
single = factory.single(command="/widget_single")
multi = factory.multi(command="/widget_multi", page_size=3)
```

### Send и update

```python
await bot.send_single_widget(
    bot_id=bot_id,
    chat_id=chat_id,
    widget=single,
    elems=["one", "two"],
    current_index=0,
)

await bot.update_widget(widget=single, message=incoming_message, diff=True)
```

### WidgetSession

```python
session = bot.widget_session(widget=single, ttl_seconds=3600)
await session.send_single(
    bot=bot,
    bot_id=bot_id,
    chat_id=chat_id,
    elems=["one", "two"],
)
await session.update(bot=bot, message=incoming_message, diff=True)
```

### State store и сериализация

```python
container.config.widgets.state_store.backend.from_value("redis")
container.config.widgets.state_store.serializer.from_value("json")
container.config.widgets.state_store.serializer_version.from_value(2)
```

Подробности в `docs/widgets.md`.

## Bot command links

Ссылки для открытия чата с ботом и отправки команды:

```python
from pybotx import build_bot_command_link

link = build_bot_command_link(
    huid=bot_huid,
    command="/start",
    body="/start",
)
```

## HTTP, retry, timeouts

HTTP-бэкенд и retry управляются через конфиг.
Подробнее в `docs/http.md`.

## Web adapters

Доступны FastAPI, aiohttp и Django Ninja адаптеры.
Подробнее в `docs/adapters.md`.

## Todo-бот примеры

См. `docs/examples_todo.md` и папку `example/todo_bot`.

## FAQ / Best Practices

См. `docs/faq.md`.
