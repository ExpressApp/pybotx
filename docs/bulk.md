# Bulk операции

Bulk операции дают управление параллелизмом и агрегированные результаты.

## Bulk send

```python
messages = [
    OutgoingMessageBuilder(...).build(),
    OutgoingMessageBuilder(...).build(),
]
result = await bot.bulk_send(messages=messages, max_concurrency=5)

print(len(result.successes), len(result.failures))
```

## Bulk reply

```python
messages = [
    ReplyMessageBuilder.for_incoming_message(message, body="one").build(),
    ReplyMessageBuilder.for_incoming_message(message, body="two").build(),
]
result = await bot.bulk_reply(messages=messages, max_concurrency=2)
```

## Bulk edit

```python
messages = [
    EditMessageBuilder.for_incoming_source_id(message).with_body("edit").build()
]
result = await bot.bulk_edit(messages=messages, max_concurrency=2)
```

## Общие MessageOptions

Bulk операции принимают `options` как базовый набор флагов. Явные поля в сообщениях имеют приоритет.

```python
options = MessageOptions(silent_response=True, send_push=False)
await bot.bulk_send(messages=messages, options=options)
```

