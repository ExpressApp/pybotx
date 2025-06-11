# Push-уведомления

В этом разделе описаны способы отправки push-уведомлений в SmartApp с помощью pybotx.

## Введение

Push-уведомления — это механизм, позволяющий серверу инициировать взаимодействие с клиентом. В контексте SmartApp push-уведомления используются для:

- Информирования пользователя о важных событиях
- Обновления данных в интерфейсе SmartApp
- Отображения счётчиков непрочитанных сообщений или уведомлений (badge)
- Привлечения внимания пользователя к приложению

pybotx предоставляет несколько способов отправки push-уведомлений, в зависимости от конкретного сценария использования.

## Отправка push-уведомлений

### Базовый способ отправки push-уведомлений

Самый простой способ отправить push-уведомление — использовать метод `bot.send_smartapp_notification`:

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent

collector = HandlerCollector()

@collector.smartapp_event
async def handle_smartapp_event(event: SmartAppEvent, bot: Bot) -> None:
    # Отправляем push-уведомление
    await bot.send_smartapp_notification(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        smartapp_id=event.smartapp_id,
        data={"message": "Новое уведомление!"},
        opts={"silent": False},
    )
```

### Параметры метода send_smartapp_notification

Метод `bot.send_smartapp_notification` имеет следующие параметры:

- `bot_id` (UUID) — идентификатор бота, от имени которого отправляется уведомление
- `chat_id` (UUID) — идентификатор чата, в который отправляется уведомление
- `smartapp_id` (UUID) — идентификатор SmartApp
- `data` (Dict[str, Any]) — данные, которые будут переданы в SmartApp
- `opts` (Dict[str, Any], опционально) — дополнительные опции уведомления:
  - `silent` (bool) — отправлять ли уведомление без звука
  - `force_dnd` (bool) — отправлять ли уведомление даже в режиме "Не беспокоить"
- `wait_callback` (bool, по умолчанию True) — ожидать ли коллбэк от BotX API
- `callback_timeout` (float, опционально) — таймаут ожидания коллбэка

### Отправка push-уведомлений с помощью pybotx-smartapp-rpc

Если вы используете библиотеку `pybotx-smartapp-rpc`, то можно отправлять push-уведомления с помощью функции `send_push`:

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent
from pybotx_smartapp_rpc import RPCRouter, send_push

# Создаем RPC-роутер
rpc_router = RPCRouter()

@rpc_router.method("notify_user")
async def notify_user(bot: Bot, event: SmartAppEvent, message: str) -> dict:
    """Отправка уведомления пользователю."""
    # Отправляем push-уведомление
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="notification",
        params={"message": message, "timestamp": datetime.now().isoformat()},
    )
    
    return {"success": True}
```

Функция `send_push` автоматически извлекает необходимые параметры из объекта `SmartAppEvent` и отправляет push-уведомление с указанным методом и параметрами.

## Настройка badge-счётчика

Badge-счётчик — это числовой индикатор, отображаемый на иконке приложения, который показывает количество непрочитанных сообщений или уведомлений. В pybotx можно управлять badge-счётчиком с помощью специальных параметров в push-уведомлениях.

### Установка значения badge-счётчика

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent

collector = HandlerCollector()

@collector.smartapp_event
async def handle_smartapp_event(event: SmartAppEvent, bot: Bot) -> None:
    # Получаем количество непрочитанных сообщений
    unread_count = await get_unread_messages_count(event.sender.huid)
    
    # Отправляем push-уведомление с установкой badge-счётчика
    await bot.send_smartapp_notification(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        smartapp_id=event.smartapp_id,
        data={
            "message": "У вас новое сообщение!",
            "badge": unread_count,  # Устанавливаем значение badge-счётчика
        },
        opts={"silent": False},
    )
