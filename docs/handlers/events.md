# Обработчики событий

В этом разделе описаны обработчики системных событий в pybotx, их настройка и использование.

## Введение

Обработчики событий — это функции, которые вызываются при получении ботом системных событий от платформы BotX. Они позволяют боту реагировать на различные события, такие как создание чата, события от SmartApp и другие.

В pybotx обработчики событий регистрируются с помощью специальных декораторов:
- `@collector.chat_created` — для обработки события создания чата
- `@collector.smartapp_event` — для обработки асинхронных событий от SmartApp
- `@collector.sync_smartapp_event` — для обработки синхронных событий от SmartApp

## Типы событий

pybotx поддерживает следующие типы системных событий:

| Тип события | Декоратор | Описание |
|-------------|-----------|----------|
| Создание чата | `@collector.chat_created` | Вызывается при создании нового чата с участием бота |
| SmartApp событие | `@collector.smartapp_event` | Вызывается при получении асинхронного события от SmartApp |
| Синхронное SmartApp событие | `@collector.sync_smartapp_event` | Вызывается при получении синхронного события от SmartApp |

## Обработчик события создания чата

Для обработки события создания чата используется декоратор `@collector.chat_created`:

```python
from pybotx import HandlerCollector, ChatCreatedEvent, Bot

collector = HandlerCollector()

@collector.chat_created
async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    # Отправляем приветственное сообщение в новый чат
    await bot.send_message(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        body=f"Привет! Я бот. Чат '{event.chat.name}' успешно создан.",
    )
```

Обработчик события создания чата должен быть асинхронной функцией, принимающей два параметра:
- `event: ChatCreatedEvent` — информация о событии создания чата
- `bot: Bot` — экземпляр бота

Объект `ChatCreatedEvent` содержит следующие поля:
- `bot` — информация о боте
- `chat` — информация о созданном чате
- `source_sync_id` — идентификатор события

## Обработчик SmartApp событий

Для обработки асинхронных событий от SmartApp используется декоратор `@collector.smartapp_event`:

```python
from pybotx import HandlerCollector, SmartAppEvent, Bot

collector = HandlerCollector()

@collector.smartapp_event
async def smartapp_event_handler(event: SmartAppEvent, bot: Bot) -> None:
    # Обрабатываем событие от SmartApp
    print(f"Получено событие от SmartApp: {event.data}")
    
    # Отправляем ответ пользователю
    await bot.send_message(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        body=f"Получено событие от SmartApp: {event.data}",
    )
```

Обработчик SmartApp событий должен быть асинхронной функцией, принимающей два параметра:
- `event: SmartAppEvent` — информация о событии от SmartApp
- `bot: Bot` — экземпляр бота

Объект `SmartAppEvent` содержит следующие поля:
- `bot` — информация о боте
- `chat` — информация о чате
- `sender` — информация об отправителе события
- `data` — данные события (словарь с произвольными данными)
- `ref` — ссылка на событие (опционально)
- `files` — прикрепленные файлы (опционально)

## Обработчик синхронных SmartApp событий

Для обработки синхронных событий от SmartApp используется декоратор `@collector.sync_smartapp_event`:

```python
from pybotx import (
    HandlerCollector,
    SmartAppEvent,
    Bot,
    BotAPISyncSmartAppEventResultResponse,
)

collector = HandlerCollector()

@collector.sync_smartapp_event
async def sync_smartapp_event_handler(
    event: SmartAppEvent,
    bot: Bot,
) -> BotAPISyncSmartAppEventResultResponse:
    # Обрабатываем синхронное событие от SmartApp
    print(f"Получено синхронное событие от SmartApp: {event.data}")
    
    # Возвращаем результат обработки
    return BotAPISyncSmartAppEventResultResponse.from_domain(
        data={"result": "success", "message": "Событие обработано"},
        files=[],  # Можно прикрепить файлы к ответу
    )
```

Обработчик синхронных SmartApp событий должен быть асинхронной функцией, принимающей два параметра:
- `event: SmartAppEvent` — информация о событии от SmartApp
- `bot: Bot` — экземпляр бота

Функция должна возвращать объект `BotAPISyncSmartAppEventResultResponse`, который содержит результат обработки события.

