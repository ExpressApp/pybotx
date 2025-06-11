# Упоминания

В этом разделе описаны способы создания и использования упоминаний пользователей и чатов в pybotx.

## Введение

Упоминания (mentions) — это специальные элементы в тексте сообщения, которые ссылаются на пользователей или чаты. При нажатии на упоминание пользователя открывается его профиль, а при нажатии на упоминание чата — сам чат.

В pybotx для создания упоминаний используется класс `MentionBuilder`, который позволяет создавать упоминания пользователей и чатов.

## MentionBuilder

Класс `MentionBuilder` предоставляет статические методы для создания упоминаний:

- `MentionBuilder.contact(huid)` — создает упоминание пользователя по его HUID
- `MentionBuilder.chat(chat_id)` — создает упоминание чата по его ID

```python
from uuid import UUID
from pybotx import MentionBuilder

# Создание упоминания пользователя
user_huid = UUID("123e4567-e89b-12d3-a456-426655440000")
user_mention = MentionBuilder.contact(user_huid)

# Создание упоминания чата
chat_id = UUID("123e4567-e89b-12d3-a456-426655440001")
chat_mention = MentionBuilder.chat(chat_id)

# Использование упоминаний в тексте сообщения
message_text = f"Привет, {user_mention}! Добро пожаловать в чат {chat_mention}."
```

## Упоминание пользователей

Для создания упоминания пользователя используется метод `MentionBuilder.contact()`:

```python
from uuid import UUID
from pybotx import MentionBuilder, HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/mention_user", description="Упомянуть пользователя")
async def mention_user_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем упоминание отправителя сообщения
    user_mention = MentionBuilder.contact(message.sender.huid)
    
    # Отправляем сообщение с упоминанием
    await bot.answer_message(f"Привет, {user_mention}!")
```

При отправке сообщения с упоминанием пользователя, упоминание будет отображаться как имя пользователя, выделенное цветом. При нажатии на упоминание будет открываться профиль пользователя.

## Упоминание чатов

Для создания упоминания чата используется метод `MentionBuilder.chat()`:

```python
from uuid import UUID
from pybotx import MentionBuilder, HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/mention_chat", description="Упомянуть текущий чат")
async def mention_chat_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем упоминание текущего чата
    chat_mention = MentionBuilder.chat(message.chat.id)
    
    # Отправляем сообщение с упоминанием
    await bot.answer_message(f"Вы находитесь в чате {chat_mention}")
```

При отправке сообщения с упоминанием чата, упоминание будет отображаться как название чата, выделенное цветом. При нажатии на упоминание будет открываться сам чат.

## Получение упоминаний из сообщения

Когда пользователь отправляет сообщение с упоминаниями, эти упоминания доступны через атрибут `message.mentions`:

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/echo_mentions", description="Показать упоминания в сообщении")
async def echo_mentions_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем упоминания пользователей
    contacts = message.mentions.contacts
    
    # Получаем упоминания чатов
    chats = message.mentions.chats
    
    # Формируем ответ
    response = []
    
    if contacts:
        response.append("Упомянутые пользователи:")
        for contact in contacts:
            response.append(f"- {contact}")
    
    if chats:
        if response:
            response.append("")
        response.append("Упомянутые чаты:")
        for chat in chats:
            response.append(f"- {chat}")
    
    if not response:
        response.append("В сообщении нет упоминаний")
    
    await bot.answer_message("\n".join(response))
```

Атрибут `message.mentions` содержит два списка:
- `message.mentions.contacts` — список упоминаний пользователей
- `message.mentions.chats` — список упоминаний чатов

Каждое упоминание содержит информацию о типе упоминания, его ID и отображаемом имени.

## Примеры использования

### Приветствие нового пользователя

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, MentionBuilder

collector = HandlerCollector()

@collector.command("/welcome", description="Поприветствовать пользователя")
async def welcome_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминания пользователей в сообщении
    if not message.mentions.contacts:
        await bot.answer_message("Пожалуйста, упомяните пользователя, которого хотите поприветствовать")
        return
    
    # Получаем первое упоминание пользователя
    user = message.mentions.contacts[0]
    
    # Создаем упоминание отправителя
    sender_mention = MentionBuilder.contact(message.sender.huid)
    
    # Отправляем приветствие
    await bot.answer_message(
        f"Привет, {user}! "
        f"Добро пожаловать в чат. Я {sender_mention}, рад познакомиться!"
    )
```

