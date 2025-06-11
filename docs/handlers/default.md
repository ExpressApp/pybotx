# Обработчик сообщений по умолчанию

В этом разделе описан обработчик сообщений по умолчанию в pybotx, его настройка и использование.

## Введение

Обработчик сообщений по умолчанию (default message handler) — это функция, которая вызывается, когда входящее сообщение не соответствует ни одной зарегистрированной команде. Это позволяет боту реагировать на любые сообщения, а не только на команды.

В pybotx обработчик сообщений по умолчанию регистрируется с помощью декоратора `@collector.default_message_handler`.

## Регистрация обработчика по умолчанию

Для регистрации обработчика сообщений по умолчанию используется декоратор `@collector.default_message_handler`:

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.default_message_handler
async def default_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(
        "Я не понимаю эту команду. Используйте /help для получения списка доступных команд."
    )
```

Обработчик по умолчанию должен быть асинхронной функцией, принимающей два параметра:
- `message: IncomingMessage` — входящее сообщение
- `bot: Bot` — экземпляр бота

## Параметры декоратора

Декоратор `@collector.default_message_handler` может принимать следующие параметры:

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `middlewares` | `Optional[Sequence[Middleware]]` | Нет | Список middleware, применяемых к обработчику |

```python
from pybotx import HandlerCollector, IncomingMessage, Bot, IncomingMessageHandlerFunc

# Пример middleware для обработчика по умолчанию
async def logging_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    print(f"Получено неизвестное сообщение: {message.body}")
    await call_next(message, bot)

collector = HandlerCollector()

@collector.default_message_handler(middlewares=[logging_middleware])
async def default_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(
        "Я не понимаю эту команду. Используйте /help для получения списка доступных команд."
    )
```

## Когда вызывается обработчик по умолчанию

Обработчик сообщений по умолчанию вызывается в следующих случаях:

1. Сообщение не начинается с символа `/` (не является командой)
2. Сообщение начинается с `/`, но такой команды нет среди зарегистрированных
3. Сообщение содержит только `/` без имени команды

> **Note**
> 
> Для каждого коллектора (`HandlerCollector`) может быть зарегистрирован только один обработчик сообщений по умолчанию. Если вы попытаетесь зарегистрировать несколько обработчиков, будет использоваться только последний зарегистрированный.

## Примеры использования

### Базовый обработчик по умолчанию

```python
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.command("/help", description="Показать справку")
async def help_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(
        "Доступные команды:\n"
        "/help - Показать справку\n"
        "/echo <текст> - Отправить обратно полученный текст"
    )

@collector.default_message_handler
async def default_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(
        f"Я не понимаю сообщение: '{message.body}'\n"
        "Используйте /help для получения списка доступных команд."
    )
```

### Обработчик с анализом текста

```python
import re
from pybotx import HandlerCollector, IncomingMessage, Bot

collector = HandlerCollector()

@collector.default_message_handler
async def smart_default_handler(message: IncomingMessage, bot: Bot) -> None:
    # Проверяем, содержит ли сообщение приветствие
    if re.search(r'\b(привет|здравствуй|хай)\b', message.body.lower()):
        await bot.answer_message(f"Привет, {message.sender.username}!")
        return
    
    # Проверяем, содержит ли сообщение вопрос
    if re.search(r'\b(что|как|где|когда|почему|зачем)\b', message.body.lower()) and '?' in message.body:
        await bot.answer_message("Извините, я не могу ответить на этот вопрос.")
        return
    
    # Проверяем, содержит ли сообщение благодарность
    if re.search(r'\b(спасибо|благодарю)\b', message.body.lower()):
        await bot.answer_message("Пожалуйста! Рад помочь.")
        return
    
    # Если ничего не подошло, отправляем стандартный ответ
    await bot.answer_message(
        "Я не понимаю это сообщение. Используйте /help для получения списка доступных команд."
    )
```

### Интеграция с сервисом обработки естественного языка

```python
from pybotx import HandlerCollector, IncomingMessage, Bot
import httpx

collector = HandlerCollector()

@collector.default_message_handler
async def nlp_handler(message: IncomingMessage, bot: Bot) -> None:
    # Если в сообщении меньше 3 символов, считаем его шумом
    if len(message.body) < 3:
        await bot.answer_message("Пожалуйста, напишите более развернутое сообщение.")
        return
    
    try:
        # Отправляем текст сообщения на NLP-сервис
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://your-nlp-service.com/api/analyze",
                json={"text": message.body},
                timeout=5.0,
            )
            
            if response.status_code == 200:
                nlp_result = response.json()
                
                # Используем результат анализа для формирования ответа
                intent = nlp_result.get("intent", "unknown")
                
                if intent == "greeting":
                    await bot.answer_message(f"Привет, {message.sender.username}!")
                elif intent == "question":
                    await bot.answer_message("Я постараюсь ответить на ваш вопрос...")
                elif intent == "farewell":
                    await bot.answer_message("До свидания! Обращайтесь еще.")
                else:
                    await bot.answer_message(
                        "Я не совсем понимаю, что вы имеете в виду. "
                        "Используйте /help для получения списка доступных команд."
                    )
            else:
                # Если сервис недоступен, отправляем стандартный ответ
                await bot.answer_message(
                    "Извините, я сейчас не могу обработать ваше сообщение. "
                    "Пожалуйста, попробуйте позже или используйте команды."
                )
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        await bot.answer_message(
            "Произошла ошибка при обработке вашего сообщения. "
            "Пожалуйста, попробуйте позже."
        )
```

## См. также

- [Обработчики команд](commands.md)
- [Обработчики событий](events.md)
- [Middleware](middlewares.md)
- [Коллекторы](collectors.md)
- [Отправка сообщений](../messages/sending.md)