```

### Инкремент badge-счётчика

Вместо установки конкретного значения, можно увеличить текущее значение badge-счётчика:

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent

collector = HandlerCollector()

@collector.smartapp_event
async def handle_smartapp_event(event: SmartAppEvent, bot: Bot) -> None:
    # Отправляем push-уведомление с инкрементом badge-счётчика
    await bot.send_smartapp_notification(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        smartapp_id=event.smartapp_id,
        data={
            "message": "У вас новое сообщение!",
            "badge_increment": 1,  # Увеличиваем badge-счётчик на 1
        },
        opts={"silent": False},
    )
```

### Сброс badge-счётчика

Для сброса badge-счётчика в ноль:

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent

collector = HandlerCollector()

@collector.smartapp_event
async def handle_smartapp_event(event: SmartAppEvent, bot: Bot) -> None:
    # Отправляем push-уведомление со сбросом badge-счётчика
    await bot.send_smartapp_notification(
        bot_id=event.bot.id,
        chat_id=event.chat.id,
        smartapp_id=event.smartapp_id,
        data={
            "message": "Все сообщения прочитаны",
            "badge": 0,  # Сбрасываем badge-счётчик в ноль
        },
        opts={"silent": True},
    )
```

> **Note**
> 
> Badge-счётчик отображается не на всех платформах. Его поддержка зависит от операционной системы и настроек устройства пользователя.

## Типы push-уведомлений

В зависимости от сценария использования, push-уведомления можно разделить на несколько типов:

### Информационные уведомления

Используются для информирования пользователя о событиях, не требующих немедленного действия:

```python
await bot.send_smartapp_notification(
    bot_id=event.bot.id,
    chat_id=event.chat.id,
    smartapp_id=event.smartapp_id,
    data={
        "type": "info",
        "message": "Ваш отчет успешно сформирован",
    },
    opts={"silent": True},
)
```

### Уведомления о действиях

Используются для информирования пользователя о действиях, которые требуют его внимания:

```python
await bot.send_smartapp_notification(
    bot_id=event.bot.id,
    chat_id=event.chat.id,
    smartapp_id=event.smartapp_id,
    data={
        "type": "action",
        "message": "Вам назначена новая задача",
        "action_id": "task-123",
    },
    opts={"silent": False},
)
```

### Уведомления об обновлениях данных

Используются для обновления данных в интерфейсе SmartApp без необходимости перезагрузки:

```python
await bot.send_smartapp_notification(
    bot_id=event.bot.id,
    chat_id=event.chat.id,
    smartapp_id=event.smartapp_id,
    data={
        "type": "data_update",
        "entity": "tasks",
        "data": updated_tasks,
    },
    opts={"silent": True},
)
```

### Системные уведомления

Используются для информирования пользователя о системных событиях:

```python
await bot.send_smartapp_notification(
    bot_id=event.bot.id,
    chat_id=event.chat.id,
    smartapp_id=event.smartapp_id,
    data={
        "type": "system",
        "message": "Соединение с сервером восстановлено",
    },
    opts={"silent": True},
)
```

## Примеры использования

### Пример 1: Уведомление о новом сообщении

```python
from pybotx import Bot, HandlerCollector, IncomingMessage

collector = HandlerCollector()

@collector.command("/notify", description="Отправить уведомление пользователю")
async def notify_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, есть ли упоминания пользователей
    if not message.mentions.contacts:
        await bot.answer_message("Пожалуйста, упомяните пользователя, которому нужно отправить уведомление")
        return
    
    # Получаем HUID упомянутого пользователя
    user_huid = message.mentions.contacts[0].entity_id
    
    # Получаем текст уведомления
    notification_text = message.body.replace("/notify", "", 1).strip()
    if not notification_text:
        notification_text = "Вам отправлено уведомление"
    
    # Отправляем push-уведомление
    try:
        await bot.send_smartapp_notification(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            smartapp_id=UUID("00000000-0000-0000-0000-000000000000"),  # ID вашего SmartApp
            data={
                "type": "message",
                "message": notification_text,
                "sender": message.sender.username,
                "timestamp": datetime.now().isoformat(),
                "badge_increment": 1,
            },
            opts={"silent": False},
        )
        
        await bot.answer_message("Уведомление успешно отправлено")
    except Exception as e:
        await bot.answer_message(f"Ошибка при отправке уведомления: {e}")