> **Note**
> 
> Основное отличие между асинхронными и синхронными SmartApp событиями заключается в том, что для синхронных событий клиент ожидает немедленного ответа, а для асинхронных — нет. Синхронные события обрабатываются через эндпоинт `/smartapps/request`, а асинхронные — через эндпоинт `/command`.

## Примеры использования

### Обработка события создания чата с приветственным сообщением

```python
from pybotx import HandlerCollector, ChatCreatedEvent, Bot, BubbleMarkup

collector = HandlerCollector()

@collector.chat_created
async def welcome_message_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    # Создаем кнопки для приветственного сообщения
    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/help",
        label="Справка",
        background_color="#007bff",
    )
    bubbles.add_button(
        command="/about",
        label="О боте",
        background_color="#28a745",
    )
    
    # Отправляем приветственное сообщение с кнопками
    await bot.send_message(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        body=(
            f"Добро пожаловать в чат '{event.chat.name}'!\n\n"
            "Я бот-помощник. Чтобы узнать, что я умею, нажмите кнопку 'Справка' "
            "или отправьте команду /help."
        ),
        bubbles=bubbles,
    )
```

### Обработка SmartApp события с данными формы

```python
from pybotx import HandlerCollector, SmartAppEvent, Bot
from typing import Dict, Any

collector = HandlerCollector()

@collector.smartapp_event
async def form_submission_handler(event: SmartAppEvent, bot: Bot) -> None:
    # Проверяем, что событие содержит данные формы
    if event.data.get("type") != "form_submission":
        return
    
    # Получаем данные формы
    form_data: Dict[str, Any] = event.data.get("form_data", {})
    
    # Обрабатываем данные формы
    name = form_data.get("name", "")
    email = form_data.get("email", "")
    message = form_data.get("message", "")
    
    # Отправляем подтверждение пользователю
    await bot.send_message(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        body=(
            f"Спасибо за заполнение формы, {name}!\n\n"
            f"Ваш email: {email}\n"
            f"Ваше сообщение: {message}\n\n"
            "Мы обработаем вашу заявку в ближайшее время."
        ),
    )
```

### Обработка синхронного SmartApp события для API

```python
from pybotx import (
    HandlerCollector,
    SmartAppEvent,
    Bot,
    BotAPISyncSmartAppEventResultResponse,
)
from typing import Dict, Any, List
import json

collector = HandlerCollector()

# Имитация базы данных пользователей
USERS_DB: List[Dict[str, Any]] = [
    {"id": 1, "name": "Иван", "email": "ivan@example.com"},
    {"id": 2, "name": "Мария", "email": "maria@example.com"},
    {"id": 3, "name": "Алексей", "email": "alex@example.com"},
]

@collector.sync_smartapp_event
async def api_handler(
    event: SmartAppEvent,
    bot: Bot,
) -> BotAPISyncSmartAppEventResultResponse:
    # Получаем тип API-запроса
    api_method = event.data.get("method", "")
    
    if api_method == "get_users":
        # Возвращаем список пользователей
        return BotAPISyncSmartAppEventResultResponse.from_domain(
            data={"users": USERS_DB},
            files=[],
        )
    
    elif api_method == "get_user":
        # Получаем ID пользователя из параметров
        user_id = event.data.get("user_id")
        
        if user_id is None:
            return BotAPISyncSmartAppEventResultResponse.from_domain(
                data={"error": "Missing user_id parameter"},
                files=[],
            )
        
        # Ищем пользователя по ID
        user = next((u for u in USERS_DB if u["id"] == user_id), None)
        
        if user is None:
            return BotAPISyncSmartAppEventResultResponse.from_domain(
                data={"error": f"User with ID {user_id} not found"},
                files=[],
            )
        
        return BotAPISyncSmartAppEventResultResponse.from_domain(
            data={"user": user},
            files=[],
        )
    
    else:
        # Неизвестный метод API
        return BotAPISyncSmartAppEventResultResponse.from_domain(
            data={"error": f"Unknown API method: {api_method}"},
            files=[],
        )
```

## См. также

- [Обработчики команд](commands.md)
- [Обработчик сообщений по умолчанию](default.md)
- [Middleware](middlewares.md)
- [Коллекторы](collectors.md)
- [SmartApps](../smartapps/overview.md)