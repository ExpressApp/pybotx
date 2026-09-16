# Retry safety in pybotx

## Зачем это понадобилось

У BotX есть важная особенность: многие методы не просто возвращают данные, а
создают side effect в Express/BotX. Например:

- отправка сообщения
- отправка smartapp event
- создание чата/треда
- изменение сообщения
- загрузка файла

Для таких методов серверный side effect может уже произойти, даже если клиент не
успел получить HTTP-ответ из-за timeout, разрыва соединения или временной ошибки
сети.

В результате слепой automatic retry может привести к дубликатам:

1. бот отправил запрос в BotX;
2. BotX принял запрос и создал side effect;
3. ответ не дошел до бота;
4. клиент повторил запрос;
5. BotX выполнил операцию еще раз.

Особенно это критично для async методов, где `sync_id` появляется только после
успешного HTTP-ответа, а финальный результат приходит отдельно через callback.

## Что делает pybotx теперь

В `pybotx` retry разделен на две части:

- `retry_policy`
  Задает backoff, jitter, лимит попыток и retryable HTTP status codes.
- `retry_request_policy`
  Решает, какие именно BotX-запросы вообще разрешено автоматически повторять.

Если `retry_policy=None`, retry полностью выключен.

Если `retry_policy` включен, но `retry_request_policy` не передан, `pybotx`
использует безопасный default:

- `SafeBotXRetryRequestPolicy`

Кроме path-based allowlist теперь есть operation-based allowlist:

- `OperationNameAllowlistBotXRetryRequestPolicy`
- `KnownSafeBotXRetryRequestPolicy`

`operation_name` в metadata равен имени client method class, например:

- `MessageStatusMethod`
- `ChatInfoMethod`
- `DirectNotificationMethod`

Для built-in client methods есть typed catalog:

- `BotXOperation`

## SafeBotXRetryRequestPolicy

Это default policy для production.

Она разрешает retry только для read-only запросов:

- `GET`
- `HEAD`
- `OPTIONS`

И отдельно allowlist’ит read-only POST:

- `POST /api/v3/botx/users/by_email`

Почему allowlist нужен отдельно: в BotX есть read-операции, которые исторически
идут через `POST`, поэтому правило только по HTTP-методу было бы слишком грубым.

`SafeBotXRetryRequestPolicy` также можно расширять через:

- `extra_safe_requests`
- `extra_safe_operation_names`

## Что safe policy не retry'ит

По умолчанию не ретраятся операции, у которых высокий риск дублирования side
effect:

- notifications
- events
- smartapps mutations
- create/update/delete operations
- file upload
- metrics ingestion

Это осознанное решение: лучше не повторить потенциально unsafe операцию, чем
получить скрытые дубликаты и несогласованное состояние.

## Когда использовать RetryAllBotXRequestsPolicy

`RetryAllBotXRequestsPolicy` нужен только если вы точно понимаете последствия и
берете ответственность за идемпотентность на себя.

Подходит, если:

- у вас есть внешний слой дедупликации;
- конкретный BotX endpoint безопасен в вашей интеграции;
- вы повторяете только те операции, для которых дубли допустимы.

Пример:

```python
from pybotx import Bot, BotXRetryPolicy, RetryAllBotXRequestsPolicy

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=RetryAllBotXRequestsPolicy(),
)
```

## Когда использовать PathAllowlistBotXRetryRequestPolicy

Если нужен не глобальный `retry all`, а точечный control plane, используйте
`PathAllowlistBotXRetryRequestPolicy`.

Пример:

```python
from pybotx import (
    Bot,
    BotXRetryPolicy,
    PathAllowlistBotXRetryRequestPolicy,
)

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
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

Особенности:

- policy нормализует UUID-сегменты пути в вид `/{uuid}`;
- allowlist задается по паре `(method, normalized_path)`;
- это дает стабильную low-cardinality настройку без привязки к конкретным id.

## Когда использовать OperationNameAllowlistBotXRetryRequestPolicy

Если вы хотите описывать retry-политику в терминах библиотеки, а не HTTP path,
используйте `OperationNameAllowlistBotXRetryRequestPolicy`.

Пример:

```python
from pybotx import (
    Bot,
    BotXOperation,
    BotXRetryPolicy,
    OperationNameAllowlistBotXRetryRequestPolicy,
)

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=OperationNameAllowlistBotXRetryRequestPolicy(
        operation_names={
            BotXOperation.MESSAGE_STATUS,
            BotXOperation.CHAT_INFO,
        },
    ),
)
```

Плюсы:

- конфиг ближе к публичным возможностям `pybotx`;
- не нужно помнить raw path;
- меньше риска ошибиться в URL version/prefix.

Минусы:

- имя класса зависит от library API;
- если в библиотеке появится новый client method class, allowlist надо обновить.

## Когда использовать KnownSafeBotXRetryRequestPolicy

Если вам нужен минимальный DX friction и library-provided preset, используйте
`KnownSafeBotXRetryRequestPolicy`.

Он разрешает retry только для built-in safe operations из каталога `BotXOperation`.

Пример:

```python
from pybotx import Bot, BotXRetryPolicy, KnownSafeBotXRetryRequestPolicy

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=KnownSafeBotXRetryRequestPolicy(),
)
```

Если нужно расширить preset:

```python
from pybotx import (
    Bot,
    BotXOperation,
    BotXRetryPolicy,
    KnownSafeBotXRetryRequestPolicy,
)

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
    retry_policy=BotXRetryPolicy(max_attempts=3),
    retry_request_policy=KnownSafeBotXRetryRequestPolicy(
        extra_operations={BotXOperation.DIRECT_NOTIFICATION},
    ),
)
```

Такое расширение считается risky и на startup библиотека пишет warning.

## Known-safe matrix

Built-in safe catalog сейчас включает:

| Operation | operation_name | Default retry |
| --- | --- | --- |
| `BotXOperation.BOTS_LIST` | `BotsListMethod` | yes |
| `BotXOperation.CHAT_INFO` | `ChatInfoMethod` | yes |
| `BotXOperation.DOWNLOAD_FILE` | `DownloadFileMethod` | yes |
| `BotXOperation.GET_STICKER` | `GetStickerMethod` | yes |
| `BotXOperation.GET_STICKER_PACK` | `GetStickerPackMethod` | yes |
| `BotXOperation.GET_STICKER_PACKS` | `GetStickerPacksMethod` | yes |
| `BotXOperation.LIST_CHATS` | `ListChatsMethod` | yes |
| `BotXOperation.MESSAGE_STATUS` | `MessageStatusMethod` | yes |
| `BotXOperation.PERSONAL_CHAT` | `PersonalChatMethod` | yes |
| `BotXOperation.SEARCH_USER_BY_EMAIL_GET` | `SearchUserByEmailMethod` | yes |
| `BotXOperation.SEARCH_USER_BY_EMAIL_POST` | `SearchUserByEmailPostMethod` | yes |
| `BotXOperation.SEARCH_USER_BY_EMAILS` | `SearchUserByEmailsMethod` | yes |
| `BotXOperation.SEARCH_USER_BY_HUID` | `SearchUserByHUIDMethod` | yes |
| `BotXOperation.SEARCH_USER_BY_LOGIN` | `SearchUserByLoginMethod` | yes |
| `BotXOperation.SEARCH_USER_BY_OTHER_ID` | `SearchUserByOtherIdMethod` | yes |
| `BotXOperation.SMARTAPPS_LIST` | `SmartAppsListMethod` | yes |
| `BotXOperation.USERS_AS_CSV` | `UsersAsCSVMethod` | yes |

Примеры built-in risky operations:

| Operation | operation_name | Why not safe by default |
| --- | --- | --- |
| `BotXOperation.DIRECT_NOTIFICATION` | `DirectNotificationMethod` | creates side effect |
| `BotXOperation.DIRECT_NOTIFICATION_SYNC` | `DirectNotificationSyncMethod` | creates side effect |
| `BotXOperation.INTERNAL_BOT_NOTIFICATION` | `InternalBotNotificationMethod` | async callback semantics |
| `BotXOperation.SMARTAPP_EVENT` | `SmartAppEventMethod` | creates side effect |
| `BotXOperation.CREATE_CHAT` | `CreateChatMethod` | mutation |
| `BotXOperation.EDIT_EVENT` | `EditEventMethod` | mutation |
| `BotXOperation.FILES_UPLOAD_FILE` | `FilesUploadFileMethod` | upload / side effect |

## Комбинирование политик

Для composable-конфигурации в `pybotx` есть `AnyOfBotXRetryRequestPolicy`.

Пример: сохранить safe default, но отдельно разрешить retry для конкретной
операции:

```python
from pybotx import (
    AnyOfBotXRetryRequestPolicy,
    Bot,
    BotXRetryPolicy,
    OperationNameAllowlistBotXRetryRequestPolicy,
    SafeBotXRetryRequestPolicy,
)

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
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

## Почему не Chain of Responsibility

Для текущей задачи в `pybotx` выбрана комбинация паттернов:

- `Strategy`
  `BotXRetryRequestPolicy` инкапсулирует правило принятия решения.
- `Composite`
  `AnyOfBotXRetryRequestPolicy` позволяет собирать несколько policy вместе.

`Chain of Responsibility` здесь пока избыточен, потому что у нас сейчас простая
булева модель: policy либо разрешает retry, либо нет.

CoR стал бы оправдан, если бы понадобилась трехсостояний модель:

- `allow`
- `deny`
- `abstain`

И если бы была важна именно приоритетная последовательность правил, например:

1. глобальный deny-list;
2. затем operation allowlist;
3. затем fallback safe default.

Пока такая сложность в `pybotx` не нужна. Для production-конфига с текущими
требованиями `Strategy + Composite` дает более простой и предсказуемый API.

## Рекомендация для production

Рекомендуемый порядок:

1. Начинать с `SafeBotXRetryRequestPolicy`.
2. Добавлять `PathAllowlistBotXRetryRequestPolicy` только для тех endpoint'ов,
   чья семантика вам точно понятна.
3. Использовать `RetryAllBotXRequestsPolicy` только как явный opt-in.
4. Для write-операций опираться не на retry, а на:
   - timeout/limits;
   - callback handling;
   - observability;
   - прикладную идемпотентность на вашей стороне, если она действительно нужна.

## Как это связано с observability

Retry events по-прежнему попадают в:

- `PrometheusMetricsCollector`
- `OpenTelemetryTracingCollector`

Но теперь retry event означает не просто "был retry policy", а
"был retry policy и этот запрос был признан допустимым для автоматического
повтора".

Это делает telemetry ближе к реальному operational поведению.
