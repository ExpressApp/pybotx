# Middleware

В этом разделе описаны middleware (промежуточное ПО) в pybotx, их настройка и использование.

## Введение

Middleware (промежуточное ПО) — это функции, которые выполняются до и после обработки сообщения основным обработчиком. Они позволяют:

- Предобрабатывать входящие сообщения
- Добавлять данные в контекст сообщения
- Перехватывать и изменять ответы
- Выполнять действия после обработки сообщения (логирование, метрики и т.д.)
- Внедрять зависимости в обработчики (Dependency Injection)

В pybotx middleware могут быть применены к отдельным обработчикам или ко всем обработчикам коллектора.

## Создание middleware

Middleware в pybotx — это асинхронная функция, принимающая три параметра:
- `message: IncomingMessage` — входящее сообщение
- `bot: Bot` — экземпляр бота
- `call_next: IncomingMessageHandlerFunc` — функция для вызова следующего middleware или обработчика

```python
from pybotx import IncomingMessage, Bot, IncomingMessageHandlerFunc

async def logging_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # Код, выполняемый до обработки сообщения
    print(f"Получено сообщение: {message.body}")
    
    # Вызов следующего middleware или обработчика
    await call_next(message, bot)
    
    # Код, выполняемый после обработки сообщения
    print("Сообщение обработано")
```

## Цепочка middleware

Middleware выполняются в порядке их регистрации. Каждый middleware может вызвать следующий middleware с помощью функции `call_next` или прервать цепочку, не вызывая `call_next`.

```mermaid
sequenceDiagram
    participant Client as BotX API
    participant Bot as Bot
    participant MW1 as Middleware 1
    participant MW2 as Middleware 2
    participant Handler as Обработчик

    Client->>Bot: Сообщение
    Bot->>MW1: Передача сообщения
    MW1->>MW2: call_next
    MW2->>Handler: call_next
    Handler-->>MW2: Возврат
    MW2-->>MW1: Возврат
    MW1-->>Bot: Возврат
    Bot-->>Client: Ответ
```

Middleware можно применять на разных уровнях:

1. **Глобально для всех обработчиков коллектора**:

```python
from pybotx import HandlerCollector

collector = HandlerCollector(middlewares=[logging_middleware, auth_middleware])
```

2. **Для конкретного обработчика**:

```python
@collector.command(
    "/admin",
    description="Административная команда",
    middlewares=[admin_auth_middleware],
)
async def admin_handler(message: IncomingMessage, bot: Bot) -> None:
    # ...
```

Если middleware применяются на обоих уровнях, сначала выполняются middleware коллектора, а затем middleware обработчика.

## Локальное состояние в message.state

Объект `message.state` предоставляет хранилище для передачи данных между middleware и обработчиками. Это позволяет middleware добавлять данные, которые затем могут быть использованы обработчиками.

```python
from pybotx import IncomingMessage, Bot, IncomingMessageHandlerFunc
from uuid import uuid4

async def request_id_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # Генерируем уникальный идентификатор запроса
    message.state.request_id = str(uuid4())
    
    # Добавляем информацию о пользователе
    message.state.is_admin = message.sender.huid in ADMIN_HUIDS
    
    await call_next(message, bot)

@collector.command("/status", description="Показать статус", middlewares=[request_id_middleware])
async def status_handler(message: IncomingMessage, bot: Bot) -> None:
    # Используем данные, добавленные middleware
    request_id = message.state.request_id
    is_admin = message.state.is_admin
    
    if is_admin:
        await bot.answer_message(f"Статус: OK (request_id: {request_id})")
    else:
        await bot.answer_message("У вас нет прав для просмотра статуса")
```

> **Note**
> 
> `message.state` — это объект типа `SimpleNamespace`, который позволяет добавлять и получать атрибуты динамически. Однако, для лучшей типизации рекомендуется определить ожидаемые атрибуты заранее.

## Dependency Injection (DI)

Middleware можно использовать для внедрения зависимостей в обработчики. Это позволяет:
- Создавать и управлять ресурсами (например, соединениями с базой данных)
- Изолировать бизнес-логику от инфраструктурного кода
- Упростить тестирование

