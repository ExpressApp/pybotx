# Dependency Injection

Проект использует `dependency-injector` как composition root. Контейнеры предоставляют конфиги и провайдеры для всех портов.

## Core контейнер

`pybotx.container.BotXContainer` даёт:

- HTTP backend selector
- Retry policy selector
- JWT encoder/verifier
- Request verifier
- BotX API facade
- WidgetFactory и WidgetStateStore

## Частые overrides

### Custom HTTP client

```python
from dependency_injector import providers
from pybotx.container import BotXContainer

container = BotXContainer()
container.config.http.backend.from_value("httpx")
container.http_client.override(providers.Object(custom_http_client))
```

### Custom raw HTTP client

```python
container.raw_http_client.override(providers.Object(custom_raw_http_client))
```

### Custom retry policy

```python
container.retry_policy.override(providers.Object(custom_retry_policy))
```

### Custom widget state store

```python
container.widget_state_store.override(providers.Object(custom_widget_store))
```

### Custom logger

```python
container.logger.override(providers.Object(custom_logger))
```

## Пример: todo_bot

В todo-bot контейнере:

- `widget_factory` создаётся через DI
- `widget_session_factory` привязан к `widget_state_store`
- demo-флаги прокидываются через `config.demo.*`

Смотрите `/Users/aleksandrosovskii/PycharmProjects/pybotx/example/todo_bot/container.py`.

