# Виджеты

## WidgetFactory

`WidgetFactory` создаёт single и multi widgets. Он DI-bound и поддерживает глобальный `include_state_in_metadata`.

```python
widget_factory = WidgetFactory(include_state_in_metadata=False)
single = widget_factory.single(command="/widget_single")
multi = widget_factory.multi(command="/widget_multi", page_size=3)
```

**Важно**
- `command`, `elems_key`, `index_key`, `page_key`, `sync_ids_key`, `prev_label`, `next_label`, `empty_text` должны быть строками.
- Не используйте `SingleMessageWidget.elems_key` или похожие class‑атрибуты в качестве значений. В dataclass со `slots` это `member_descriptor`, не строка.
- Если нужно переопределить ключи — передавайте явные строки или используйте константы `DEFAULT_*` из `pybotx.domain.widgets`.

## Send и update

```python
await bot.send_single_widget(
    bot_id=bot_id,
    chat_id=chat_id,
    widget=single,
    elems=["one", "two"],
    current_index=0,
)

await bot.update_widget(widget=single, message=incoming_message)
```

## Diff updates

`update_widget(..., diff=True)` пропускает апдейт, если страница или индекс не изменились.

```python
await bot.update_widget(widget=single, message=incoming_message, diff=True)
```

## Batched edits

Для multi widget доступно ограничение параллелизма.

```python
await bot.update_widget(
    widget=multi,
    message=incoming_message,
    max_concurrency=3,
)
```

## WidgetSession

Сессии хранят состояние вне metadata и позволяют делать diff без больших payloads.

```python
session = WidgetSession(widget=single, store=widget_state_store, ttl_seconds=3600)
await session.send_single(
    bot=bot,
    bot_id=bot_id,
    chat_id=chat_id,
    elems=["one", "two"],
)

await session.update(bot=bot, message=incoming_message, diff=True)
```

### Bot convenience

Если бот сконфигурирован с `WidgetStateStorePort`, можно создавать сессии через mixin:

```python
session = bot.widget_session(widget=single, ttl_seconds=3600)
```

## Widget state store

Состояние хранится через `WidgetStateStorePort`.

- `InMemoryWidgetStateStore`
- `RedisWidgetStateStore`

Пример DI:

```python
container.config.widgets.state_store.backend.from_value("redis")
container.config.widgets.state_store.redis_prefix.from_value("widget_state:")
container.config.widgets.state_store.serializer.from_value("json")
container.redis_client.override(providers.Object(redis_client))
```

## include_state_in_metadata

Глобальный флаг определяет хранение state в metadata. Дефолт `False`.

```python
container.config.widgets.include_state_in_metadata.from_value(False)
```

## JSON serializer

`RedisWidgetStateStore` по умолчанию использует JSON сериализацию. Это безопаснее, чем pickle.

```python
container.config.widgets.state_store.serializer.from_value("json")
```

Для совместимости можно включить `pickle`:

```python
container.config.widgets.state_store.serializer.from_value("pickle")
```

### Строгая схема и версионирование

JSON-сериализатор валидирует структуру state. При неверных типах будет исключение `ValueError`.

Также используется версионирование формата (`__version__`). Сейчас поддерживаются версии `1` и `2`. Версия записи управляется параметром `serializer_version` в конфиге.

Версия 2 использует поля:

- Single: `items`, `index`
- Multi: `items`, `page`, `sync_ids`

Версия 1 автоматически мигрируется при чтении.
