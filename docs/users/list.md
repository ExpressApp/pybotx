# Список пользователей

В этом разделе описаны способы получения списка пользователей с помощью pybotx.

## Введение

pybotx предоставляет возможность получения списка пользователей, зарегистрированных на CTS-сервере. Это может быть полезно для создания каталога пользователей, экспорта данных или для массовой рассылки сообщений.

Основной метод для получения списка пользователей — `bot.users_as_csv()`, который возвращает асинхронный генератор, позволяющий эффективно обрабатывать большие списки пользователей.

## Метод bot.users_as_csv

Метод `bot.users_as_csv()` имеет следующую сигнатуру:

```python
def users_as_csv(
    self,
    bot_id: UUID,
    *,
    cts_user: bool = True,
    unregistered: bool = False,
    botx: bool = False,
    wait_callback: bool = True,
    callback_timeout: Optional[float] = None,
) -> AsyncContextManager[AsyncGenerator[Dict[str, str], None]]:
    # ...
```

### Параметры

- `bot_id` (UUID) — идентификатор бота, от имени которого выполняется запрос
- `cts_user` (bool, по умолчанию True) — включать ли обычных пользователей CTS
- `unregistered` (bool, по умолчанию False) — включать ли незарегистрированных пользователей
- `botx` (bool, по умолчанию False) — включать ли ботов
- `wait_callback` (bool, по умолчанию True) — ожидать ли коллбэк от BotX API
- `callback_timeout` (float, опционально) — таймаут ожидания коллбэка

### Возвращаемое значение

Метод возвращает асинхронный контекстный менеджер, который при входе в контекст возвращает асинхронный генератор. Этот генератор при итерации возвращает словари, где каждый словарь представляет одного пользователя.

Каждый словарь содержит следующие ключи:

- `ad_login` — логин пользователя в Active Directory
- `ad_domain` — домен Active Directory
- `username` — отображаемое имя пользователя
- `company` — название компании
- `company_position` — должность в компании
- `department` — отдел
- `emails` — список email-адресов (разделенных запятыми)
- `huid` — уникальный идентификатор пользователя
- `is_admin` — является ли пользователь администратором ("true" или "false")
- `is_deleted` — удален ли пользователь ("true" или "false")

## Экспорт пользователей в CSV

Метод `bot.users_as_csv()` специально разработан для эффективного экспорта пользователей в CSV-формат. Он использует асинхронный генератор, что позволяет обрабатывать большие списки пользователей без загрузки всего списка в память.

Пример базового использования:

```python
import csv
from pybotx import Bot, HandlerCollector, IncomingMessage

collector = HandlerCollector()

@collector.command("/export_users", description="Экспортировать список пользователей в CSV")
async def export_users_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем CSV-файл в памяти
    csv_content = []
    
    # Добавляем заголовки
    headers = ["username", "company", "department", "emails", "huid"]
    csv_content.append(",".join(headers))
    
    # Получаем список пользователей
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        # Итерируемся по пользователям
        async for user in users:
            # Добавляем строку с данными пользователя
            row = [
                user["username"],
                user["company"],
                user["department"],
                user["emails"],
                user["huid"],
            ]
            # Экранируем запятые и кавычки
            escaped_row = [f'"{field.replace('"', '""')}"' for field in row]
            csv_content.append(",".join(escaped_row))
    
    # Создаем CSV-строку
    csv_str = "\n".join(csv_content)
    
    # Отправляем CSV-файл
    from io import BytesIO
    from pybotx import OutgoingAttachment
    
    # Создаем вложение из CSV-строки
    attachment = await OutgoingAttachment.from_bytes(
        csv_str.encode("utf-8"),
        filename="users.csv"
    )
    
    # Отправляем файл
    await bot.answer_message("Список пользователей:", file=attachment)
```

> **Note**
> 
> Метод `bot.users_as_csv()` может возвращать большое количество пользователей, особенно на крупных CTS-серверах. Рекомендуется использовать фильтрацию и ограничение количества пользователей, если вам не нужен полный список.

## Примеры использования

### Экспорт пользователей с фильтрацией по отделу

