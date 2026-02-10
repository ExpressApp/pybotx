# Архитектура и слои

## Модель слоёв

Мы придерживаемся 4 слоёв и строгого направления зависимостей:

1. Domain
2. Application
3. Infrastructure
4. Presentation

Зависимости направлены только сверху вниз. Domain не зависит ни от чего. Application зависит от Domain. Infrastructure и Presentation зависят от Application и Domain. Контракты разделены на inbound и outbound, чтобы убрать боковые зависимости.

## Что где живёт

### Domain

- Чистые бизнес-модели и value objects
- Доменные порты и ошибки
- Модели и builders сообщений
- Доменная логика виджетов
- Утилиты для текста и упоминаний

### Application

- Фасад бота
- Handler collectors
- WidgetFactory и WidgetSession
- Оркестрация use-cases

### Infrastructure

- HTTP клиенты и retry policy
- Реализация BotX API
- JWT encoder и verifier
- Хранилища и adapters
- AttachmentFactory implementation

### Presentation

- Web adapters
- DTO для входящих payloads
- Framework-specific роутинг и lifecycle

## Контракты

Контракты разделены на inbound и outbound, чтобы убрать зависимость domain от транспортных DTO.

- Inbound: presentation payloads
- Outbound: infrastructure API payloads

## Порты и адаптеры

Все внешние зависимости accessed через порты. Infrastructure реализует адаптеры этих портов.

Примеры:

- `WidgetStateStorePort` -> `InMemoryWidgetStateStore` / `RedisWidgetStateStore`
- `JwtEncoderPort` -> `PyJwtEncoder`
- `JwtVerifierPort` -> `PyJwtVerifier`
- `HttpClientPort` -> `HttpxClientAdapter` / `AioHttpClientAdapter`

## DI границы

DI делается только в контейнерах. Все runtime настройки прокидываются в `container.config`.