### Создание чата и приглашение пользователей

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, MentionBuilder, ChatTypes

collector = HandlerCollector()

@collector.command("/create_chat", description="Создать новый чат с упомянутыми пользователями")
async def create_chat_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминания пользователей в сообщении
    if not message.mentions.contacts:
        await bot.answer_message("Пожалуйста, упомяните пользователей, которых хотите добавить в чат")
        return
    
    # Проверяем, указано ли название чата
    if not message.argument:
        await bot.answer_message("Пожалуйста, укажите название чата")
        return
    
    # Получаем HUID упомянутых пользователей
    user_huids = [contact.entity_id for contact in message.mentions.contacts]
    
    # Добавляем отправителя в список участников
    if message.sender.huid not in user_huids:
        user_huids.append(message.sender.huid)
    
    try:
        # Создаем новый чат
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=message.argument,
            chat_type=ChatTypes.GROUP_CHAT,
            huids=user_huids,
        )
        
        # Создаем упоминание нового чата
        chat_mention = MentionBuilder.chat(chat_id)
        
        # Отправляем сообщение с упоминанием чата
        await bot.answer_message(f"Чат {chat_mention} успешно создан!")
    except Exception as e:
        await bot.answer_message(f"Ошибка при создании чата: {e}")
```

### Отправка сообщения с упоминаниями всех участников чата

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, MentionBuilder

collector = HandlerCollector()

@collector.command("/mention_all", description="Упомянуть всех участников чата")
async def mention_all_handler(message: IncomingMessage, bot: Bot) -> None:
    try:
        # Получаем список участников чата
        # Примечание: в реальном приложении нужно реализовать получение списка участников через API BotX
        chat_members = []  # Здесь должен быть код для получения списка участников
        
        if not chat_members:
            await bot.answer_message("Не удалось получить список участников чата")
            return
        
        # Создаем упоминания для каждого участника
        mentions = []
        for member in chat_members:
            mention = MentionBuilder.contact(member.huid)
            mentions.append(str(mention))
        
        # Отправляем сообщение с упоминаниями
        await bot.answer_message(
            f"Внимание, {', '.join(mentions)}!\n\n"
            f"{message.argument or 'Важное объявление!'}"
        )
    except Exception as e:
        await bot.answer_message(f"Ошибка: {e}")
```

### Форматирование сообщения с упоминаниями

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, MentionBuilder

collector = HandlerCollector()

@collector.command("/format", description="Форматировать сообщение с упоминаниями")
async def format_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминания в сообщении
    if not message.mentions.contacts and not message.mentions.chats:
        await bot.answer_message(
            "Пожалуйста, упомяните пользователей или чаты в сообщении.\n"
            "Пример: /format @Пользователь будет добавлен в чат #Общий"
        )
        return
    
    # Получаем текст сообщения без команды
    text = message.body.replace("/format", "", 1).strip()
    
    # Заменяем упоминания на форматированные строки
    formatted_text = text
    
    # Заменяем упоминания пользователей
    for contact in message.mentions.contacts:
        # Создаем новое упоминание с тем же HUID
        new_mention = MentionBuilder.contact(contact.entity_id)
        # Заменяем упоминание в тексте
        formatted_text = formatted_text.replace(str(contact), f"**{new_mention}**")
    
    # Заменяем упоминания чатов
    for chat in message.mentions.chats:
        # Создаем новое упоминание с тем же ID
        new_mention = MentionBuilder.chat(chat.entity_id)
        # Заменяем упоминание в тексте
        formatted_text = formatted_text.replace(str(chat), f"*{new_mention}*")
    
    # Отправляем отформатированное сообщение
    await bot.answer_message(formatted_text)
```

## См. также

- [Отправка сообщений](sending.md)
- [Редактирование сообщений](editing.md)
- [Удаление сообщений](deleting.md)
- [Кнопки и разметка](bubbles.md)
- [Вложения](attachments.md)