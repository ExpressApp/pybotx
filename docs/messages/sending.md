# Отправка сообщений

В этом разделе описаны способы отправки сообщений в pybotx.


## Введение

pybotx предоставляет несколько способов отправки сообщений:

1. `bot.answer_message()` — ответ на входящее сообщение
2. `bot.send_message()` — отправка сообщения в произвольный чат
3. `bot.send()` — отправка предварительно созданного объекта `OutgoingMessage`

Каждый из этих методов позволяет отправлять текстовые сообщения, а также добавлять к ним кнопки, файлы, метаданные и другие элементы.

## Ответ на сообщение

Метод `bot.answer_message()` используется для ответа на входящее сообщение. Он автоматически использует контекст входящего сообщения (ID бота, ID чата), поэтому вам нужно указать только текст сообщения и дополнительные параметры.

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/hello", description="Поприветствовать пользователя")
async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(f"Привет, {message.sender.username}!")
```

Метод `bot.answer_message()` имеет следующую сигнатуру:

```python
async def answer_message(
    self,
    body: str,
    *,
    metadata: Missing[Dict[str, Any]] = Undefined,
    bubbles: Missing[BubbleMarkup] = Undefined,
    keyboard: Missing[KeyboardMarkup] = Undefined,
    file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
    recipients: Missing[List[UUID]] = Undefined,
    silent_response: Missing[bool] = Undefined,
    markup_auto_adjust: Missing[bool] = Undefined,
    stealth_mode: Missing[bool] = Undefined,
    send_push: Missing[bool] = Undefined,
    ignore_mute: Missing[bool] = Undefined,
    wait_callback: bool = True,
    callback_timeout: Optional[float] = None,
) -> UUID:
    # ...
```

Метод возвращает `UUID` — уникальный идентификатор отправленного сообщения (`sync_id`), который можно использовать для последующего редактирования или удаления сообщения.

## Отправка сообщения в произвольный чат

Метод `bot.send_message()` используется для отправки сообщения в произвольный чат. В отличие от `bot.answer_message()`, вам нужно явно указать ID бота и ID чата.

```python
from uuid import UUID
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/broadcast", description="Отправить сообщение в другой чат")
async def broadcast_handler(message: IncomingMessage, bot: Bot) -> None:
    # ID чата, в который нужно отправить сообщение
    target_chat_id = UUID("123e4567-e89b-12d3-a456-426655440000")

    await bot.send_message(
        bot_id=message.bot.id,
        chat_id=target_chat_id,
        body="Важное объявление!",
    )

    await bot.answer_message("Сообщение отправлено")
```

Метод `bot.send_message()` имеет следующую сигнатуру:

```python
async def send_message(
    self,
    *,
    bot_id: UUID,
    chat_id: UUID,
    body: str,
    metadata: Missing[Dict[str, Any]] = Undefined,
    bubbles: Missing[BubbleMarkup] = Undefined,
    keyboard: Missing[KeyboardMarkup] = Undefined,
    file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
    silent_response: Missing[bool] = Undefined,
    markup_auto_adjust: Missing[bool] = Undefined,
    recipients: Missing[List[UUID]] = Undefined,
    stealth_mode: Missing[bool] = Undefined,
    send_push: Missing[bool] = Undefined,
    ignore_mute: Missing[bool] = Undefined,
    wait_callback: bool = True,
    callback_timeout: Optional[float] = None,
) -> UUID:
    # ...
```

## Использование OutgoingMessage

Класс `OutgoingMessage` позволяет создать сообщение заранее, а затем отправить его с помощью метода `bot.send()`. Это полезно, когда логика формирования сообщения отделена от логики его отправки.

```python
from uuid import UUID
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingMessage, BubbleMarkup

collector = HandlerCollector()

def create_welcome_message(bot_id: UUID, chat_id: UUID, username: str) -> OutgoingMessage:
    """Создает приветственное сообщение с кнопками."""
    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/help",
        label="Справка",
        background_color="#007bff",
    )

    return OutgoingMessage(
        bot_id=bot_id,
        chat_id=chat_id,
        body=f"Добро пожаловать, {username}!",
        bubbles=bubbles,
    )

@collector.command("/welcome", description="Отправить приветственное сообщение")
async def welcome_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем сообщение
    welcome_message = create_welcome_message(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        username=message.sender.username,
    )

    # Отправляем сообщение
    await bot.send(message=welcome_message)
```

Конструктор `OutgoingMessage` принимает те же параметры, что и метод `bot.send_message()`:

```python
class OutgoingMessage:
    def __init__(
        self,
        bot_id: UUID,
        chat_id: UUID,
        body: str,
        metadata: Optional[Dict[str, Any]] = None,
        bubbles: Optional[BubbleMarkup] = None,
        keyboard: Optional[KeyboardMarkup] = None,
        file: Optional[Union[IncomingFileAttachment, OutgoingAttachment]] = None,
        silent_response: Optional[bool] = None,
        markup_auto_adjust: Optional[bool] = None,
        recipients: Optional[List[UUID]] = None,
        stealth_mode: Optional[bool] = None,
        send_push: Optional[bool] = None,
        ignore_mute: Optional[bool] = None,
    ):
        # ...
