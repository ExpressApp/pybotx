# Миграции и breaking changes

## include_state_in_metadata

Дефолт стал `False`.

- Раньше state виджетов сохранялся в metadata
- Теперь state хранится в `WidgetStateStorePort` по умолчанию

Чтобы вернуть старое поведение:

```python
container.config.widgets.include_state_in_metadata.from_value(True)
```

## Контракты

Контракты разделены на inbound и outbound. Обновите импорты на новые пути.

## HTTP aliases

Старые `Http*` алиасы удалены в пользу явных интерфейсов.

## BotX API facade

Внутренний `_build_method` заменён на `BotXApiMethodFactory`.

## Raw handlers

Raw-обработчики перенесены в adapters. Используйте framework adapters или публичные raw handlers.