```python
import csv
from io import StringIO
from pybotx import Bot, HandlerCollector, IncomingMessage, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/export_department", description="Экспортировать пользователей определенного отдела")
async def export_department_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем название отдела из аргумента команды
    department_name = message.argument
    
    if not department_name:
        await bot.answer_message("Пожалуйста, укажите название отдела")
        return
    
    # Создаем CSV-файл в памяти
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer, quoting=csv.QUOTE_ALL)
    
    # Записываем заголовки
    writer.writerow([
        "Имя пользователя",
        "Компания",
        "Должность",
        "Отдел",
        "Email",
        "HUID"
    ])
    
    # Счетчик пользователей
    user_count = 0
    
    # Получаем список пользователей
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        # Итерируемся по пользователям
        async for user in users:
            # Фильтруем по отделу (регистронезависимое сравнение)
            if department_name.lower() in user["department"].lower():
                # Записываем данные пользователя
                writer.writerow([
                    user["username"],
                    user["company"],
                    user["company_position"],
                    user["department"],
                    user["emails"],
                    user["huid"]
                ])
                user_count += 1
    
    # Если не найдено пользователей
    if user_count == 0:
        await bot.answer_message(f"Пользователи из отдела '{department_name}' не найдены")
        return
    
    # Получаем CSV-строку
    csv_str = csv_buffer.getvalue()
    
    # Создаем вложение из CSV-строки
    attachment = await OutgoingAttachment.from_bytes(
        csv_str.encode("utf-8"),
        filename=f"users_{department_name}.csv"
    )
    
    # Отправляем файл
    await bot.answer_message(
        f"Список пользователей из отдела '{department_name}' ({user_count} чел.):",
        file=attachment
    )
```

### Создание адресной книги с контактами

```python
import csv
from io import StringIO
from pybotx import Bot, HandlerCollector, IncomingMessage, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/address_book", description="Создать адресную книгу")
async def address_book_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем CSV-файл в памяти
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer, quoting=csv.QUOTE_ALL)
    
    # Записываем заголовки
    writer.writerow([
        "Имя",
        "Компания",
        "Должность",
        "Отдел",
        "Email",
        "HUID"
    ])
    
    # Счетчик пользователей
    user_count = 0
    
    # Получаем список пользователей
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        # Итерируемся по пользователям
        async for user in users:
            # Пропускаем пользователей без email
            if not user["emails"]:
                continue
            
            # Пропускаем удаленных пользователей
            if user["is_deleted"] == "true":
                continue
            
            # Записываем данные пользователя
            writer.writerow([
                user["username"],
                user["company"],
                user["company_position"],
                user["department"],
                user["emails"],
                user["huid"]
            ])
            user_count += 1
    
    # Получаем CSV-строку
    csv_str = csv_buffer.getvalue()
    
    # Создаем вложение из CSV-строки
    attachment = await OutgoingAttachment.from_bytes(
        csv_str.encode("utf-8"),
        filename="address_book.csv"
    )
    
    # Отправляем файл
    await bot.answer_message(
        f"Адресная книга ({user_count} контактов):",
        file=attachment
    )
```

### Поиск администраторов

```python
from pybotx import Bot, HandlerCollector, IncomingMessage

collector = HandlerCollector()

@collector.command("/find_all_admins", description="Найти всех администраторов")
async def find_all_admins_handler(message: IncomingMessage, bot: Bot) -> None:
    # Список администраторов
    admins = []
    
    # Получаем список пользователей
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        # Итерируемся по пользователям
        async for user in users:
            # Фильтруем администраторов
            if user["is_admin"] == "true" and user["is_deleted"] == "false":
                admins.append({
                    "username": user["username"],
                    "department": user["department"],
                    "emails": user["emails"],
                    "huid": user["huid"]
                })
    
    # Если не найдено администраторов
    if not admins:
        await bot.answer_message("Администраторы не найдены")
        return
    
    # Формируем сообщение
    response = [f"Найдено администраторов: {len(admins)}"]
    
    # Сортируем по имени
    admins.sort(key=lambda x: x["username"])
    
    # Добавляем информацию о каждом администраторе
    for admin in admins:
        response.append(
            f"\n- {admin['username']}\n"
            f"  Отдел: {admin['department'] or 'Не указан'}\n"
            f"  Email: {admin['emails'] or 'Не указан'}"
        )
    
    # Отправляем сообщение
    await bot.answer_message("".join(response))
```

