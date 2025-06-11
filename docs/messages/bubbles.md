# Кнопки и разметка

В этом разделе описаны способы добавления интерактивных кнопок к сообщениям в pybotx.

## Введение

pybotx позволяет добавлять интерактивные кнопки к сообщениям, что делает взаимодействие с ботом более удобным и интуитивным. Кнопки могут выполнять команды, передавать данные или открывать ссылки.

Существует два типа разметки для кнопок:
1. `BubbleMarkup` — кнопки, отображаемые под сообщением
2. `KeyboardMarkup` — кнопки, отображаемые в поле ввода сообщения

## Типы разметки

### BubbleMarkup

`BubbleMarkup` — это класс для создания кнопок, которые отображаются под сообщением. Эти кнопки видны всем участникам чата и могут быть нажаты любым пользователем.

```python
from pybotx import BubbleMarkup

# Создаем разметку с кнопками
bubbles = BubbleMarkup()

# Добавляем кнопку
bubbles.add_button(
    command="/help",
    label="Справка",
    background_color="#007bff",
)

# Отправляем сообщение с кнопками
await bot.answer_message("Выберите действие:", bubbles=bubbles)
```

### KeyboardMarkup

`KeyboardMarkup` — это класс для создания кнопок, которые отображаются в поле ввода сообщения. Эти кнопки видны только пользователю, который их получил, и не видны другим участникам чата.

```python
from pybotx import KeyboardMarkup

# Создаем разметку с кнопками
keyboard = KeyboardMarkup()

# Добавляем кнопку
keyboard.add_button(
    command="/help",
    label="Справка",
    background_color="#007bff",
)

# Отправляем сообщение с кнопками в поле ввода
await bot.answer_message("Выберите действие:", keyboard=keyboard)
```

> **Note**
> 
> Классы `BubbleMarkup` и `KeyboardMarkup` имеют одинаковый интерфейс и методы. Разница только в том, где отображаются кнопки.

## BubbleMarkup

Класс `BubbleMarkup` используется для создания кнопок, отображаемых под сообщением:

```python
from pybotx import BubbleMarkup

# Создаем разметку с кнопками
bubbles = BubbleMarkup()

# Добавляем кнопки
bubbles.add_button(
    command="/action1",
    label="Действие 1",
    background_color="#007bff",
)

bubbles.add_button(
    command="/action2",
    label="Действие 2",
    background_color="#28a745",
    new_row=False,  # Кнопка будет в том же ряду
)

bubbles.add_button(
    command="/action3",
    label="Действие 3",
    background_color="#dc3545",
    new_row=True,  # Кнопка будет в новом ряду
)
```

Метод `add_button` принимает следующие параметры:
- `command` — команда, которая будет отправлена при нажатии на кнопку
- `label` — текст, отображаемый на кнопке
- `background_color` — цвет фона кнопки (в формате HEX)
- `new_row` — флаг, указывающий, нужно ли начинать новый ряд кнопок
- `data` — дополнительные данные, которые будут переданы при нажатии на кнопку
- `link` — ссылка, которая будет открыта при нажатии на кнопку (для кнопок-ссылок)
- `alert` — текст предупреждения, которое будет показано перед переходом по ссылке

## KeyboardMarkup

Класс `KeyboardMarkup` используется для создания кнопок, отображаемых в поле ввода сообщения:

```python
from pybotx import KeyboardMarkup

# Создаем разметку с кнопками
keyboard = KeyboardMarkup()

# Добавляем кнопки
keyboard.add_button(
    command="/action1",
    label="Действие 1",
    background_color="#007bff",
)

keyboard.add_button(
    command="/action2",
    label="Действие 2",
    background_color="#28a745",
    new_row=False,  # Кнопка будет в том же ряду
)

keyboard.add_button(
    command="/action3",
    label="Действие 3",
    background_color="#dc3545",
    new_row=True,  # Кнопка будет в новом ряду
)
```

Метод `add_button` для `KeyboardMarkup` принимает те же параметры, что и для `BubbleMarkup`.

## Параметры кнопок

### Команды и данные

Кнопки могут отправлять команды и дополнительные данные:

```python
bubbles = BubbleMarkup()

# Кнопка с командой
bubbles.add_button(
    command="/help",
    label="Справка",
)

# Кнопка с командой и данными
bubbles.add_button(
    command="/select",
    label="Выбрать",
    data={"item_id": 123, "action": "view"},
)
```

При нажатии на кнопку с данными, эти данные будут доступны в обработчике через `message.data`:

```python
@collector.command("/select")
async def select_handler(message: IncomingMessage, bot: Bot) -> None:
    item_id = message.data.get("item_id")
    action = message.data.get("action")
    
    await bot.answer_message(f"Выбран элемент {item_id}, действие: {action}")
```

### Кнопки-ссылки

Кнопки могут открывать ссылки:

```python
bubbles = BubbleMarkup()

# Кнопка-ссылка
bubbles.add_button(
    label="Документация",
    link="https://example.com/docs",
)

# Кнопка-ссылка с предупреждением
bubbles.add_button(
    label="Внешний сайт",
    link="https://external-site.com",
    alert="Вы переходите на внешний сайт. Продолжить?",
)
```

> **Note**
> 
> Для кнопок-ссылок параметр `command` не указывается. Вместо этого используется параметр `link`.

## Цвета кнопок

Цвет кнопки задается параметром `background_color` в формате HEX:

```python
bubbles = BubbleMarkup()

# Синяя кнопка
bubbles.add_button(
    command="/action1",
    label="Синяя",
    background_color="#007bff",
)

# Зеленая кнопка
bubbles.add_button(
    command="/action2",
    label="Зеленая",
    background_color="#28a745",
)

# Красная кнопка
bubbles.add_button(
    command="/action3",
    label="Красная",
    background_color="#dc3545",
)

# Желтая кнопка
bubbles.add_button(
    command="/action4",
    label="Желтая",
    background_color="#ffc107",
)

# Серая кнопка
bubbles.add_button(
    command="/action5",
    label="Серая",
    background_color="#6c757d",
)
```

Рекомендуемые цвета для кнопок:
- Синий (`#007bff`) — основные действия
- Зеленый (`#28a745`) — положительные действия (подтверждение, согласие)
- Красный (`#dc3545`) — отрицательные действия (отмена, удаление)
- Желтый (`#ffc107`) — предупреждения, важные действия
- Серый (`#6c757d`) — нейтральные действия

## Примеры использования

### Меню с кнопками

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, BubbleMarkup

collector = HandlerCollector()

@collector.command("/menu", description="Показать меню")
async def menu_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем разметку с кнопками
    bubbles = BubbleMarkup()
    
    # Первый ряд кнопок
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
    
    # Второй ряд кнопок
    bubbles.add_button(
        command="/settings",
        label="Настройки",
        background_color="#6c757d",
    )
    
    bubbles.add_button(
        label="Документация",
        link="https://example.com/docs",
        background_color="#17a2b8",
        new_row=False,  # Кнопка будет в том же ряду
    )
    
    await bot.answer_message(
        "Выберите действие:",
        bubbles=bubbles,
    )
```

### Кнопки подтверждения

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, BubbleMarkup

collector = HandlerCollector()

@collector.command("/confirm", description="Запросить подтверждение")
async def confirm_handler(message: IncomingMessage, bot: Bot) -> None:
    if "action" in message.data:
        # Пользователь нажал на кнопку подтверждения или отмены
        action = message.data["action"]
        
        if action == "confirm":
            await bot.answer_message("Действие подтверждено!")
        elif action == "cancel":
            await bot.answer_message("Действие отменено.")
    else:
        # Создаем кнопки подтверждения и отмены
        bubbles = BubbleMarkup()
        
        bubbles.add_button(
            command="/confirm",
            label="Подтвердить",
            data={"action": "confirm"},
            background_color="#28a745",
        )
        
        bubbles.add_button(
            command="/confirm",
            label="Отменить",
            data={"action": "cancel"},
            background_color="#dc3545",
            new_row=False,  # Кнопка будет в том же ряду
        )
        
        await bot.answer_message(
            "Вы уверены, что хотите выполнить это действие?",
            bubbles=bubbles,
        )
```

