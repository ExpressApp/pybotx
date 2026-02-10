# Widgets Guide

Этот документ дополняет `widgets.md` практическими сценариями и шаблонами использования.

## Базовые виджеты

```python
from pybotx import WidgetFactory

factory = WidgetFactory(include_state_in_metadata=False)
single = factory.single(command="/widget_single")
multi = factory.multi(command="/widget_multi", page_size=3)
```

**Важно**
- Все key/label параметры должны быть строками.
- Не передавайте `SingleMessageWidget.elems_key` или `MultiMessageWidget.page_key` как значения. В dataclass со `slots` это `member_descriptor`.

## Отправка и обновление

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

## Diff и батч‑редактирование

```python
await bot.update_widget(
    widget=multi,
    message=incoming_message,
    diff=True,
    max_concurrency=3,
)
```

## WidgetSession

Сессия хранит state вне metadata, что уменьшает payload и позволяет гибко обновлять UI.

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

## State store и сериализация

```python
container.config.widgets.state_store.backend.from_value("redis")
container.config.widgets.state_store.serializer.from_value("json")
container.config.widgets.state_store.serializer_version.from_value(2)
```

## include_state_in_metadata

По умолчанию `False`. Включайте только если нужен state внутри metadata.

```python
container.config.widgets.include_state_in_metadata.from_value(False)
```
