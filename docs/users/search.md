# Поиск пользователей

В этом разделе описаны способы поиска пользователей с помощью pybotx.


## Введение

pybotx предоставляет возможность поиска пользователей по их уникальному идентификатору (HUID). Это может быть полезно для получения информации о пользователе, проверки его существования или для дальнейшего взаимодействия с ним.

Основной метод для поиска пользователей — `bot.search_user_by_huid()`, который возвращает информацию о пользователе по его HUID.

## Метод bot.search_user_by_huid

Метод `bot.search_user_by_huid()` имеет следующую сигнатуру:

```python
async def search_user_by_huid(
    self,
    bot_id: UUID,
    huid: UUID,
    *,
    wait_callback: bool = True,
    callback_timeout: Optional[float] = None,
) -> UserFromSearch:
    # ...
```

### Параметры

- `bot_id` (UUID) — идентификатор бота, от имени которого выполняется поиск
- `huid` (UUID) — уникальный идентификатор пользователя, которого нужно найти
- `wait_callback` (bool, по умолчанию True) — ожидать ли коллбэк от BotX API
- `callback_timeout` (float, опционально) — таймаут ожидания коллбэка

### Возвращаемое значение

Метод возвращает объект типа `UserFromSearch`, который содержит информацию о найденном пользователе:

```python
@dataclass
class UserFromSearch:
    """User information from search."""

    ad_login: str
    ad_domain: str
    username: str
    company: str
    company_position: str
    department: str
    emails: List[str]
    huid: UUID
    is_admin: bool
    is_deleted: bool
    devices: List[UserDevice]
```

Поля объекта `UserFromSearch`:

- `ad_login` — логин пользователя в Active Directory
- `ad_domain` — домен Active Directory
- `username` — отображаемое имя пользователя
- `company` — название компании
- `company_position` — должность в компании
- `department` — отдел
- `emails` — список email-адресов
- `huid` — уникальный идентификатор пользователя
- `is_admin` — является ли пользователь администратором
- `is_deleted` — удален ли пользователь
- `devices` — список устройств пользователя

## Обработка ошибок

При поиске пользователя могут возникнуть различные ошибки. Основная ошибка, которую нужно обрабатывать — `UserNotFoundError`, которая возникает, когда пользователь с указанным HUID не найден.

```python
from pybotx import Bot, HandlerCollector, IncomingMessage, UserNotFoundError

collector = HandlerCollector()

@collector.command("/find_user", description="Найти пользователя по HUID")
async def find_user_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем HUID из аргумента команды
    try:
        huid = UUID(message.argument)
    except ValueError:
        await bot.answer_message("Пожалуйста, укажите корректный HUID")
        return

    try:
        # Ищем пользователя
        user = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=huid,
        )

        # Формируем информацию о пользователе
        user_info = (
            f"Имя: {user.username}\n"
            f"Компания: {user.company}\n"
            f"Должность: {user.company_position}\n"
            f"Отдел: {user.department}\n"
            f"Email: {', '.join(user.emails) if user.emails else 'Не указан'}\n"
            f"Администратор: {'Да' if user.is_admin else 'Нет'}\n"
            f"Удален: {'Да' if user.is_deleted else 'Нет'}"
        )

        await bot.answer_message(user_info)
    except UserNotFoundError:
        await bot.answer_message(
            "Пользователь не найден. Возможно, пользователь не существует "
            "или находится на другом CTS-сервере."
        )
```

> **Note**
> 
> Ошибка `UserNotFoundError` может возникнуть не только если пользователь не существует, но и если бот и пользователь находятся на разных CTS-серверах. В этом случае бот не сможет получить информацию о пользователе.

## Примеры использования

### Поиск информации о текущем пользователе

```python
import dataclasses
from pybotx import Bot, HandlerCollector, IncomingMessage, UserNotFoundError

collector = HandlerCollector()

@collector.command("/my_info", description="Получить информацию о себе")
async def my_info_handler(message: IncomingMessage, bot: Bot) -> None:
    try:
        # Ищем пользователя по HUID отправителя сообщения
        user = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=message.sender.huid,
        )

        # Преобразуем объект в словарь для удобного вывода
        user_dict = dataclasses.asdict(user)

        # Формируем информацию о пользователе
        user_info = "Информация о вас:\n\n"
        for key, value in user_dict.items():
            if key == "devices":  # Пропускаем список устройств для краткости
                continue

            # Форматируем значение
            if isinstance(value, list):
                formatted_value = ", ".join(str(item) for item in value) if value else "Не указано"
            elif value is None or value == "":
                formatted_value = "Не указано"
            elif isinstance(value, bool):
                formatted_value = "Да" if value else "Нет"
            else:
                formatted_value = str(value)

            # Добавляем поле в информацию
            user_info += f"{key}: {formatted_value}\n"

        await bot.answer_message(user_info)
    except UserNotFoundError:
        await bot.answer_message(
            "Не удалось получить информацию о вас. "
            "Возможно, вы находитесь на другом CTS-сервере."
        )
```

### Проверка существования пользователя перед добавлением в чат

```python
from pybotx import (
    Bot, HandlerCollector, IncomingMessage, ChatTypes,
    UserNotFoundError, MentionBuilder
)

collector = HandlerCollector()

@collector.command("/add_to_chat", description="Добавить пользователя в чат")
async def add_to_chat_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминания пользователей
    if not message.mentions.contacts:
        await bot.answer_message(
            "Пожалуйста, упомяните пользователя, которого нужно добавить в чат"
        )
        return

    # Получаем HUID упомянутого пользователя
    user_huid = message.mentions.contacts[0].entity_id

    try:
        # Проверяем существование пользователя
        user = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=user_huid,
        )

        # Если пользователь найден, создаем чат с ним
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=f"Чат с {user.username}",
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[user_huid, message.sender.huid],
        )

        # Создаем упоминание чата
        chat_mention = MentionBuilder.chat(chat_id)

        # Отправляем сообщение с упоминанием чата
        await bot.answer_message(f"Чат {chat_mention} успешно создан!")
    except UserNotFoundError:
        await bot.answer_message(
            "Пользователь не найден. Возможно, пользователь не существует "
            "или находится на другом CTS-сервере."
        )
```

