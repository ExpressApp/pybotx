# Production presets in pybotx

## Зачем это нужно

После добавления retry, metrics и tracing в `pybotx` основной сценарий выглядел
правильно, но был слишком многословным:

```python
bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
    retry_policy=BotXRetryPolicy(...),
    retry_request_policy=...,
    metrics_collector=PrometheusMetricsCollector(...),
    tracing_collector=OpenTelemetryTracingCollector(...),
    ingress_metrics_collector=PrometheusIngressMetricsCollector(...),
)
```

Для production это нормальная мощность API, но плохой DX для типового проекта.
Поэтому в библиотеку добавлен отдельный factory/preset layer.

## Что добавлено

- `BotRetryPreset`
- `BotObservabilityPreset`
- `BotProductionPreset`
- `build_production_retry_preset()`
- `build_production_observability_preset()`
- `build_production_bot_preset()`

Каждый preset - immutable value object, который можно превратить в kwargs для
`Bot` через `as_bot_kwargs()`.

## Базовый сценарий

```python
from pybotx import Bot, build_production_bot_preset

production_preset = build_production_bot_preset()

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
    **production_preset.as_bot_kwargs(),
)
```

По умолчанию такой preset собирает:

- production retry preset;
- `PrometheusMetricsCollector` для outgoing BotX requests;
- `PrometheusIngressMetricsCollector` для ingress queue/latency/errors/rejected;
- `OpenTelemetryTracingCollector` для outgoing BotX requests.

Для этого нужны optional dependencies:

```bash
uv add prometheus-client opentelemetry-api
```

## Retry preset

`build_production_retry_preset()` включает:

- `BotXRetryPolicy` с production defaults из `pybotx`;
- composable `retry_request_policy`:
  - `SafeBotXRetryRequestPolicy()`
  - `KnownSafeBotXRetryRequestPolicy()`

Это дает такой результат:

- generic safe retry для `GET/HEAD/OPTIONS`;
- safe retry для read-only `POST`, которые уже известны библиотеке;
- safe-by-default поведение для стандартных built-in методов `pybotx`.

Пример кастомизации:

```python
from pybotx import BotXOperation, build_production_retry_preset

retry_preset = build_production_retry_preset(
    max_attempts=5,
    extra_safe_operations={BotXOperation.DIRECT_NOTIFICATION},
)
```

Если передан свой `retry_request_policy`, одновременно передавать
`extra_safe_requests` или `extra_safe_operations` нельзя: builder это запрещает,
чтобы не было неявного precedence.

## Observability preset

`build_production_observability_preset()` по умолчанию собирает:

- outgoing Prometheus metrics;
- ingress Prometheus metrics;
- OpenTelemetry tracing.

Пример отключить tracing, но оставить metrics:

```python
from pybotx import build_production_observability_preset

observability_preset = build_production_observability_preset(
    enable_open_telemetry_tracing=False,
)
```

Пример наоборот, только tracing:

```python
from pybotx import build_production_observability_preset

observability_preset = build_production_observability_preset(
    enable_prometheus_metrics=False,
    tracer_name="mybot.pybotx",
)
```

Если выключить оба backend одновременно, builder поднимет `ValueError`.

## Сборка полного production preset

Если нужен полный preset с кастомизированными частями:

```python
from pybotx import (
    build_production_bot_preset,
    build_production_observability_preset,
    build_production_retry_preset,
)

production_preset = build_production_bot_preset(
    retry_preset=build_production_retry_preset(max_attempts=5),
    observability_preset=build_production_observability_preset(
        enable_open_telemetry_tracing=False,
    ),
)
```

## Почему это отдельный layer, а не новый аргумент в Bot

Выбран паттерн `Factory + Value Object`.

Причина:

- не раздувает `Bot.__init__` еще сильнее;
- не вводит сложные precedence rules между `preset` и обычными kwargs;
- оставляет текущий `Bot` API обратно совместимым;
- упрощает документацию и тестирование.

Альтернатива была такой:

- добавить `production_preset=` в `Bot`

Но тогда пришлось бы отдельно определять:

- кто кого переопределяет;
- можно ли смешивать preset и raw kwargs;
- как валидировать конфликтующие параметры.

Для текущей задачи отдельный preset layer проще и чище.
