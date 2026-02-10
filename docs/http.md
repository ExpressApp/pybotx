# HTTP, Retry, Timeouts

## HTTP backend

Выбор backend через конфиг:

```python
container.config.http.backend.from_value("httpx")
# или
container.config.http.backend.from_value("aiohttp")
```

## HTTP_TIMEOUT и raw_http_client

Можно инжектить raw client напрямую:

```python
container.raw_http_client.override(providers.Object(custom_raw_http_client))
```

Или настроить timeout для встроенных адаптеров:

```python
container.config.http.timeout.from_value(60.0)
```

## Retry policy

Доступны:

- `noop`
- `tenacity`

Пример настройки:

```python
container.config.http.retry.enabled.from_value(True)
container.config.http.retry.backend.from_value("tenacity")
container.config.http.retry.retry_stream.from_value(True)
container.config.http.retry.max_attempts.from_value(3)
container.config.http.retry.min_delay.from_value(0.1)
container.config.http.retry.max_delay.from_value(2.0)
container.config.http.retry.multiplier.from_value(2.0)
container.config.http.retry.jitter.from_value(True)
```

