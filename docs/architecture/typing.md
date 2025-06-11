# Типизация в pybotx

В этом разделе описана система типизации в pybotx, включая аннотации типов, настройку mypy и использование Protocol'ов.


## Введение в типизацию

pybotx полностью поддерживает статическую типизацию Python с помощью аннотаций типов. Это позволяет:

- Находить ошибки на этапе разработки
- Улучшать документацию кода
- Получать подсказки в IDE
- Обеспечивать безопасность рефакторинга

Библиотека использует модуль `typing` из стандартной библиотеки Python и совместима с инструментами статического анализа, такими как mypy.

## Аннотации типов в pybotx

Все публичные API в pybotx имеют аннотации типов. Вот некоторые примеры:

```python
from uuid import UUID
from typing import List, Optional, Dict, Any

from pybotx import Bot, IncomingMessage, BubbleMarkup

# Аннотации типов в методах бота
async def answer_message(
    self,
    body: str,
    *,
    metadata: Optional[Dict[str, Any]] = None,
    bubbles: Optional[BubbleMarkup] = None,
    # ...другие параметры...
) -> UUID:
    # Реализация метода
    pass

# Аннотации типов в обработчиках
async def command_handler(message: IncomingMessage, bot: Bot) -> None:
    # Реализация обработчика
    pass
```

pybotx также предоставляет специальные типы для работы с различными сущностями:

```python
from pybotx import (
    IncomingMessage,  # Тип входящего сообщения
    OutgoingMessage,  # Тип исходящего сообщения
    BotAccount,       # Тип учетной записи бота
    ChatCreatedEvent, # Тип события создания чата
    SmartAppEvent,    # Тип события SmartApp
    # ...другие типы...
)
```

## Настройка mypy

Для проверки типов в вашем проекте с использованием pybotx, рекомендуется настроить mypy. Вот пример конфигурации mypy в файле `mypy.ini`:

```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
strict_optional = True

[mypy.plugins.pybotx.*]
disallow_untyped_defs = False
disallow_incomplete_defs = False
```

Или в `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_optional = true

[[tool.mypy.overrides]]
module = "pybotx.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

## Использование Protocol

pybotx активно использует `Protocol` из модуля `typing` для определения структурной типизации. Это позволяет создавать интерфейсы, которые не требуют наследования.

Вот пример использования `Protocol` в pybotx:

```python
from typing import Protocol, runtime_checkable
from uuid import UUID

from pybotx import IncomingMessage, Bot

@runtime_checkable
class MessageHandler(Protocol):
    """Протокол для обработчиков сообщений."""

    async def __call__(self, message: IncomingMessage, bot: Bot) -> None:
        """Обработать входящее сообщение."""
        ...

# Функция, которая принимает обработчик сообщений
async def process_message(
    message: IncomingMessage,
    bot: Bot,
    handler: MessageHandler,
) -> None:
    await handler(message, bot)

# Функция, соответствующая протоколу MessageHandler
async def my_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Получено сообщение!")

# Использование
await process_message(message, bot, my_handler)  # Типы проверяются корректно
```

Другой пример — создание собственного middleware с использованием протоколов:

```python
from typing import Protocol, TypeVar, Callable, Awaitable
from pybotx import IncomingMessage, Bot

T = TypeVar('T')

class NextHandler(Protocol):
    async def __call__(self, message: IncomingMessage, bot: Bot) -> None:
        ...

class Middleware(Protocol):
    async def __call__(
        self,
        message: IncomingMessage,
        bot: Bot,
        call_next: NextHandler,
    ) -> None:
        ...

# Реализация middleware
async def logging_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: NextHandler,
) -> None:
    print(f"Получено сообщение: {message.body}")
    await call_next(message, bot)
    print("Сообщение обработано")
```

## Типичные паттерны типизации

### Missing[T]

pybotx использует специальный тип `Missing[T]` для параметров, которые могут быть не указаны (в отличие от `None`):

```python
from pybotx import Missing, Undefined

# Параметр metadata может быть не указан (Undefined)
# или может быть словарем
async def send_message(
    self,
    *,
    body: str,
    metadata: Missing[Dict[str, Any]] = Undefined,
) -> UUID:
    if metadata is not Undefined:
        # Используем metadata
        pass
    # ...
```

### Union и Optional

Для параметров, которые могут иметь разные типы или быть `None`:

```python
from typing import Union, Optional
from pybotx import IncomingFileAttachment, OutgoingAttachment

# file может быть IncomingFileAttachment, OutgoingAttachment или None
async def answer_message(
    self,
    body: str,
    *,
    file: Optional[Union[IncomingFileAttachment, OutgoingAttachment]] = None,
) -> UUID:
    # ...
```

## Советы по типизации

1. **Используйте аннотации типов для всех функций и методов**:

   ```python
   # Хорошо
   def get_user_name(user_id: UUID) -> str:
       # ...

   # Плохо
   def get_user_name(user_id):
       # ...
   ```

2. **Используйте mypy для проверки типов**:

   ```bash
   mypy your_bot_module.py
   ```

3. **Используйте `Protocol` для определения интерфейсов**:

   ```python
   from typing import Protocol

   class UserRepository(Protocol):
       async def get_user(self, user_id: UUID) -> User:
           ...
   ```

4. **Используйте `TypeVar` для обобщенных функций**:

   ```python
   from typing import TypeVar, List

   T = TypeVar('T')

   def first_element(items: List[T]) -> T:
       return items[0]
   ```

5. **Используйте `Literal` для ограничения значений**:

   ```python
   from typing import Literal

   def set_chat_type(chat_type: Literal["group", "personal"]) -> None:
       # ...
   ```

## См. также

- [Обзор архитектуры](overview.md)
- [Жизненный цикл бота](lifecycle.md)
- [Обработчики команд](../handlers/commands.md)
- [Middleware](../handlers/middlewares.md)
- [Документация по typing](https://docs.python.org/3/library/typing.html)
- [Документация по mypy](https://mypy.readthedocs.io/)