### Получение списка администраторов

```python
from pybotx import Bot, HandlerCollector, IncomingMessage, UserNotFoundError

collector = HandlerCollector()

@collector.command("/find_admins", description="Найти администраторов среди упомянутых пользователей")
async def find_admins_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминания пользователей
    if not message.mentions.contacts:
        await bot.answer_message(
            "Пожалуйста, упомяните пользователей, среди которых нужно найти администраторов"
        )
        return

    # Получаем HUID упомянутых пользователей
    user_huids = [contact.entity_id for contact in message.mentions.contacts]

    # Списки для хранения результатов
    admins = []
    non_admins = []
    not_found = []

    # Проверяем каждого пользователя
    for huid in user_huids:
        try:
            user = await bot.search_user_by_huid(
                bot_id=message.bot.id,
                huid=huid,
            )

            if user.is_admin:
                admins.append(user.username)
            else:
                non_admins.append(user.username)
        except UserNotFoundError:
            not_found.append(str(huid))

    # Формируем ответ
    response = []

    if admins:
        response.append("Администраторы:")
        for admin in admins:
            response.append(f"- {admin}")

    if non_admins:
        if response:
            response.append("")
        response.append("Не администраторы:")
        for non_admin in non_admins:
            response.append(f"- {non_admin}")

    if not_found:
        if response:
            response.append("")
        response.append("Не найдены:")
        for huid in not_found:
            response.append(f"- {huid}")

    if not response:
        response.append("Не удалось получить информацию о пользователях")

    await bot.answer_message("\n".join(response))
```

### Поиск пользователя с обработкой всех возможных ошибок

```python
from uuid import UUID
from pybotx import (
    Bot, HandlerCollector, IncomingMessage,
    UserNotFoundError, BotXMethodCallbackTimeoutError
)

collector = HandlerCollector()

@collector.command("/find_user_safe", description="Найти пользователя с обработкой всех ошибок")
async def find_user_safe_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем HUID из аргумента команды
    try:
        huid = UUID(message.argument)
    except ValueError:
        await bot.answer_message(
            "Пожалуйста, укажите корректный HUID в формате UUID "
            "(например, 123e4567-e89b-12d3-a456-426655440000)"
        )
        return

    try:
        # Ищем пользователя с коротким таймаутом
        user = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=huid,
            callback_timeout=5.0,  # 5 секунд таймаут
        )

        # Формируем информацию о пользователе
        user_info = (
            f"Имя: {user.username}\n"
            f"Компания: {user.company}\n"
            f"Должность: {user.company_position}\n"
            f"Отдел: {user.department}\n"
            f"Email: {', '.join(user.emails) if user.emails else 'Не указан'}\n"
            f"Администратор: {'Да' if user.is_admin else 'Нет'}\n"
            f"Удален: {'Да' if user.is_deleted else 'Нет'}"
        )

        await bot.answer_message(user_info)
    except UserNotFoundError:
        await bot.answer_message(
            "Пользователь не найден. Возможно, пользователь не существует "
            "или находится на другом CTS-сервере."
        )
    except BotXMethodCallbackTimeoutError:
        await bot.answer_message(
            "Превышено время ожидания ответа от сервера. "
            "Пожалуйста, повторите запрос позже."
        )
    except Exception as e:
        await bot.answer_message(f"Произошла непредвиденная ошибка: {e}")
```

### Получение информации о нескольких пользователях

```python
from uuid import UUID
from pybotx import Bot, HandlerCollector, IncomingMessage, UserNotFoundError

collector = HandlerCollector()

@collector.command("/compare_users", description="Сравнить информацию о двух пользователях")
async def compare_users_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминания пользователей
    if not message.mentions.contacts or len(message.mentions.contacts) < 2:
        await bot.answer_message(
            "Пожалуйста, упомяните двух пользователей для сравнения"
        )
        return

    # Получаем HUID первых двух упомянутых пользователей
    user1_huid = message.mentions.contacts[0].entity_id
    user2_huid = message.mentions.contacts[1].entity_id

    # Получаем информацию о пользователях
    user1_info = None
    user2_info = None

    try:
        user1 = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=user1_huid,
        )
        user1_info = (
            f"Имя: {user1.username}\n"
            f"Компания: {user1.company}\n"
            f"Должность: {user1.company_position}\n"
            f"Отдел: {user1.department}"
        )
    except UserNotFoundError:
        user1_info = "Пользователь не найден"

    try:
        user2 = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=user2_huid,
        )
        user2_info = (
            f"Имя: {user2.username}\n"
            f"Компания: {user2.company}\n"
            f"Должность: {user2.company_position}\n"
            f"Отдел: {user2.department}"
        )
    except UserNotFoundError:
        user2_info = "Пользователь не найден"

    # Формируем ответ
    response = (
        f"Информация о первом пользователе:\n{user1_info}\n\n"
        f"Информация о втором пользователе:\n{user2_info}"
    )

    await bot.answer_message(response)
```

## См. также

- [Список пользователей](/users/list/)
- [Создание чатов](/chats/create/)
- [Упоминания](/messages/mentions/)
- [Отправка сообщений](/messages/sending/)