```

### Пример 2: Система задач с уведомлениями

```python
import uuid
from datetime import datetime
from pybotx import Bot, HandlerCollector, SmartAppEvent
from pybotx_smartapp_rpc import RPCRouter, send_push

# Создаем RPC-роутер
rpc_router = RPCRouter()

# Хранилище задач (в реальном приложении использовалась бы база данных)
tasks = {}

@rpc_router.method("create_task")
async def create_task(bot: Bot, event: SmartAppEvent, title: str, assignee_huid: str) -> dict:
    """Создание новой задачи с уведомлением."""
    # Создаем задачу
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": title,
        "assignee_huid": assignee_huid,
        "status": "new",
        "created_at": datetime.now().isoformat(),
        "created_by": str(event.sender.huid),
    }
    
    # Сохраняем задачу
    tasks[task_id] = task
    
    # Отправляем уведомление создателю
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="task_created",
        params={
            "task": task,
            "message": f"Задача '{title}' успешно создана",
        },
    )
    
    # Отправляем уведомление исполнителю (если это не создатель)
    if assignee_huid != str(event.sender.huid):
        # В реальном приложении здесь был бы код для отправки уведомления другому пользователю
        pass
    
    return {"success": True, "task": task}

@rpc_router.method("update_task_status")
async def update_task_status(bot: Bot, event: SmartAppEvent, task_id: str, status: str) -> dict:
    """Обновление статуса задачи с уведомлением."""
    # Проверяем существование задачи
    if task_id not in tasks:
        return {"success": False, "error": "Задача не найдена"}
    
    # Получаем задачу
    task = tasks[task_id]
    
    # Обновляем статус
    old_status = task["status"]
    task["status"] = status
    task["updated_at"] = datetime.now().isoformat()
    task["updated_by"] = str(event.sender.huid)
    
    # Сохраняем обновленную задачу
    tasks[task_id] = task
    
    # Отправляем уведомление об обновлении статуса
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="task_updated",
        params={
            "task": task,
            "message": f"Статус задачи '{task['title']}' изменен с '{old_status}' на '{status}'",
            "badge_increment": 1,
        },
    )
    
    return {"success": True, "task": task}

# Регистрируем RPC-роутер в обработчике синхронных событий
collector = HandlerCollector()

@collector.sync_smartapp_event
async def handle_sync_smartapp_event(event: SmartAppEvent, bot: Bot):
    # Обрабатываем RPC-запросы
    return await rpc_router.handle(bot, event)
