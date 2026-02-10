# Bot API

Основные методы `Bot` и ключевые изменения.

## Reply и edit sugar

Без contextvars и без ручного проброса ID.

```python
await bot.reply_to(
    message,
    body="Thanks!",
)

await bot.edit_from(
    message,
    body="Updated text",
)
```

## Bulk операции

### Bulk send

```python
messages = [
    OutgoingMessageBuilder(...).build(),
    OutgoingMessageBuilder(...).build(),
]
result = await bot.bulk_send(messages=messages, max_concurrency=5)
```

### Bulk reply

```python
messages = [
    ReplyMessageBuilder.for_incoming_message(message, body="one").build(),
    ReplyMessageBuilder.for_incoming_message(message, body="two").build(),
]
result = await bot.bulk_reply(messages=messages, max_concurrency=3)
```

### Bulk с общими MessageOptions

Bulk операции принимают `options`. Значения в отдельных сообщениях имеют приоритет над общими.

```python
options = MessageOptions(silent_response=True, send_push=False)
result = await bot.bulk_send(messages=messages, options=options)
```

## Request verification

`RequestVerifier` доступен как публичный интерфейс и может быть заменён через DI.

## Логирование

Логгер можно инжектить через контейнер. Порт логгера поддерживает `enable()` и `disable()`.

