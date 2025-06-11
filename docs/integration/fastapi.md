# Интеграция с FastAPI

В этом разделе описана интеграция pybotx с веб-фреймворком FastAPI, включая настройку CORS и логирование.

## Введение

FastAPI — это современный, высокопроизводительный веб-фреймворк для создания API с Python 3.6+, основанный на
стандартных аннотациях типов Python. Он отлично подходит для создания серверной части ботов на pybotx благодаря своей
асинхронной природе и простоте использования.

Интеграция pybotx с FastAPI позволяет:

- Обрабатывать входящие команды и события от BotX API
- Отправлять ответы и уведомления пользователям
- Обрабатывать коллбэки от BotX API
- Предоставлять дополнительные API-эндпоинты для вашего бота

## Базовая интеграция

Для базовой интеграции pybotx с FastAPI необходимо:

1. Создать экземпляр `Bot` с необходимыми обработчиками
2. Создать экземпляр `FastAPI`
3. Добавить обработчики событий для запуска и остановки бота
4. Создать эндпоинты для обработки команд, статуса и коллбэков

```python
from http import HTTPStatus
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pybotx import (
    Bot, BotAccountWithSecret, HandlerCollector,
    IncomingMessage, build_command_accepted_response,
)

# Создаем коллектор обработчиков
collector = HandlerCollector()


# Регистрируем обработчик команды
@collector.command("/hello", description="Поприветствовать пользователя")
async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(f"Привет, {message.sender.username}!")


# Создаем экземпляр бота
bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            cts_url="https://cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
)

# Создаем экземпляр FastAPI
app = FastAPI()

# Добавляем обработчики событий для запуска и остановки бота
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


# Эндпоинт для обработки команд
@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


# Эндпоинт для получения статуса бота
@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(
        dict(request.query_params),
        request_headers=request.headers,
    )
    return JSONResponse(status)


# Эндпоинт для обработки коллбэков
@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    await bot.set_raw_botx_method_result(
        await request.json(),
        verify_request=False,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )
```

## Настройка CORS

Cross-Origin Resource Sharing (CORS) — это механизм, который позволяет веб-страницам запрашивать ресурсы с других
доменов. Это важно, если ваш бот взаимодействует с веб-приложениями или SmartApp.

FastAPI предоставляет простой способ настройки CORS с помощью middleware:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://express.ms", "https://smartapp.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Bot-Key"],
)
```

### Параметры CORS

- `allow_origins` — список разрешенных источников (доменов)
- `allow_credentials` — разрешить передачу учетных данных (cookies, HTTP-аутентификация)
- `allow_methods` — разрешенные HTTP-методы
- `allow_headers` — разрешенные HTTP-заголовки

> **Note**
>
> Для продакшн-окружения рекомендуется указывать конкретные домены в `allow_origins`, а не использовать `["*"]`, чтобы
> повысить безопасность.

## Полный пример

Ниже приведен полный пример интеграции pybotx с FastAPI, включая настройку CORS, логирование и обработку ошибок:

```python
import sys
import time
import uuid
from http import HTTPStatus
from typing import Callable, Dict, Any
from uuid import UUID

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from pybotx import (
    Bot, BotAccountWithSecret, HandlerCollector,
    IncomingMessage, SmartAppEvent, BotAPISyncSmartAppEventResultResponse,
    build_command_accepted_response,
)

# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="INFO",
)
logger.add(
    "logs/bot.log",
    rotation="10 MB",
    retention="1 week",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG",
)

# Создаем коллектор обработчиков
collector = HandlerCollector()


# Регистрируем обработчик команды
@collector.command("/hello", description="Поприветствовать пользователя")
async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
    logger.info(f"Received /hello command from {message.sender.username}")
    await bot.answer_message(f"Привет, {message.sender.username}!")


# Регистрируем обработчик события создания чата
@collector.chat_created
async def chat_created_handler(event, bot: Bot) -> None:
    logger.info(f"Chat created: {event.chat.id}")
    await bot.send_message(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        body="Спасибо за создание чата! Я готов помочь вам.",
    )


# Регистрируем обработчик синхронных SmartApp-событий
@collector.sync_smartapp_event
async def sync_smartapp_event_handler(
        event: SmartAppEvent, bot: Bot
) -> BotAPISyncSmartAppEventResultResponse:
    logger.info(f"Received sync SmartApp event: {event.type}")

    if event.type == "get_user_info":
        # Пример обработки события получения информации о пользователе
        return BotAPISyncSmartAppEventResultResponse.from_domain(
            data={
                "username": event.sender.username,
                "huid": str(event.sender.huid),
            },
            files=[],
        )

    # Обработка неизвестного типа события
    return BotAPISyncSmartAppEventResultResponse.from_domain(
        data={"error": f"Unknown event type: {event.type}"},
        files=[],
    )


# Обработчик ошибок
async def error_handler(message: IncomingMessage, bot: Bot, exc: Exception) -> None:
    logger.exception(f"Error processing message: {exc}")
    await bot.answer_message(
        "Произошла ошибка при обработке вашего сообщения. "
        "Пожалуйста, попробуйте позже или обратитесь к администратору."
    )


# Создаем экземпляр бота
bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            cts_url="https://cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
    exception_handlers={Exception: error_handler},
)

# Создаем экземпляр FastAPI
app = FastAPI(
    title="BotX API",
    description="API для бота на платформе BotX",
    version="1.0.0",
)

# Добавляем обработчики событий для запуска и остановки бота
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://express.ms"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Bot-Key"],
)