```

## Параметры сообщений

Все методы отправки сообщений принимают следующие параметры:

| Параметр | Тип | Описание |
|----------|-----|----------|
| `body` | `str` | Текст сообщения |
| `metadata` | `Dict[str, Any]` | Метаданные сообщения (произвольный JSON) |
| `bubbles` | `BubbleMarkup` | Кнопки, отображаемые под сообщением |
| `keyboard` | `KeyboardMarkup` | Кнопки, отображаемые в поле ввода |
| `file` | `Union[IncomingFileAttachment, OutgoingAttachment]` | Файл, прикрепленный к сообщению |
| `recipients` | `List[UUID]` | Список получателей сообщения (для групповых чатов) |
| `silent_response` | `bool` | Отправить сообщение без уведомления |
| `markup_auto_adjust` | `bool` | Автоматически настроить расположение кнопок |
| `stealth_mode` | `bool` | Отправить сообщение в режиме "невидимки" |
| `send_push` | `bool` | Отправить push-уведомление |
| `ignore_mute` | `bool` | Игнорировать настройки "не беспокоить" |
| `wait_callback` | `bool` | Ждать подтверждения отправки от сервера |
| `callback_timeout` | `float` | Таймаут ожидания подтверждения |

> **Note**
> 
> Параметры с типом `Missing[T]` могут быть опущены (не переданы в функцию). Это отличается от передачи `None`, который явно указывает на отсутствие значения.

## Примеры использования

### Отправка простого текстового сообщения

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/echo", description="Отправить обратно полученный текст")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите текст для эхо")
        return

    await bot.answer_message(message.argument)
```

### Отправка сообщения с кнопками

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, BubbleMarkup

collector = HandlerCollector()

@collector.command("/menu", description="Показать меню")
async def menu_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем разметку с кнопками
    bubbles = BubbleMarkup()

    # Добавляем кнопки в первый ряд
    bubbles.add_button(
        command="/help",
        label="Справка",
        background_color="#007bff",
    )
    bubbles.add_button(
        command="/profile",
        label="Профиль",
        background_color="#28a745",
        new_row=False,  # Кнопка будет в том же ряду
    )

    # Добавляем кнопки во второй ряд
    bubbles.add_button(
        command="/settings",
        label="Настройки",
        background_color="#6c757d",
    )

    # Добавляем кнопку-ссылку
    bubbles.add_button(
        label="Документация",
        link="https://example.com/docs",
        background_color="#17a2b8",
    )

    await bot.answer_message(
        "Выберите действие:",
        bubbles=bubbles,
    )
```

### Отправка сообщения с файлом

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/file", description="Отправить файл")
async def file_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем файл из строки
    file_content = "Это содержимое текстового файла."
    file = await OutgoingAttachment.from_bytes(
        file_content.encode("utf-8"),
        filename="example.txt",
    )

    await bot.answer_message(
        "Вот ваш файл:",
        file=file,
    )
```

### Отправка сообщения с метаданными

```python
from pybotx import HandlerCollector, IncomingMessage, Bot
import json

collector = HandlerCollector()

@collector.command("/metadata", description="Отправить сообщение с метаданными")
async def metadata_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем метаданные
    metadata = {
        "type": "example",
        "timestamp": "2023-06-15T12:00:00Z",
        "user_id": str(message.sender.huid),
        "custom_data": {
            "key1": "value1",
            "key2": 42,
        },
    }

    await bot.answer_message(
        f"Сообщение с метаданными:\n```json\n{json.dumps(metadata, indent=2)}\n```",
        metadata=metadata,
    )
```

### Отправка сообщения определенным получателям в групповом чате

```python
from uuid import UUID
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/private", description="Отправить приватное сообщение")
async def private_handler(message: IncomingMessage, bot: Bot) -> None:
    if not message.mentions.contacts:
        await bot.answer_message("Пожалуйста, укажите получателей через @")
        return

    # Получаем список HUID упомянутых пользователей
    recipients = [contact.entity_id for contact in message.mentions.contacts]

    await bot.answer_message(
        "Это приватное сообщение, видимое только упомянутым пользователям",
        recipients=recipients,
    )
```

### Отправка сообщения без уведомления

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/silent", description="Отправить тихое сообщение")
async def silent_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(
        "Это сообщение отправлено без уведомления",
        silent_response=True,
    )
```

## См. также

- [Редактирование сообщений](/messages/editing/)
- [Удаление сообщений](/messages/deleting/)
- [Кнопки и разметка](/messages/bubbles/)
- [Упоминания](/messages/mentions/)
- [Вложения](/messages/attachments/)