```python
from pybotx import IncomingMessage, Bot, IncomingMessageHandlerFunc
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Создаем фабрику сессий
engine = create_async_engine("postgresql+asyncpg://user:password@localhost/db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def db_session_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # Создаем сессию базы данных
    async with AsyncSessionLocal() as session:
        # Добавляем сессию в состояние сообщения
        message.state.db_session = session
        
        # Вызываем следующий middleware или обработчик
        await call_next(message, bot)

@collector.command(
    "/users",
    description="Показать список пользователей",
    middlewares=[db_session_middleware],
)
async def users_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем сессию из состояния сообщения
    session = message.state.db_session
    
    # Используем сессию для запроса к базе данных
    result = await session.execute("SELECT username FROM users LIMIT 10")
    users = [row[0] for row in result]
    
    await bot.answer_message(f"Пользователи: {', '.join(users)}")
```

## Примеры использования

### Логирование и метрики

```python
import time
from pybotx import IncomingMessage, Bot, IncomingMessageHandlerFunc

async def metrics_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # Запоминаем время начала обработки
    start_time = time.time()
    
    # Вызываем следующий middleware или обработчик
    await call_next(message, bot)
    
    # Вычисляем время обработки
    processing_time = time.time() - start_time
    
    # Логируем метрики
    print(f"Сообщение обработано за {processing_time:.3f} секунд")
    
    # Здесь можно отправить метрики в систему мониторинга
    # например, Prometheus, Graphite, etc.
```

### Аутентификация и авторизация

```python
from uuid import UUID
from pybotx import IncomingMessage, Bot, IncomingMessageHandlerFunc

# Список HUID администраторов
ADMIN_HUIDS = (
    UUID("123e4567-e89b-12d3-a456-426614174000"),
    UUID("123e4567-e89b-12d3-a456-426614174001"),
)

async def admin_auth_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # Проверяем, является ли отправитель администратором
    if message.sender.huid not in ADMIN_HUIDS:
        # Если нет, отправляем сообщение об ошибке и прерываем цепочку
        await bot.answer_message("У вас нет прав для выполнения этой команды")
        return
    
    # Если да, продолжаем цепочку
    message.state.is_admin = True
    await call_next(message, bot)

@collector.command(
    "/admin",
    description="Административная команда",
    middlewares=[admin_auth_middleware],
)
async def admin_handler(message: IncomingMessage, bot: Bot) -> None:
    # Этот код выполнится только если пользователь — администратор
    await bot.answer_message("Вы выполнили административную команду")
```

### Обработка ошибок

```python
from pybotx import IncomingMessage, Bot, IncomingMessageHandlerFunc

async def error_handling_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    try:
        # Пытаемся выполнить следующий middleware или обработчик
        await call_next(message, bot)
    except Exception as e:
        # Логируем ошибку
        print(f"Ошибка при обработке сообщения: {e}")
        
        # Отправляем сообщение об ошибке пользователю
        await bot.answer_message(
            "Произошла ошибка при обработке вашего сообщения. "
            "Пожалуйста, попробуйте позже."
        )
        
        # Можно также отправить уведомление администраторам
        # или записать ошибку в систему мониторинга
```

### Внедрение HTTP-клиента

```python
from pybotx import IncomingMessage, Bot, IncomingMessageHandlerFunc
import httpx

async def http_client_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # Создаем HTTP-клиент
    async with httpx.AsyncClient() as client:
        # Добавляем клиент в состояние сообщения
        message.state.http_client = client
        
        # Вызываем следующий middleware или обработчик
        await call_next(message, bot)

@collector.command(
    "/weather",
    description="Показать погоду",
    middlewares=[http_client_middleware],
)
async def weather_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем HTTP-клиент из состояния сообщения
    client = message.state.http_client
    
    # Используем клиент для запроса к API погоды
    city = message.argument or "Moscow"
    response = await client.get(
        f"https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": "your_api_key",
            "units": "metric",
        },
    )
    
    if response.status_code == 200:
        weather_data = response.json()
        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        
        await bot.answer_message(
            f"Погода в {city}: {description}, {temp}°C"
        )
    else:
        await bot.answer_message(f"Не удалось получить погоду для {city}")
```

## См. также

- [Обработчики команд](commands.md)
- [Обработчик сообщений по умолчанию](default.md)
- [Обработчики событий](events.md)
- [Коллекторы](collectors.md)
- [Жизненный цикл бота](../architecture/lifecycle.md)