### Экспорт пользователей с разбивкой по компаниям

```python
import csv
from io import StringIO
from collections import defaultdict
from pybotx import Bot, HandlerCollector, IncomingMessage, OutgoingAttachment

collector = HandlerCollector()

@collector.command("/export_by_company", description="Экспортировать пользователей с разбивкой по компаниям")
async def export_by_company_handler(message: IncomingMessage, bot: Bot) -> None:
    # Словарь для хранения пользователей по компаниям
    users_by_company = defaultdict(list)
    
    # Получаем список пользователей
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        # Итерируемся по пользователям
        async for user in users:
            # Пропускаем удаленных пользователей
            if user["is_deleted"] == "true":
                continue
            
            # Определяем компанию (если не указана, используем "Без компании")
            company = user["company"] or "Без компании"
            
            # Добавляем пользователя в соответствующий список
            users_by_company[company].append(user)
    
    # Если не найдено пользователей
    if not users_by_company:
        await bot.answer_message("Пользователи не найдены")
        return
    
    # Создаем CSV-файл в памяти
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer, quoting=csv.QUOTE_ALL)
    
    # Записываем заголовки
    writer.writerow([
        "Компания",
        "Имя пользователя",
        "Должность",
        "Отдел",
        "Email",
        "HUID"
    ])
    
    # Общий счетчик пользователей
    total_users = 0
    
    # Записываем данные пользователей, сгруппированные по компаниям
    for company, company_users in sorted(users_by_company.items()):
        # Сортируем пользователей по имени
        company_users.sort(key=lambda x: x["username"])
        
        # Записываем данные каждого пользователя
        for user in company_users:
            writer.writerow([
                company,
                user["username"],
                user["company_position"],
                user["department"],
                user["emails"],
                user["huid"]
            ])
            total_users += 1
    
    # Получаем CSV-строку
    csv_str = csv_buffer.getvalue()
    
    # Создаем вложение из CSV-строки
    attachment = await OutgoingAttachment.from_bytes(
        csv_str.encode("utf-8"),
        filename="users_by_company.csv"
    )
    
    # Отправляем файл
    await bot.answer_message(
        f"Список пользователей по компаниям ({total_users} чел., {len(users_by_company)} компаний):",
        file=attachment
    )
```

### Генерация статистики по отделам

```python
from collections import defaultdict
from pybotx import Bot, HandlerCollector, IncomingMessage

collector = HandlerCollector()

@collector.command("/department_stats", description="Статистика по отделам")
async def department_stats_handler(message: IncomingMessage, bot: Bot) -> None:
    # Словарь для хранения статистики по отделам
    department_stats = defaultdict(int)
    
    # Общее количество пользователей
    total_users = 0
    
    # Получаем список пользователей
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        # Итерируемся по пользователям
        async for user in users:
            # Пропускаем удаленных пользователей
            if user["is_deleted"] == "true":
                continue
            
            # Определяем отдел (если не указан, используем "Без отдела")
            department = user["department"] or "Без отдела"
            
            # Увеличиваем счетчик для отдела
            department_stats[department] += 1
            total_users += 1
    
    # Если не найдено пользователей
    if not department_stats:
        await bot.answer_message("Пользователи не найдены")
        return
    
    # Формируем сообщение
    response = [f"Статистика по отделам (всего пользователей: {total_users}):\n"]
    
    # Сортируем отделы по количеству пользователей (по убыванию)
    sorted_departments = sorted(
        department_stats.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Добавляем информацию о каждом отделе
    for department, count in sorted_departments:
        percentage = (count / total_users) * 100
        response.append(f"- {department}: {count} чел. ({percentage:.1f}%)")
    
    # Отправляем сообщение
    await bot.answer_message("\n".join(response))
```

## См. также

- [Поиск пользователей](search.md)
- [Создание чатов](../chats/create.md)
- [Упоминания](../messages/mentions.md)
- [Отправка сообщений](../messages/sending.md)
- [Вложения](../messages/attachments.md)