# Эндпоинт для обработки команд
@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    try:
        request_body = await request.json()
        logger.debug(f"Received command: {request_body}")

        bot.async_execute_raw_bot_command(
            request_body,
            request_headers=request.headers,
        )

        return JSONResponse(
            build_command_accepted_response(),
            status_code=HTTPStatus.ACCEPTED,
        )
    except Exception as e:
        logger.exception(f"Error processing command: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# Эндпоинт для обработки синхронных SmartApp-событий
@app.post("/smartapps/request")
async def sync_smartapp_event_handler(request: Request) -> JSONResponse:
    try:
        request_body = await request.json()
        logger.debug(f"Received SmartApp event: {request_body}")

        response = await bot.sync_execute_raw_smartapp_event(
            request_body,
            request_headers=request.headers,
        )

        return JSONResponse(
            response.jsonable_dict(),
            status_code=HTTPStatus.OK,
        )
    except Exception as e:
        logger.exception(f"Error processing SmartApp event: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# Эндпоинт для получения статуса бота
@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    try:
        status = await bot.raw_get_status(
            dict(request.query_params),
            request_headers=request.headers,
        )
        return JSONResponse(status)
    except Exception as e:
        logger.exception(f"Error getting status: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# Эндпоинт для обработки коллбэков
@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    try:
        request_body = await request.json()
        logger.debug(f"Received callback: {request_body}")

        await bot.set_raw_botx_method_result(
            request_body,
            verify_request=False,
        )

        return JSONResponse(
            build_command_accepted_response(),
            status_code=HTTPStatus.ACCEPTED,
        )
    except Exception as e:
        logger.exception(f"Error processing callback: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# Дополнительный эндпоинт для проверки работоспособности
@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok"})


# Запуск приложения (для локальной разработки)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
```

## Лучшие практики

### 1. Конфигурация через переменные окружения

Используйте переменные окружения для конфигурации:

```python
# config.py
import os
from uuid import UUID
from pydantic import BaseSettings


class Settings(BaseSettings):
    BOT_ID: UUID
    CTS_URL: str
    SECRET_KEY: str
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["https://express.ms"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

### 2. Асинхронная обработка длительных операций

Для длительных операций используйте асинхронные задачи:

```python
import asyncio
from fastapi import BackgroundTasks


@collector.command("/report", description="Сгенерировать отчет")
async def report_handler(message: IncomingMessage, bot: Bot) -> None:
    # Отправляем начальное сообщение
    await bot.answer_message("Начинаю генерацию отчета. Это может занять некоторое время...")

    # Запускаем асинхронную задачу
    asyncio.create_task(
        generate_report(bot, message.bot.id, message.chat.id, message.sender.huid)
    )


async def generate_report(bot: Bot, bot_id: UUID, chat_id: UUID, user_huid: UUID) -> None:
    try:
        # Имитация длительной операции
        await asyncio.sleep(10)

        # Генерация отчета
        report_data = "Это данные отчета..."

        # Отправка результата
        await bot.send_message(
            bot_id=bot_id,
            chat_id=chat_id,
            body=f"Отчет готов:\n\n{report_data}",
        )
    except Exception as e:
        logger.exception(f"Error generating report: {e}")

        # Отправка сообщения об ошибке
        await bot.send_message(
            bot_id=bot_id,
            chat_id=chat_id,
            body="Произошла ошибка при генерации отчета. Пожалуйста, попробуйте позже.",
        )
```

### 3. Обработка ошибок

Создайте специальные обработчики для разных типов ошибок:

```python
from pybotx.models.commands import BotCommand
from pybotx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackTimeoutError


# Обработчик для ошибок команд
async def command_error_handler(
        message: IncomingMessage, bot: Bot, exc: Exception
) -> None:
    logger.exception(f"Error processing command: {exc}")
    await bot.answer_message(
        "Произошла ошибка при обработке команды. "
        "Пожалуйста, попробуйте позже или обратитесь к администратору."
    )


# Обработчик для ошибок таймаута
async def timeout_error_handler(
        message: IncomingMessage, bot: Bot, exc: BotXMethodCallbackTimeoutError
) -> None:
    logger.error(f"Timeout error: {exc}")
    await bot.answer_message(
        "Превышено время ожидания ответа от сервера. "
        "Пожалуйста, попробуйте позже."
    )


# Обработчик для ошибок при завершении работы бота
async def shutdown_error_handler(
        message: IncomingMessage, bot: Bot, exc: BotShuttingDownError
) -> None:
    logger.warning(f"Bot shutting down: {exc}")
    await bot.answer_message(
        "Бот в данный момент завершает работу. "
        "Пожалуйста, повторите запрос через несколько минут."
    )


# Регистрация обработчиков ошибок
bot = Bot(
    collectors=[collector],
    bot_accounts=[...],
    exception_handlers={
        Exception: command_error_handler,
        BotXMethodCallbackTimeoutError: timeout_error_handler,
        BotShuttingDownError: shutdown_error_handler,
    },
)
```

### 4. Документация API

FastAPI автоматически генерирует документацию API с помощью Swagger UI и ReDoc:

```python
app = FastAPI(
    title="BotX API",
    description="API для бота на платформе BotX",
    version="1.0.0",
    docs_url="/docs",  # URL для Swagger UI
    redoc_url="/redoc",  # URL для ReDoc
)
```

## См. также

- [Обзор архитектуры](../architecture/overview.md)
- [Жизненный цикл бота](../architecture/lifecycle.md)
- [Обработка команд](../handlers/commands.md)
- [Обработка событий](../handlers/events.md)