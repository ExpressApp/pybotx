# Жизненный цикл бота

В этом разделе описан жизненный цикл бота в pybotx, включая процессы запуска, остановки и обработки соединений.


## Обзор жизненного цикла

Жизненный цикл бота в pybotx состоит из следующих основных этапов:

1. **Инициализация** - создание экземпляра класса `Bot`
2. **Запуск (startup)** - подготовка ресурсов и соединений
3. **Работа** - обработка входящих сообщений и событий
4. **Остановка (shutdown)** - освобождение ресурсов и закрытие соединений

```mermaid
graph LR
    A[Инициализация] --> B[Запуск]
    B --> C[Работа]
    C --> D[Остановка]
```

## Запуск бота (startup)

Метод `bot.startup()` выполняет следующие действия:

1. Инициализирует HTTP-клиенты для взаимодействия с BotX API
2. Создает пулы соединений для каждого CTS-сервера
3. Регистрирует обработчики команд и событий
4. Запускает фоновые задачи для обработки очередей сообщений

```python
from fastapi import FastAPI
from pybotx import Bot, BotAccountWithSecret
from uuid import UUID

# Создание экземпляра бота
bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            cts_url="https://cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
)

# Создание FastAPI приложения
app = FastAPI()

# Регистрация обработчика запуска
@app.on_event("startup")
async def startup_event():
    await bot.startup()
```

> **Note**
> 
> Метод `bot.startup()` должен быть вызван до начала обработки входящих сообщений.

## Остановка бота (shutdown)

Метод `bot.shutdown()` выполняет следующие действия:

1. Останавливает фоновые задачи
2. Закрывает пулы соединений
3. Освобождает ресурсы HTTP-клиентов
4. Завершает все незавершенные операции

```python
# Регистрация обработчика остановки
@app.on_event("shutdown")
async def shutdown_event():
    await bot.shutdown()
```

## Graceful shutdown

pybotx поддерживает "graceful shutdown" (плавное завершение работы), что позволяет боту корректно завершить все текущие операции перед остановкой. Это особенно важно в продакшн-окружении, где внезапная остановка может привести к потере данных или незавершенным операциям.

При вызове метода `bot.shutdown()` происходит следующее:

1. Бот перестает принимать новые сообщения
2. Все текущие обработчики сообщений продолжают работу до завершения
3. Все асинхронные задачи получают сигнал о необходимости завершения
4. Бот ожидает завершения всех задач в течение таймаута
5. После завершения всех задач (или по истечении таймаута) закрываются соединения

```python
import asyncio
import signal
from contextlib import asynccontextmanager

# Пример реализации graceful shutdown с обработкой сигналов
async def shutdown_on_signal(bot):
    loop = asyncio.get_running_loop()

    # Регистрация обработчиков сигналов
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(bot.shutdown()),
        )

    try:
        # Ожидание завершения работы бота
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        # Обработка отмены задачи
        pass

# Контекстный менеджер для автоматического запуска и остановки бота
@asynccontextmanager
async def lifespan_bot(bot):
    await bot.startup()
    try:
        yield bot
    finally:
        await bot.shutdown()

# Использование в приложении
async def main():
    async with lifespan_bot(bot):
        await shutdown_on_signal(bot)
```

## Пулы соединений

pybotx использует пулы соединений для оптимизации взаимодействия с BotX API. Пулы соединений позволяют:

1. Повторно использовать HTTP-соединения, что снижает накладные расходы на установку новых соединений
2. Ограничивать количество одновременных соединений к серверу
3. Управлять таймаутами и повторными попытками при сбоях

Пулы соединений создаются автоматически при вызове `bot.startup()` и закрываются при вызове `bot.shutdown()`.

```python
from pybotx import Bot, BotAccountWithSecret
from uuid import UUID

# Настройка бота с параметрами пула соединений
bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            cts_url="https://cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
    httpx_client_kwargs={
        "timeout": 30.0,  # Таймаут соединения в секундах
        "limits": {
            "max_connections": 100,  # Максимальное количество соединений
            "max_keepalive_connections": 20,  # Максимальное количество постоянных соединений
        },
    },
)
```

## Обработка ошибок

При возникновении ошибок во время жизненного цикла бота, pybotx предоставляет механизмы для их обработки:

1. **Обработчики исключений** - позволяют перехватывать и обрабатывать исключения, возникающие в обработчиках сообщений
2. **Логирование** - все ошибки записываются в лог для последующего анализа
3. **Повторные попытки** - при сбоях соединения с BotX API выполняются автоматические повторные попытки

```python
from pybotx import Bot, IncomingMessage

# Обработчик исключений
async def error_handler(message: IncomingMessage, bot: Bot, exc: Exception) -> None:
    print(f"Ошибка при обработке сообщения: {exc}")
    await bot.answer_message("Произошла ошибка при обработке вашего сообщения.")

# Регистрация обработчика исключений
bot = Bot(
    collectors=[collector],
    bot_accounts=[...],
    exception_handlers={Exception: error_handler},
)
```

## См. также

- [Обзор архитектуры](/architecture/overview/)
- [Типизация](/architecture/typing/)
- [Обработчики команд](/handlers/commands/)
- [Middleware](/handlers/middlewares/)
- [Отладка и логирование](/debug/logging/)