### Пагинация с кнопками

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, BubbleMarkup

collector = HandlerCollector()

# Имитация базы данных с элементами
ITEMS = [f"Элемент {i}" for i in range(1, 21)]
ITEMS_PER_PAGE = 5

@collector.command("/list", description="Показать список с пагинацией")
async def list_handler(message: IncomingMessage, bot: Bot) -> None:
    # Получаем текущую страницу из данных кнопки или устанавливаем начальную страницу
    if message.source_sync_id and "page" in message.data:
        current_page = message.data["page"]
    else:
        current_page = 1
    
    # Вычисляем общее количество страниц
    total_pages = (len(ITEMS) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    # Получаем элементы для текущей страницы
    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_items = ITEMS[start_idx:end_idx]
    
    # Формируем текст сообщения
    message_text = f"Страница {current_page} из {total_pages}:\n\n"
    for i, item in enumerate(current_items, start=start_idx + 1):
        message_text += f"{i}. {item}\n"
    
    # Создаем кнопки пагинации
    bubbles = BubbleMarkup()
    
    # Кнопка "Предыдущая страница"
    if current_page > 1:
        bubbles.add_button(
            command="/list",
            label="◀️ Назад",
            data={"page": current_page - 1},
            background_color="#6c757d",
        )
    
    # Кнопка "Следующая страница"
    if current_page < total_pages:
        bubbles.add_button(
            command="/list",
            label="Вперед ▶️",
            data={"page": current_page + 1},
            background_color="#6c757d",
            new_row=False if current_page > 1 else True,  # В том же ряду, если есть кнопка "Назад"
        )
    
    # Отправляем или редактируем сообщение
    if message.source_sync_id:
        await bot.edit_message(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
            body=message_text,
            bubbles=bubbles,
        )
    else:
        await bot.answer_message(
            message_text,
            bubbles=bubbles,
        )
```

### Клавиатура быстрых ответов

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, KeyboardMarkup

collector = HandlerCollector()

@collector.command("/quick_replies", description="Показать быстрые ответы")
async def quick_replies_handler(message: IncomingMessage, bot: Bot) -> None:
    # Создаем клавиатуру с быстрыми ответами
    keyboard = KeyboardMarkup()
    
    # Первый ряд кнопок
    keyboard.add_button(
        command="/reply",
        label="Да",
        data={"reply": "yes"},
        background_color="#28a745",
    )
    
    keyboard.add_button(
        command="/reply",
        label="Нет",
        data={"reply": "no"},
        background_color="#dc3545",
        new_row=False,  # Кнопка будет в том же ряду
    )
    
    keyboard.add_button(
        command="/reply",
        label="Может быть",
        data={"reply": "maybe"},
        background_color="#ffc107",
        new_row=False,  # Кнопка будет в том же ряду
    )
    
    # Второй ряд кнопок
    keyboard.add_button(
        command="/reply",
        label="Спасибо",
        data={"reply": "thanks"},
        background_color="#17a2b8",
    )
    
    keyboard.add_button(
        command="/reply",
        label="Извините",
        data={"reply": "sorry"},
        background_color="#6c757d",
        new_row=False,  # Кнопка будет в том же ряду
    )
    
    await bot.answer_message(
        "Выберите быстрый ответ из клавиатуры ниже:",
        keyboard=keyboard,
    )

@collector.command("/reply")
async def reply_handler(message: IncomingMessage, bot: Bot) -> None:
    # Обрабатываем быстрый ответ
    reply = message.data.get("reply", "")
    
    replies = {
        "yes": "Вы ответили: Да",
        "no": "Вы ответили: Нет",
        "maybe": "Вы ответили: Может быть",
        "thanks": "Вы ответили: Спасибо",
        "sorry": "Вы ответили: Извините",
    }
    
    await bot.answer_message(replies.get(reply, "Неизвестный ответ"))
```

## См. также

- [Отправка сообщений](sending.md)
- [Редактирование сообщений](editing.md)
- [Удаление сообщений](deleting.md)
- [Упоминания](mentions.md)
- [Вложения](attachments.md)