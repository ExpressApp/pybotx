# pybotx

*Библиотека для создания чат-ботов и SmartApps для мессенджера eXpress*

## Что такое pybotx

pybotx — это Python-библиотека для создания чат-ботов и SmartApps для корпоративного мессенджера eXpress. Библиотека
предоставляет удобный интерфейс для взаимодействия с BotX API, позволяя разработчикам сосредоточиться на бизнес-логике,
а не на деталях реализации протокола.

## Hello World бот

Вот простой пример "Hello World" бота, который отвечает на команду `/hello`:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pybotx import Bot, BotAccountWithSecret, HandlerCollector, IncomingMessage, build_command_accepted_response
from uuid import UUID

# Создаем коллектор обработчиков
collector = HandlerCollector()


# Регистрируем обработчик команды /hello
@collector.command("/hello", description="Поприветствовать пользователя")
async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(f"Привет, {message.sender.username}!")


# Создаем экземпляр бота
bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),  # ID бота
            cts_url="https://cts.example.com",  # URL CTS сервера
            secret_key="e29b417773f2feab9dac143ee3da20c5",  # Секретный ключ
        ),
    ],
)

# Создаем FastAPI приложение
app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


# Обработчик команд
@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=202,
    )
```

## Преимущества библиотеки

- **Простота использования**: Интуитивно понятный API, который позволяет быстро начать разработку
- **Асинхронность**: Полная поддержка асинхронного программирования с использованием `async/await`
- **Типизация**: Полное покрытие аннотациями типов для лучшей поддержки IDE и инструментов статического анализа
- **Интеграция с веб-фреймворками**: Легко интегрируется с FastAPI, Starlette, AioHTTP и другими асинхронными
  веб-фреймворками
- **Поддержка коллбэков**: Встроенная поддержка коллбэков BotX для асинхронных операций
- **Расширяемость**: Возможность создания собственных плагинов и расширений
- **Тестируемость**: Полное покрытие тестами и инструменты для тестирования ваших ботов

## Начало работы

Для начала работы с pybotx, установите библиотеку с помощью Poetry:

```bash
poetry add pybotx
```

Затем ознакомьтесь с [руководством по быстрому старту](/quick_start/), чтобы создать свой первый бот.

## Документация

- [Быстрый старт](/quick_start/)
- [Миграция между версиями](/migration/)
- [Архитектура](/architecture/overview/)
- [Обработчики](/handlers/commands/)
- [Сообщения](/messages/sending/)
- [Чаты](/chats/create/)
- [Пользователи](/users/search/)
- [SmartApps](/smartapps/overview/)
- [Интеграция](/integration/fastapi/)
- [Развертывание](/deployment/docker/)
- [Тестирование](/testing/unit/)
- [Отладка](/debug/logging/)
- [Расширения](/extensions/fsm/)