```

### Пример 3: Система уведомлений с управлением badge-счётчиком

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent
from pybotx_smartapp_rpc import RPCRouter, send_push
from typing import Dict, List, Any
import uuid
from datetime import datetime

# Создаем RPC-роутер
rpc_router = RPCRouter()

# Хранилище уведомлений (в реальном приложении использовалась бы база данных)
notifications: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

@rpc_router.method("get_notifications")
async def get_notifications(bot: Bot, event: SmartAppEvent) -> dict:
    """Получение списка уведомлений пользователя."""
    user_huid = str(event.sender.huid)
    
    # Получаем уведомления пользователя
    user_notifications = notifications.get(user_huid, {"unread": [], "read": []})
    
    # Возвращаем уведомления
    return {
        "notifications": {
            "unread": user_notifications["unread"],
            "read": user_notifications["read"],
        },
        "unread_count": len(user_notifications["unread"]),
    }

@rpc_router.method("mark_notification_as_read")
async def mark_notification_as_read(bot: Bot, event: SmartAppEvent, notification_id: str) -> dict:
    """Отметка уведомления как прочитанного."""
    user_huid = str(event.sender.huid)
    
    # Проверяем, есть ли уведомления у пользователя
    if user_huid not in notifications:
        return {"success": False, "error": "Уведомления не найдены"}
    
    # Ищем уведомление среди непрочитанных
    user_notifications = notifications[user_huid]
    notification = None
    
    for i, notif in enumerate(user_notifications["unread"]):
        if notif["id"] == notification_id:
            notification = user_notifications["unread"].pop(i)
            break
    
    if not notification:
        return {"success": False, "error": "Уведомление не найдено"}
    
    # Отмечаем уведомление как прочитанное
    notification["read_at"] = datetime.now().isoformat()
    user_notifications["read"].append(notification)
    
    # Обновляем хранилище
    notifications[user_huid] = user_notifications
    
    # Отправляем push-уведомление с обновленным badge-счётчиком
    unread_count = len(user_notifications["unread"])
    
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="notifications_updated",
        params={
            "unread_count": unread_count,
            "badge": unread_count,  # Устанавливаем badge-счётчик равным количеству непрочитанных уведомлений
        },
    )
    
    return {
        "success": True,
        "unread_count": unread_count,
    }

@rpc_router.method("mark_all_notifications_as_read")
async def mark_all_notifications_as_read(bot: Bot, event: SmartAppEvent) -> dict:
    """Отметка всех уведомлений как прочитанных."""
    user_huid = str(event.sender.huid)
    
    # Проверяем, есть ли уведомления у пользователя
    if user_huid not in notifications:
        return {"success": True, "unread_count": 0}
    
    # Получаем уведомления пользователя
    user_notifications = notifications[user_huid]
    
    # Отмечаем все уведомления как прочитанные
    now = datetime.now().isoformat()
    for notification in user_notifications["unread"]:
        notification["read_at"] = now
        user_notifications["read"].append(notification)
    
    # Очищаем список непрочитанных уведомлений
    user_notifications["unread"] = []
    
    # Обновляем хранилище
    notifications[user_huid] = user_notifications
    
    # Отправляем push-уведомление с обновленным badge-счётчиком
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="notifications_updated",
        params={
            "unread_count": 0,
            "badge": 0,  # Сбрасываем badge-счётчик в ноль
        },
    )
    
    return {
        "success": True,
        "unread_count": 0,
    }

@rpc_router.method("send_notification")
async def send_notification(
    bot: Bot, 
    event: SmartAppEvent, 
    recipient_huid: str, 
    title: str, 
    message: str, 
    type: str = "info"
) -> dict:
    """Отправка уведомления пользователю."""
    # Создаем уведомление
    notification = {
        "id": str(uuid.uuid4()),
        "title": title,
        "message": message,
        "type": type,
        "created_at": datetime.now().isoformat(),
        "created_by": str(event.sender.huid),
    }
    
    # Добавляем уведомление в хранилище
    if recipient_huid not in notifications:
        notifications[recipient_huid] = {"unread": [], "read": []}
    
    notifications[recipient_huid]["unread"].append(notification)
    
    # Получаем количество непрочитанных уведомлений
    unread_count = len(notifications[recipient_huid]["unread"])
    
    # В реальном приложении здесь был бы код для отправки push-уведомления получателю
    # с использованием его HUID
    
    return {
        "success": True,
        "notification": notification,
        "unread_count": unread_count,
    }

# Регистрируем RPC-роутер в обработчике синхронных событий
collector = HandlerCollector()

@collector.sync_smartapp_event
async def handle_sync_smartapp_event(event: SmartAppEvent, bot: Bot):
    # Обрабатываем RPC-запросы
    return await rpc_router.handle(bot, event)
```

## См. также

- [Обзор SmartApp](overview.md)
- [RPC в SmartApp](rpc.md)
- [UI-компоненты](ui.md)
- [Интеграция с FastAPI](../integration/fastapi.md)
- [Отправка сообщений](../messages/sending.md)