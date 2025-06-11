# Создание чатов

В этом разделе описаны способы создания чатов с помощью pybotx.


## Введение

pybotx позволяет ботам создавать различные типы чатов и добавлять в них пользователей. Это может быть полезно для организации групповых обсуждений, создания тематических каналов или приватных чатов между пользователями.

Для создания чата используется метод `bot.create_chat()`, который принимает различные параметры, такие как название чата, тип чата и список участников.

## Метод bot.create_chat

Метод `bot.create_chat()` имеет следующую сигнатуру:

```python
async def create_chat(
    self,
    bot_id: UUID,
    name: str,
    chat_type: ChatTypes,
    huids: List[UUID],
    *,
    description: Missing[str] = Undefined,
    avatar: Missing[str] = Undefined,
    wait_callback: bool = True,
    callback_timeout: Optional[float] = None,
) -> UUID:
    # ...
```

### Параметры

- `bot_id` (UUID) — идентификатор бота, от имени которого создается чат
- `name` (str) — название чата
- `chat_type` (ChatTypes) — тип создаваемого чата (групповой, канал и т.д.)
- `huids` (List[UUID]) — список HUID пользователей, которые будут добавлены в чат
- `description` (str, опционально) — описание чата
- `avatar` (str, опционально) — аватар чата в формате base64
- `wait_callback` (bool, по умолчанию True) — ожидать ли коллбэк от BotX API
- `callback_timeout` (float, опционально) — таймаут ожидания коллбэка

### Возвращаемое значение

Метод возвращает UUID созданного чата, который можно использовать для дальнейших операций с этим чатом.

## Типы чатов

В pybotx доступны следующие типы чатов, определенные в перечислении `ChatTypes`:

- `ChatTypes.GROUP_CHAT` — групповой чат, в котором могут общаться несколько пользователей
- `ChatTypes.CHANNEL` — канал, в котором сообщения могут отправлять только администраторы
- `ChatTypes.PERSONAL_CHAT` — личный чат между двумя пользователями

```python
from pybotx import ChatTypes

# Пример использования типов чатов
chat_type = ChatTypes.GROUP_CHAT  # Групповой чат
# или
chat_type = ChatTypes.CHANNEL  # Канал
# или
chat_type = ChatTypes.PERSONAL_CHAT  # Личный чат
```

## Обработка ошибок

При создании чата могут возникнуть различные ошибки. pybotx предоставляет специальные исключения для их обработки:

### ChatCreationError

Базовое исключение для всех ошибок, связанных с созданием чата. От него наследуются более специфические исключения:

- `ChatCreationProhibitedError` — создание чата запрещено (например, у бота нет прав на создание чатов)
- `InvalidChatTypeError` — указан недопустимый тип чата
- `InvalidChatNameError` — указано недопустимое название чата (например, слишком короткое или длинное)
- `InvalidChatDescriptionError` — указано недопустимое описание чата
- `InvalidChatAvatarError` — указан недопустимый аватар чата
- `InvalidChatMembersError` — указан недопустимый список участников чата

Пример обработки ошибок:

```python
from pybotx import (
    Bot, HandlerCollector, IncomingMessage, ChatTypes,
    ChatCreationError, ChatCreationProhibitedError
)

collector = HandlerCollector()

@collector.command("/create_chat", description="Создать групповой чат")
async def create_chat_handler(message: IncomingMessage, bot: Bot) -> None:
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите название чата")
        return

    try:
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=message.argument,
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[message.sender.huid],  # Добавляем отправителя в чат
        )
        await bot.answer_message(f"Чат успешно создан! ID: {chat_id}")
    except ChatCreationProhibitedError:
        await bot.answer_message("У бота нет прав на создание чатов")
    except ChatCreationError as e:
        await bot.answer_message(f"Ошибка при создании чата: {e}")
```

## Примеры использования

### Создание группового чата

```python
from uuid import UUID
from pybotx import Bot, HandlerCollector, IncomingMessage, ChatTypes, MentionBuilder

collector = HandlerCollector()

@collector.command("/create_group", description="Создать групповой чат")
async def create_group_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, указано ли название чата
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите название чата")
        return

    # Проверяем, есть ли упоминания пользователей
    if not message.mentions.contacts:
        await bot.answer_message(
            "Пожалуйста, упомяните пользователей, которых нужно добавить в чат"
        )
        return

    # Получаем HUID упомянутых пользователей
    user_huids = [contact.entity_id for contact in message.mentions.contacts]

    # Добавляем отправителя в список участников, если его там еще нет
    if message.sender.huid not in user_huids:
        user_huids.append(message.sender.huid)

    try:
        # Создаем групповой чат
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=message.argument,
            chat_type=ChatTypes.GROUP_CHAT,
            huids=user_huids,
            description="Чат создан с помощью бота",
        )

        # Создаем упоминание чата
        chat_mention = MentionBuilder.chat(chat_id)

        # Отправляем сообщение с упоминанием чата
        await bot.answer_message(f"Групповой чат {chat_mention} успешно создан!")
    except Exception as e:
        await bot.answer_message(f"Ошибка при создании чата: {e}")
```

### Создание канала

