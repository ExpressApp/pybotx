# Обработчики команд

В этом разделе описаны обработчики команд в pybotx, их настройка и использование.


## Введение

Обработчики команд — это функции, которые вызываются при получении ботом сообщения, начинающегося с определенной команды (например, `/help`). Они являются основным способом взаимодействия пользователя с ботом.

В pybotx обработчики команд регистрируются с помощью декоратора `@collector.command`.

## Регистрация обработчика команды

Для регистрации обработчика команды используется декоратор `@collector.command`:

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/hello", description="Поприветствовать пользователя")
async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(f"Привет, {message.sender.username}!")
```

Каждый обработчик команды должен быть асинхронной функцией, принимающей два параметра:
- `message: IncomingMessage` — входящее сообщение
- `bot: Bot` — экземпляр бота

## Параметры декоратора @collector.command

Декоратор `@collector.command` принимает следующие параметры:

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `command_name` | `str` | Да | Имя команды, начинающееся с символа `/` |
| `visible` | `Union[bool, VisibleFunc]` | Нет | Флаг видимости команды или функция, определяющая видимость |
| `description` | `Optional[str]` | Нет (но обязателен для видимых команд) | Описание команды, отображаемое в списке команд |
| `middlewares` | `Optional[Sequence[Middleware]]` | Нет | Список middleware, применяемых к обработчику |

```python
@collector.command(
    "/admin",
    visible=is_admin,  # Функция, определяющая видимость
    description="Административная команда",
    middlewares=[logging_middleware],
)
async def admin_handler(message: IncomingMessage, bot: Bot) -> None:
    # Обработка команды
    pass
```

## Видимость команд

Параметр `visible` определяет, будет ли команда отображаться в списке команд бота. Он может принимать следующие значения:

1. `True` (по умолчанию) — команда видима для всех пользователей
2. `False` — команда невидима (не отображается в списке команд)
3. Функция типа `VisibleFunc` — команда видима только для пользователей, для которых функция возвращает `True`

### Невидимые команды

Невидимые команды не отображаются в списке команд, но могут быть вызваны пользователем:

```python
@collector.command("/_debug", visible=False)
async def debug_handler(message: IncomingMessage, bot: Bot) -> None:
    # Для невидимых команд описание не обязательно
    await bot.answer_message("Отладочная информация...")
```

### Условная видимость

Для реализации условной видимости (например, только для администраторов) используется функция типа `VisibleFunc`:

```python
from uuid import UUID
from pybotx import StatusRecipient, Bot

# Список HUID администраторов
ADMIN_HUIDS = (
    UUID("123e4567-e89b-12d3-a456-426614174000"),
    UUID("123e4567-e89b-12d3-a456-426614174001"),
)

# Функция, определяющая видимость команды
async def is_admin(status_recipient: StatusRecipient, bot: Bot) -> bool:
    return status_recipient.huid in ADMIN_HUIDS

@collector.command(
    "/admin",
    visible=is_admin,
    description="Административная команда",
)
async def admin_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Вы выполнили административную команду")
```

Функция видимости должна быть асинхронной и принимать два параметра:
- `status_recipient: StatusRecipient` — информация о пользователе, запрашивающем список команд
- `bot: Bot` — экземпляр бота

## Аргументы команд

Аргументы команды — это текст, следующий за командой в сообщении. Например, в сообщении `/echo Hello, world!` аргументом является `Hello, world!`.

Аргументы доступны через свойство `message.argument`:

```python
@collector.command("/echo", description="Отправить обратно полученный текст")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите текст для эхо")
        return

    await bot.answer_message(message.argument)
```

Для более сложного разбора аргументов можно использовать регулярные выражения или другие методы парсинга:

```python
import re

@collector.command("/calc", description="Калькулятор (например, /calc 2+2)")
async def calc_handler(message: IncomingMessage, bot: Bot) -> None:
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите выражение для вычисления")
        return

    # Проверка безопасности выражения
    if not re.match(r'^[\d\+\-\*\/\(\)\s\.]+$', message.argument):
        await bot.answer_message("Недопустимое выражение")
        return

    try:
        result = eval(message.argument)
        await bot.answer_message(f"Результат: {result}")
    except Exception as e:
        await bot.answer_message(f"Ошибка: {e}")
```

## Примеры использования

### Базовый обработчик команды

```python
@collector.command("/help", description="Показать справку")
async def help_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(
        "Доступные команды:\n"
        "/help - Показать справку\n"
        "/echo <текст> - Отправить обратно полученный текст\n"
        "/time - Показать текущее время"
    )
```

### Команда с обработкой аргументов

```python
from datetime import datetime
import pytz

@collector.command("/time", description="Показать время в указанном часовом поясе")
async def time_handler(message: IncomingMessage, bot: Bot) -> None:
    if not message.argument:
        # Если часовой пояс не указан, показываем время по UTC
        now = datetime.now(pytz.UTC)
        await bot.answer_message(f"Текущее время (UTC): {now.strftime('%H:%M:%S')}")
        return

    try:
        # Пытаемся получить часовой пояс из аргумента
        timezone = pytz.timezone(message.argument)
        now = datetime.now(timezone)
        await bot.answer_message(
            f"Текущее время ({message.argument}): {now.strftime('%H:%M:%S')}"
        )
    except pytz.exceptions.UnknownTimeZoneError:
        await bot.answer_message(
            f"Неизвестный часовой пояс: {message.argument}\n"
            "Примеры: Europe/Moscow, America/New_York, Asia/Tokyo"
        )
```

### Команда только для администраторов

```python
from uuid import UUID

# Список HUID администраторов
ADMIN_HUIDS = (
    UUID("123e4567-e89b-12d3-a456-426614174000"),
    UUID("123e4567-e89b-12d3-a456-426614174001"),
)

async def is_admin(status_recipient: StatusRecipient, bot: Bot) -> bool:
    return status_recipient.huid in ADMIN_HUIDS

@collector.command(
    "/broadcast",
    visible=is_admin,
    description="Отправить сообщение всем пользователям",
)
async def broadcast_handler(message: IncomingMessage, bot: Bot) -> None:
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите текст для рассылки")
        return

    # Проверяем, что отправитель действительно администратор
    if message.sender.huid not in ADMIN_HUIDS:
        await bot.answer_message("У вас нет прав для выполнения этой команды")
        return

    # Здесь должен быть код для рассылки сообщения всем пользователям
    await bot.answer_message(f"Сообщение '{message.argument}' отправлено всем пользователям")
```

> **Note**
> 
> Даже если команда невидима для пользователя, он все равно может попытаться ее выполнить, если знает ее имя. Поэтому всегда проверяйте права доступа в самом обработчике команды.

## См. также

- [Обработчик сообщений по умолчанию](default.md)
- [Обработчики событий](events.md)
- [Middleware](middlewares.md)
- [Коллекторы](collectors.md)
- [Отправка сообщений](../messages/sending.md)
