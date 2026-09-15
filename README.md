# pybotx

*Библиотека для создания чат-ботов и SmartApps для мессенджера eXpress*

[![PyPI version](https://badge.fury.io/py/pybotx.svg)](https://badge.fury.io/py/pybotx)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pybotx)
[![Coverage](https://codecov.io/gh/ExpressApp/pybotx/branch/master/graph/badge.svg)](https://codecov.io/gh/ExpressApp/pybotx/branch/master)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## Особенности

* Простая для использования
* Поддерживает коллбэки BotX
* Легко интегрируется с асинхронными веб-фреймворками
* Полное покрытие тестами
* Полное покрытие аннотациями типов


## Установка

Используя `uv`:

```bash
uv add pybotx
```

Для генерации нового production-ready бота из активного окружения:

```bash
pybotx create bot my-bot
```

Или через `uv`, если окружение не активировано:

```bash
uv run pybotx create bot my-bot
```

Для FSM-шаблона:

```bash
uv run pybotx create bot my-fsm-bot --template production-fastapi-fsm
```

Или в пустой текущей директории:

```bash
pybotx create bot
```

Сгенерированный проект включает:

- FastAPI endpoints для Bot API
- `build_production_bot_preset()` по умолчанию
- `/metrics` с Prometheus registry
- `setup_healthcheck(...)`
- `dependency-injector`
- 4 слоя: `domain / application / infrastructure / presentation`
- пример domain port + repository stub с DI wiring
- `ARCHITECTURE.md` с правилами зависимостей и примерами размещения кода
- тесты, `ruff`, `mypy`, Docker-файлы

Поддерживаемые встроенные шаблоны:

- `production-fastapi`
- `production-fastapi-fsm`

После генерации проекта можно добавить новую команду:

```bash
uv run pybotx create command ping-users --project-dir my-bot
```

Чтобы добавить application service/use case без ручной раскладки по слоям:

```bash
uv run pybotx create service sync-users --project-dir my-bot
```

Чтобы добавить только domain port без concrete adapter:

```bash
uv run pybotx create port billing-gateway --project-dir my-bot
```

Чтобы добавить domain port + infrastructure repository stub с DI wiring:

```bash
uv run pybotx create repository user-profile --project-dir my-bot
```

Если port уже существует, repository можно привязать к нему:

```bash
uv run pybotx create repository stripe-billing-gateway --project-dir my-bot --port billing-gateway
```

Для FSM-шаблона можно сгенерировать новый flow c starter command и тестом:

```bash
uv run pybotx create fsm-flow approval --project-dir my-fsm-bot
```

Для scaffold-проекта можно сгенерировать widget command на базе `WidgetFactory` и `widget_command`:

```bash
uv run pybotx create widget deployment-approval --project-dir my-bot --kind confirm
```

Если нужен готовый flow `command + widget + follow-up services` без ручного wiring:

```bash
uv run pybotx create widget-flow deployment-approval --project-dir my-bot --kind confirm
```

Сгенерированный scaffold использует следующий контракт:

- `src/<package>/container.py` - composition root и DI
- `src/<package>/presentation/` - FastAPI, `pybotx` handlers, widgets, FSM
- `src/<package>/application/services/` - application services/use cases
- `src/<package>/domain/` - доменные модели и контракты, включая `domain/ports/`
- `src/<package>/infrastructure/` - config, repository/adapters, внешние интеграции

**Предупреждение:** Данный проект находится в активной разработке (`0.y.z`) и
его API может быть изменён при повышении минорной версии.

## Документация по виджетам

Подробное и исчерпывающее руководство по всем виджетам и API раннера:

- `/Users/aleksandrosovskii/PycharmProjects/pybotx_stable/WIDGETS.md`

Демо-бот с примерами всех виджетов:

- `/Users/aleksandrosovskii/PycharmProjects/pybotx_stable/example/README.md`


## Информация о мессенджере eXpress и платформе BotX

Документацию по мессенджеру (включая руководство пользователя и администратора)
можно найти на [официальном сайте](https://express.ms/).

Перед тем, как продолжать знакомство с библиотекой `pybotx`,
советуем прочитать данные статьи: Что такое [чат-боты](https://docs.express.ms/chatbots/developer-guide/#%D1%87%D0%B0%D1%82-%D0%B1%D0%BE%D1%82-%D0%B8-smartapp)
и [SmartApp](https://docs.express.ms/smartapps/developer-guide/)
и [Взаимодействие с Bot API и BotX API](https://docs.express.ms/chatbots/developer-guide/api/).
В этих статьях находятся исчерпывающие примеры работы с платформой, которые
легко повторить, используя `pybotx`.

Также не будет лишним ознакомиться с [документацией по плаформе BotX
](https://hackmd.ccsteam.ru/s/botx_platform).


## Примеры готовых проектов на базе pybotx

* [Next Feature Bot](https://github.com/ExpressApp/next-feature-bot) - бот,
  используемый для тестирования функционала платформы BotX.
* [ToDo Bot](https://github.com/ExpressApp/todo-bot) - бот для ведения списка
  дел.
* [Weather SmartApp](https://github.com/ExpressApp/weather-smartapp) -
  приложение для просмотра погоды.


## Минимальный пример бота (интеграция с FastAPI)

```python
from uuid import UUID

from fastapi import FastAPI

# В этом и последующих примерах импорт из `pybotx` будет производиться
# через звёздочку для краткости. Однако, это не является хорошей практикой.
from pybotx import *

collector = HandlerCollector()


@collector.command("/echo", description="Send back the received message body")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(message.body)


# Сюда можно добавлять свои обработчики команд
# или копировать примеры кода, расположенные ниже.


bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            # Не забудьте заменить эти учётные данные на настоящие,
            # когда создадите бота в панели администратора.
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            cts_url="https://cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
)

app: FastAPI = create_fastapi_bot_app(
    bot=bot,
    title="Example bot",
    config=FastAPIBotAppConfig(
        metrics_path="/metrics",
        smartapp_request_path="/smartapps/request",
    ),
)
```

`create_fastapi_bot_app(...)` регистрирует:

- `POST /command`
- `GET /status`
- `POST /notification/callback`
- опционально `POST /smartapps/request`
- опционально `GET /metrics`
- healthcheck routes через `setup_healthcheck(...)`

Если у вас уже есть свой `FastAPI()` объект, можно не создавать новый app, а
подключить `pybotx` в существующий:

```python
from fastapi import FastAPI
from pybotx import *

app = FastAPI()
bot = Bot(collectors=[], bot_accounts=[])
setup_fastapi_bot(
    app,
    bot=bot,
    config=FastAPIBotAppConfig(metrics_path="/metrics"),
)
```

### Healthcheck (опционально, подключается явно)

По умолчанию `pybotx` не регистрирует healthcheck-эндпоинты.
Подключение выполняется явно:

```python
from fastapi import FastAPI
from pybotx import *

app = FastAPI()

healthcheck = setup_healthcheck(app)  # Роуты: /health/ и /health/ready


async def db_readiness_check() -> ReadinessCheckResult:
    # Пример: реальная проверка БД/кеша/внешнего API.
    # Рекомендуется выставлять таймауты внутри проверки.
    return ReadinessCheckResult(status="ok")


healthcheck.add_readiness_check(
    ReadinessCheck(
        name="db",
        check=db_readiness_check,
        critical=True,
        timeout_seconds=0.5,
    ),
)
```

`/health/`:
- `200` — процесс жив (`status=ok`)
- `500` — фатальное состояние (`status=fail`)

`/health/ready`:
- `200` — готов (`status=ok`) или частично деградирован (`status=degraded`)
- `503` — не готов (`status=fail`, если упал хотя бы один `critical` check)

### HTTP-клиент, retry, metrics и tracing

`pybotx` создаёт внутренний `httpx.AsyncClient` с безопасными значениями
`timeout` и `limits`. При необходимости их можно переопределить в `Bot(...)`
через `httpx_timeout` и `httpx_limits`.

`retry_policy` по умолчанию выключен (`None`), то есть повторных попыток нет.
Для включения ретраев передайте `BotXRetryPolicy`. Начиная с текущей версии
retry в `pybotx` стал safe-by-default: если политика включена, библиотека
автоматически повторяет только те BotX-запросы, которые считаются безопасными
для автоматического повтора.

```python
import httpx
from pybotx import *

bot = Bot(
    collectors=[],
    bot_accounts=[],
    httpx_timeout=httpx.Timeout(connect=2.0, read=20.0, write=10.0, pool=1.0),
    httpx_limits=httpx.Limits(max_connections=800, max_keepalive_connections=200),
    retry_policy=BotXRetryPolicy(
        max_attempts=4,
        initial_delay_seconds=0.2,
        max_delay_seconds=5.0,
        jitter_seconds=0.2,
        retryable_status_codes=frozenset({408, 429, 500, 502, 503, 504}),
    ),
)
```

Retry-политика применяется ко всем вызовам BotX API и повторяет запросы при:
- сетевых/timeout ошибках транспорта `httpx`
- HTTP-статусах из `retryable_status_codes`

Важно: BotX async-методы обычно создают side effect и возвращают только `sync_id`,
который появляется уже после успешного ответа. Поэтому ретраи на write-вызовах
могут повторить операцию, если первый запрос был принят BotX, но клиент не получил
ответ. По этой причине `retry_policy=None` оставлен значением по умолчанию, а
в production ретраи лучше включать осознанно и с пониманием семантики конкретного
метода.

По умолчанию используется `SafeBotXRetryRequestPolicy`:
- retry разрешен для read-only запросов (`GET`, `HEAD`, `OPTIONS`)
- отдельно allowlist’ится read-only `POST /api/v3/botx/users/by_email`
- write-операции (`notifications`, `events`, `smartapps`, `create/update/delete`,
  `upload`, `metrics`) по умолчанию не ретраятся автоматически

Это поведение можно переопределить через `retry_request_policy`.

```python
from pybotx import *

bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=RetryAllBotXRequestsPolicy(),
)
```

Для точечного allowlist есть `PathAllowlistBotXRetryRequestPolicy`:

```python
from pybotx import *

bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=PathAllowlistBotXRetryRequestPolicy(
        allowed_requests={
            ("GET", "/api/v3/botx/chats/info"),
            ("GET", "/api/v3/botx/events/{uuid}/status"),
            ("POST", "/api/v3/botx/users/by_email"),
        },
    ),
)
```

Для allowlist по библиотечным операциям есть
`OperationNameAllowlistBotXRetryRequestPolicy`. `operation_name` по умолчанию
равен имени client method class, например `MessageStatusMethod`,
`ChatInfoMethod`, `DirectNotificationMethod`. Для built-in операций есть typed
catalog `BotXOperation`.

```python
from pybotx import *

bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=OperationNameAllowlistBotXRetryRequestPolicy(
        operation_names={
            BotXOperation.MESSAGE_STATUS,
            BotXOperation.CHAT_INFO,
        },
    ),
)
```

Есть готовый preset по built-in safe операциям:

```python
from pybotx import *

bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=KnownSafeBotXRetryRequestPolicy(),
)
```

Для комбинирования safe default с дополнительными исключениями есть
`AnyOfBotXRetryRequestPolicy`:

```python
from pybotx import *

bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=AnyOfBotXRetryRequestPolicy(
        policies=(
            SafeBotXRetryRequestPolicy(),
            OperationNameAllowlistBotXRetryRequestPolicy(
                operation_names={"DirectNotificationMethod"},
            ),
        ),
    ),
)
```

Подробное объяснение решения и рекомендаций для production:
[`docs/retry_safety.md`](docs/retry_safety.md).

Для сокращения boilerplate при сборке production-конфига есть готовые preset
builders:

```python
from pybotx import Bot, build_production_bot_preset

production_preset = build_production_bot_preset()

bot = Bot(
    collectors=[],
    bot_accounts=[],
    **production_preset.as_bot_kwargs(),
)
```

Если нужно отдельно настраивать retry и observability:

```python
from pybotx import (
    Bot,
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

bot = Bot(
    collectors=[],
    bot_accounts=[],
    **production_preset.as_bot_kwargs(),
)
```

Подробности по preset layer:
[`docs/production_presets.md`](docs/production_presets.md).

Если передан собственный `httpx_client`, параметры `httpx_timeout` и
`httpx_limits` передавать нельзя.

Для кастомной логики ретраев можно передать собственный `retry_strategy`
(протокол `BotXRetryStrategy`):

```python
from collections.abc import Callable

from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)
from pybotx import *


class CustomRetryStrategy(BotXRetryStrategy):
    def build_retrying(
        self,
        *,
        retry_policy: BotXRetryPolicy,
        retry_exceptions: tuple[type[BaseException], ...],
        before_sleep: Callable[[RetryCallState], None],
    ) -> AsyncRetrying:
        return AsyncRetrying(
            stop=stop_after_attempt(2),
            wait=wait_fixed(0.1),
            retry=retry_if_exception_type(retry_exceptions),
            before_sleep=before_sleep,
            reraise=True,
        )


bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=5),
    retry_strategy=CustomRetryStrategy(),
)
```

Также доступны opt-in хуки наблюдаемости:
- `metrics_collector`
- `tracing_collector`

Оба параметра по умолчанию выключены (`None`).

Входящая observability в `pybotx` теперь включена по умолчанию:
- Структурированные JSON-логи.
- Корреляционные поля в каждом логе: `trace_id`, `request_id`, `chat_id`, `bot_id`.
- Встроенный ingress-коллектор метрик (`InMemoryIngressMetricsCollector`) в `Bot`.

По умолчанию `request_id` берется из заголовков (`X-Request-Id`, `X-Correlation-Id`,
`Request-Id`) или из `sync_id`, а `trace_id` из (`X-Trace-Id`, `traceparent`, `b3`)
или из `request_id`. Если Express/BotX не присылает такие заголовки, `pybotx`
использует то, что реально есть в протоколе: `sync_id` для Bot API команд и
callback-ов, а для sync smartapp event оставляет поле пустым, пока внешний ingress
не добавит correlation id.

Для ingress-метрик можно передать кастомный collector через:
- `ingress_metrics_collector`

Есть готовая реализация для Prometheus (опциональная зависимость):
- `PrometheusIngressMetricsCollector`
- Требуется `prometheus-client` (`uv add prometheus-client`)

```python
from pybotx import *

ingress_metrics = PrometheusIngressMetricsCollector()

bot = Bot(
    collectors=[],
    bot_accounts=[],
    ingress_metrics_collector=ingress_metrics,
)
```

Ingress-метрики по умолчанию:
- `pybotx_ingress_latency_seconds{command_kind,command_name,outcome}`
- `pybotx_ingress_errors_total{command_kind,command_name,error_type}`
- `pybotx_ingress_rejected_total{command_kind,command_name,reason}`
- `pybotx_ingress_queue_depth`

Готовая реализация метрик для Prometheus:
- `PrometheusMetricsCollector` (latency/error/retry counters с label’ами)
- Требуется `prometheus-client` (`uv add prometheus-client`)

```python
from pybotx import *

prometheus_metrics = PrometheusMetricsCollector()

bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    metrics_collector=prometheus_metrics,
)
```

Можно передать нормализаторы для контроля кардинальности label-ов:

```python
from pybotx import PrometheusMetricsCollector

prometheus_metrics = PrometheusMetricsCollector(
    path_normalizer=lambda url: "/normalized/path",
    reason_normalizer=lambda reason: reason.split(":", 1)[0],
)
```

Метрики по умолчанию:
- `pybotx_botx_requests_total{method,path,status,outcome}`
- `pybotx_botx_request_errors_total{method,path,status,error_type}`
- `pybotx_botx_request_retries_total{method,path,reason}`
- `pybotx_botx_request_latency_seconds{method,path,status}`

Готовая реализация трассировки для OpenTelemetry:
- `OpenTelemetryTracingCollector` (span на запрос + retry events как span events)
- Требуется `opentelemetry-api` (`uv add opentelemetry-api`)
- Для экспорта спанов обычно нужен `opentelemetry-sdk`

```python
from pybotx import *

otel_tracing = OpenTelemetryTracingCollector(tracer_name="mybot.pybotx")

bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    tracing_collector=otel_tracing,
)
```

Также можно обогащать спан через `span_enricher`:

```python
from typing import Any

from pybotx import BotXRequestMetadata, OpenTelemetryTracingCollector


def span_enricher(span: Any, metadata: BotXRequestMetadata) -> None:
    span.set_attribute("bot.name", "mybot")
    span.set_attribute("botx.request_method", metadata.method)


otel_tracing = OpenTelemetryTracingCollector(
    tracer_name="mybot.pybotx",
    span_enricher=span_enricher,
)
```

```python
from pybotx import *


class MetricsCollector:
    def on_request_start(self, metadata: BotXRequestMetadata) -> None:
        # Пример: увеличение счётчика in-flight
        pass

    def on_request_retry(
        self,
        metadata: BotXRequestMetadata,
        retry_event: BotXRetryEvent,
    ) -> None:
        # Пример: счётчик повторов с reason/status
        pass

    def on_request_finish(
        self,
        metadata: BotXRequestMetadata,
        result: BotXRequestResult,
    ) -> None:
        # Пример: latency histogram + error counter
        pass


class TracingCollector:
    def on_request_start(self, metadata: BotXRequestMetadata) -> None:
        pass

    def on_request_retry(
        self,
        metadata: BotXRequestMetadata,
        retry_event: BotXRetryEvent,
    ) -> None:
        pass

    def on_request_finish(
        self,
        metadata: BotXRequestMetadata,
        result: BotXRequestResult,
    ) -> None:
        pass


bot = Bot(
    collectors=[],
    bot_accounts=[],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    metrics_collector=MetricsCollector(),
    tracing_collector=TracingCollector(),
)
```

### Ограничение параллелизма входящих команд (Queue + Semaphore + rejection policy)

`pybotx` обрабатывает входящие команды через bounded pipeline:
- очередь (`Queue`) ограничивает backlog;
- воркеры и `Semaphore` ограничивают параллелизм;
- стратегия перегруза решает, что делать при переполнении очереди.

Параметры задаются через `command_processing_config` в `Bot(...)`.
По умолчанию: `max_concurrency=100`, `max_queue_size=1000`,
`RejectNewBotCommandOverloadStrategy`.

```python
from pybotx import *

bot = Bot(
    collectors=[],
    bot_accounts=[],
    command_processing_config=BotCommandProcessingConfig(
        max_concurrency=64,
        max_queue_size=2000,
        overload_strategy=RejectNewBotCommandOverloadStrategy(),
    ),
)
```

Встроенные стратегии перегруза:
- `RejectNewBotCommandOverloadStrategy` — отклоняет новый входящий command.
- `DropOldestBotCommandOverloadStrategy` — выбрасывает самый старый queued command и принимает новый.

Можно реализовать свою стратегию через `BotCommandOverloadStrategy`:

```python
from pybotx import BotCommandOverloadAction, BotCommandOverloadStrategy


class PreferDropOldestOnBigBurst(BotCommandOverloadStrategy):
    def on_queue_overflow(
        self,
        *,
        queue_size: int,
        queue_max_size: int,
    ) -> BotCommandOverloadAction:
        if queue_size > queue_max_size // 2:
            return BotCommandOverloadAction.DROP_OLDEST
        return BotCommandOverloadAction.REJECT_NEW
```

Если вы `await`-ите `bot.async_execute_bot_command(...)`, при отклонении получите
`BotCommandRejectedError`.

Trade-off: в пике увеличивается latency из-за очереди, зато предсказуемо ограничиваются
память/конкурентность и снижается риск каскадных отказов.

## Примеры


### Получение сообщений

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/api/bot-api/command/))*
```python
from uuid import UUID

from pybotx import *

ADMIN_HUIDS = (UUID("123e4567-e89b-12d3-a456-426614174000"),)

collector = HandlerCollector()


@collector.command("/visible", description="Visible command")
async def visible_handler(_: IncomingMessage, bot: Bot) -> None:
    # Обработчик команды бота. Команда видимая, поэтому описание
    # является обязательным.
    print("Hello from `/visible` handler")


@collector.command("/_invisible", visible=False)
async def invisible_handler(_: IncomingMessage, bot: Bot) -> None:
    # Невидимая команда - не отображается в списке команд бота
    # и не нуждается в описании.
    print("Hello from `/invisible` handler")


async def is_admin(status_recipient: StatusRecipient, bot: Bot) -> bool:
    return status_recipient.huid in ADMIN_HUIDS


@collector.command("/admin-command", visible=is_admin)
async def admin_command_handler(_: IncomingMessage, bot: Bot) -> None:
    # Команда показывается только если пользователь является админом.
    # Список команд запрашивается при открытии чата в приложении.
    print("Hello from `/admin-command` handler")


@collector.default_message_handler
async def default_handler(_: IncomingMessage, bot: Bot) -> None:
    # Если команда не была найдена, вызывается `default_message_handler`,
    # если он определён. Такой обработчик может быть только один.
    print("Hello from default handler")
```


### Получение системных событий

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/api/bot-api/command/#%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D1%8B%D0%B5-%D0%BA%D0%BE%D0%BC%D0%B0%D0%BD%D0%B4%D1%8B))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.chat_created
async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    # Работа с событиями производится с помощью специальных обработчиков.
    # На каждое событие можно объявить только один такой обработчик.
    print(f"Got `chat_created` event: {event}")


@collector.smartapp_event
async def smartapp_event_handler(event: SmartAppEvent, bot: Bot) -> None:
    print(f"Got `smartapp_event` event: {event}")
```


### Получение синхронных SmartApp событий

```python
from pybotx import *

collector = HandlerCollector()


# Обработчик синхронных Smartapp событий, приходящих на эндпоинт `/smartapps/request`
@collector.sync_smartapp_event
async def handle_sync_smartapp_event(
    event: SmartAppEvent, bot: Bot,
) -> BotAPISyncSmartAppEventResultResponse:
    print(f"Got sync smartapp event: {event}")
    return BotAPISyncSmartAppEventResultResponse.from_domain(
        data={},
        files=[],
    )
```


### Middlewares

*(Этот функционал относится исключительно к `pybotx`)*

```python
from httpx import AsyncClient

from pybotx import *

collector = HandlerCollector()


async def custom_api_client_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # До вызова `call_next` (обязателен в каждой миддлвари) располагается
    # код, который выполняется до того, как сообщение дойдёт до
    # своего обработчика.
    async_client = AsyncClient()

    # У сообщения есть объект состояния, в который миддлвари могут добавлять
    # необходимые данные.
    message.state.async_client = async_client

    await call_next(message, bot)

    # После вызова `call_next` выполняется код, когда обработчик уже
    # завершил свою работу.
    await async_client.aclose()


@collector.command(
    "/fetch-resource",
    description="Fetch resource from passed URL",
    middlewares=[custom_api_client_middleware],
)
async def fetch_resource_handler(message: IncomingMessage, bot: Bot) -> None:
    async_client = message.state.async_client
    response = await async_client.get(message.argument)
    print(response.status_code)
```

### Сборщики обработчиков

*(Этот функционал относится исключительно к `pybotx`)*

```python
from uuid import UUID, uuid4

from pybotx import *

ADMIN_HUIDS = (UUID("123e4567-e89b-12d3-a456-426614174000"),)


async def request_id_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    message.state.request_id = uuid4()
    await call_next(message, bot)


async def ensure_admin_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    if message.sender.huid not in ADMIN_HUIDS:
        await bot.answer_message("You are not admin")
        return

    await call_next(message, bot)


# Для того чтобы добавить новый обработчик команды,
# необходимо создать экземпляр класса `HandlerCollector`.
# Позже этот сборщик будет использован при создании бота.
main_collector = HandlerCollector(middlewares=[request_id_middleware])

# У сборщиков (как у обработчиков), могут быть собственные миддлвари.
# Они автоматически применяются ко всем обработчикам данного сборщика.
admin_collector = HandlerCollector(middlewares=[ensure_admin_middleware])

# Сборщики можно включать друг в друга. В данном примере у
# `admin_collector` будут две миддлвари. Первая - его собственная,
# вторая - полученная при включении в `main_collector`.
main_collector.include(admin_collector)
```


### Отправка сообщения

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F))*
```python
from uuid import UUID

from pybotx import *

collector = HandlerCollector()


@collector.command("/answer", description="Answer to sender")
async def answer_to_sender_handler(message: IncomingMessage, bot: Bot) -> None:
    # Т.к. нам известно, откуда пришло сообщение, у `pybotx` есть необходимый
    # контекст для отправки ответа.
    await bot.answer_message("Text")


@collector.command("/send", description="Send message to specified chat")
async def send_message_handler(message: IncomingMessage, bot: Bot) -> None:
    try:
        chat_id = UUID(message.argument)
    except ValueError:
        await bot.answer_message("Invalid chat id")
        return

    # В данном случае нас интересует не ответ, а отправка сообщения
    # в другой чат. Чат должен существовать и бот должен быть в нём.
    try:
        await bot.send_message(
            bot_id=message.bot.id,
            chat_id=chat_id,
            body="Text",
        )
    except Exception as exc:
        await bot.answer_message(f"Error: {exc}")
        return

    await bot.answer_message("Message was send")


@collector.command("/prebuild-answer", description="Answer with prebuild message")
async def prebuild_answer_handler(message: IncomingMessage, bot: Bot) -> None:
    # С помощью OutgoingMessage можно выносить логику
    # формирования ответов в другие модули.
    answer = OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body="Text",
    )
    await bot.send(message=answer)
```


#### Отправка сообщения с кнопками

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-%D1%81-%D0%BA%D0%BD%D0%BE%D0%BF%D0%BA%D0%B0%D0%BC%D0%B8))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/bubbles", description="Send buttons")
async def bubbles_handler(message: IncomingMessage, bot: Bot) -> None:
    # Если вам нужна клавиатура под полем для ввода сообщения,
    # используйте `KeyboardMarkup`. Этот класс имеет те же методы,
    # что и `BubbleMarkup`.
    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/choose",
        label="Red",
        data={"pill": "red"},
        background_color="#FF0000",
    )
    bubbles.add_button(
        command="/choose",
        label="Blue",
        data={"pill": "blue"},
        background_color="#0000FF",
        new_row=False,
    )

    # В кнопку можно добавит ссылку на ресурс,
    # для этого нужно добавить url в аргумент `link`, а `command` оставить пустым,
    # `alert` добавляется в окно подтверждения при переходе по ссылке.
    bubbles.add_button(
        label="Bubble with link",
        alert="alert text",
        link="https://example.com",
    )

    await bot.answer_message(
        "The time has come to make a choice, Mr. Anderson:",
        bubbles=bubbles,
    )
```


#### Упоминание пользователя

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D1%83%D0%BF%D0%BE%D0%BC%D0%B8%D0%BD%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/send-contact", description="Send author's contact")
async def send_contact_handler(message: IncomingMessage, bot: Bot) -> None:
    contact = MentionBuilder.contact(message.sender.huid)
    await bot.answer_message(f"Author is {contact}")


@collector.command("/echo-contacts", description="Send back recieved contacts")
async def echo_contact_handler(message: IncomingMessage, bot: Bot) -> None:
    if not (contacts := message.mentions.contacts):
        await bot.answer_message("Please send at least one contact")
        return

    answer = ", ".join(map(str, contacts))
    await bot.answer_message(answer)
```


#### Отправка файла в сообщении

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0-%D1%84%D0%B0%D0%B9%D0%BB%D0%B0-%D0%B2-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B8))*
```python
from aiofiles.tempfile import NamedTemporaryFile

from pybotx import *

collector = HandlerCollector()


@collector.command("/send-file", description="Send file")
async def send_file_handler(message: IncomingMessage, bot: Bot) -> None:
    # Для создания файла используется file-like object
    # с поддержкой асинхронных операций.
    async with NamedTemporaryFile("wb+") as async_buffer:
        await async_buffer.write(b"Hello, world!\n")
        await async_buffer.seek(0)

        file = await OutgoingAttachment.from_async_buffer(async_buffer, "test.txt")

    await bot.answer_message("Attached file", file=file)


@collector.command("/echo-file", description="Echo file")
async def echo_file_handler(message: IncomingMessage, bot: Bot) -> None:
    if not (attached_file := message.file):
        await bot.answer_message("Attached file is required")
        return

    await bot.answer_message("", file=attached_file)
```

### Редактирование сообщения

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D1%80%D0%B5%D0%B4%D0%B0%D0%BA%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/increment", description="Self-updating widget")
async def increment_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.source_sync_id:  # ID сообщения, в котором была нажата кнопка.
        current_value = message.data["current_value"]
        next_value = current_value + 1
    else:
        current_value = 0
        next_value = 1

    answer_text = f"Counter: {current_value}"
    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/increment",
        label="+",
        data={"current_value": next_value},
    )

    if message.source_sync_id:
        await bot.edit_message(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
            body=answer_text,
            bubbles=bubbles,
        )
    else:
        await bot.answer_message(answer_text, bubbles=bubbles)
```

### Удаление сообщения

*([подробное описание функции](
https://hackmd.ccsteam.ru/s/E9MPeOxjP#%D0%A3%D0%B4%D0%B0%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/deleted-message", description="Self-deleted message")
async def deleted_message_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.source_sync_id:  # ID сообщения, в котором была нажата кнопка.
        await bot.delete_message(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
        )
        return

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/deleted-message",
        label="Delete",
    )

    await bot.answer_message("Self-deleted message", bubbles=bubbles)
```


### Обработчики ошибок

*(Этот функционал относится исключительно к `pybotx`)*

```python
from loguru import logger

from pybotx import *


async def internal_error_handler(
    message: IncomingMessage,
    bot: Bot,
    exc: Exception,
) -> None:
    logger.exception("Internal error:")

    await bot.answer_message(
        "**Error:** internal error, please contact your system administrator",
    )


# Для перехвата исключений существуют специальные обработчики.
# Бот принимает словарь из типов исключений и их обработчиков.
bot = Bot(
    collectors=[],
    bot_accounts=[],
    exception_handlers={Exception: internal_error_handler},
)
```

### Создание чата

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5-%D1%87%D0%B0%D1%82%D0%B0))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/create-group-chat", description="Create group chat")
async def create_group_chat_handler(message: IncomingMessage, bot: Bot) -> None:
    if not (contacts := message.mentions.contacts):
        await bot.answer_message("Please send at least one contact")
        return

    try:
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name="New group chat",
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[contact.entity_id for contact in contacts],
        )
    except (ChatCreationProhibitedError, ChatCreationError) as exc:
        await bot.answer_message(str(exc))
        return

    chat_mention = MentionBuilder.chat(chat_id)
    await bot.answer_message(f"Chat created: {chat_mention}")
```

### Поиск пользователей

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D0%BF%D0%BE%D0%B8%D1%81%D0%BA-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F))*
```python
import dataclasses

from pybotx import *

collector = HandlerCollector()


@collector.command("/my-info", description="Get info of current user")
async def search_user_handler(message: IncomingMessage, bot: Bot) -> None:
    try:
        user_info = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=message.sender.huid,
            trusts_search=True,
        )
    except UserNotFoundError:
        await bot.answer_message("User not found.")
        return

    await bot.answer_message(f"Your info:\n{dataclasses.asdict(user_info)}\n")
```

### Получение списка пользователей

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/examples/#%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B0-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D0%B5%D0%B9-%D0%BD%D0%B0-cts))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/get_users_list", description="Get a list of users")
async def users_list_handler(message: IncomingMessage, bot: Bot) -> None:
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        async for user in users:
            print(user)
```