```python
from pybotx import Bot, HandlerCollector, IncomingMessage, ChatTypes, MentionBuilder

collector = HandlerCollector()

@collector.command("/create_channel", description="Создать канал")
async def create_channel_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, указано ли название канала
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите название канала")
        return

    # Проверяем, есть ли упоминания пользователей (будущих подписчиков)
    subscribers = []
    if message.mentions.contacts:
        subscribers = [contact.entity_id for contact in message.mentions.contacts]

    # Добавляем отправителя в список подписчиков
    if message.sender.huid not in subscribers:
        subscribers.append(message.sender.huid)

    try:
        # Создаем канал
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=message.argument,
            chat_type=ChatTypes.CHANNEL,
            huids=subscribers,
            description="Канал для публикации новостей и объявлений",
        )

        # Создаем упоминание канала
        chat_mention = MentionBuilder.chat(chat_id)

        # Отправляем сообщение с упоминанием канала
        await bot.answer_message(f"Канал {chat_mention} успешно создан!")

        # Отправляем первое сообщение в канал
        await bot.send_message(
            bot_id=message.bot.id,
            chat_id=chat_id,
            body="Добро пожаловать в новый канал! Здесь будут публиковаться важные новости и объявления.",
        )
    except Exception as e:
        await bot.answer_message(f"Ошибка при создании канала: {e}")
```

### Создание личного чата

```python
from pybotx import Bot, HandlerCollector, IncomingMessage, ChatTypes, MentionBuilder

collector = HandlerCollector()

@collector.command("/create_personal", description="Создать личный чат с пользователем")
async def create_personal_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминание пользователя
    if not message.mentions.contacts or len(message.mentions.contacts) != 1:
        await bot.answer_message(
            "Пожалуйста, упомяните одного пользователя, с которым нужно создать личный чат"
        )
        return

    # Получаем HUID упомянутого пользователя
    user_huid = message.mentions.contacts[0].entity_id

    try:
        # Создаем личный чат
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name="Личный чат",  # Название не так важно для личного чата
            chat_type=ChatTypes.PERSONAL_CHAT,
            huids=[user_huid, message.sender.huid],
        )

        # Создаем упоминание чата
        chat_mention = MentionBuilder.chat(chat_id)

        # Отправляем сообщение с упоминанием чата
        await bot.answer_message(f"Личный чат {chat_mention} успешно создан!")
    except Exception as e:
        await bot.answer_message(f"Ошибка при создании личного чата: {e}")
```

### Создание чата с аватаром

```python
import base64
from aiofiles import open as aio_open
from pybotx import Bot, HandlerCollector, IncomingMessage, ChatTypes, MentionBuilder

collector = HandlerCollector()

@collector.command("/create_chat_with_avatar", description="Создать чат с аватаром")
async def create_chat_with_avatar_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, указано ли название чата
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите название чата")
        return

    # Проверяем, есть ли файл в сообщении (будущий аватар)
    if not message.file:
        await bot.answer_message("Пожалуйста, прикрепите изображение для аватара чата")
        return

    # Проверяем, является ли файл изображением
    if not message.file.content_type.startswith("image/"):
        await bot.answer_message("Пожалуйста, прикрепите файл изображения")
        return

    # Получаем HUID отправителя
    user_huid = message.sender.huid

    try:
        # Читаем содержимое файла
        image_data = await message.file.read()

        # Кодируем изображение в base64
        avatar_base64 = base64.b64encode(image_data).decode("utf-8")

        # Создаем чат с аватаром
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=message.argument,
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[user_huid],
            description="Чат с аватаром",
            avatar=avatar_base64,
        )

        # Создаем упоминание чата
        chat_mention = MentionBuilder.chat(chat_id)

        # Отправляем сообщение с упоминанием чата
        await bot.answer_message(f"Чат {chat_mention} с аватаром успешно создан!")
    except Exception as e:
        await bot.answer_message(f"Ошибка при создании чата: {e}")
```

### Обработка различных ошибок

```python
from pybotx import (
    Bot, HandlerCollector, IncomingMessage, ChatTypes,
    ChatCreationError, ChatCreationProhibitedError,
    InvalidChatTypeError, InvalidChatNameError,
    InvalidChatDescriptionError, InvalidChatAvatarError,
    InvalidChatMembersError
)

collector = HandlerCollector()

@collector.command("/create_chat_safe", description="Создать чат с обработкой всех возможных ошибок")
async def create_chat_safe_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, указано ли название чата
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите название чата")
        return

    # Получаем HUID отправителя
    user_huid = message.sender.huid

    try:
        # Создаем чат
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=message.argument,
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[user_huid],
        )

        await bot.answer_message(f"Чат успешно создан! ID: {chat_id}")
    except ChatCreationProhibitedError:
        await bot.answer_message(
            "У бота нет прав на создание чатов. "
            "Обратитесь к администратору для предоставления необходимых прав."
        )
    except InvalidChatTypeError:
        await bot.answer_message(
            "Указан недопустимый тип чата. "
            "Допустимые типы: GROUP_CHAT, CHANNEL, PERSONAL_CHAT."
        )
    except InvalidChatNameError:
        await bot.answer_message(
            "Указано недопустимое название чата. "
            "Название должно содержать от 1 до 128 символов."
        )
    except InvalidChatDescriptionError:
        await bot.answer_message(
            "Указано недопустимое описание чата. "
            "Описание должно содержать не более 512 символов."
        )
    except InvalidChatAvatarError:
        await bot.answer_message(
            "Указан недопустимый аватар чата. "
            "Аватар должен быть в формате base64 и не превышать 1 МБ."
        )
    except InvalidChatMembersError:
        await bot.answer_message(
            "Указан недопустимый список участников чата. "
            "Убедитесь, что все HUID действительны и пользователи существуют."
        )
    except ChatCreationError as e:
        await bot.answer_message(f"Ошибка при создании чата: {e}")
    except Exception as e:
        await bot.answer_message(f"Непредвиденная ошибка: {e}")
```

## См. также

- [Отправка сообщений](/messages/sending/)
- [Упоминания](/messages/mentions/)
- [Поиск пользователей](/users/search/)
- [Список пользователей](/users/list/)
