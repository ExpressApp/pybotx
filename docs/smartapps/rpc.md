# RPC в SmartApp

В этом разделе описаны способы использования RPC (Remote Procedure Call) в SmartApp с помощью pybotx-smartapp-rpc.

## Введение

RPC (Remote Procedure Call) — это механизм, позволяющий клиентской части SmartApp вызывать методы на серверной стороне. Это упрощает взаимодействие между клиентом и сервером, делая его более структурированным и типизированным.

Библиотека `pybotx-smartapp-rpc` предоставляет удобный способ декларирования и использования RPC-методов в SmartApp, а также отправки push-уведомлений клиенту.

## Установка pybotx-smartapp-rpc

Для использования RPC в SmartApp необходимо установить библиотеку `pybotx-smartapp-rpc`:

```bash
poetry add pybotx-smartapp-rpc
```

или

```bash
pip install pybotx-smartapp-rpc
```

## Декларирование RPC-методов

RPC-методы декларируются с помощью декоратора `@rpc_method`. Каждый метод должен быть асинхронным и принимать параметры, соответствующие ожидаемым данным от клиента.

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent
from pybotx_smartapp_rpc import RPCRouter, rpc_method

# Создаем RPC-роутер
rpc_router = RPCRouter()

# Декларируем RPC-метод
@rpc_router.method("get_user_data")
async def get_user_data(bot: Bot, event: SmartAppEvent, user_id: str) -> dict:
    """Получение данных пользователя."""
    # Логика получения данных пользователя
    user_data = {
        "id": user_id,
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "role": "user",
    }
    return user_data

# Декларируем RPC-метод с несколькими параметрами
@rpc_router.method("update_user_data")
async def update_user_data(
    bot: Bot, 
    event: SmartAppEvent, 
    user_id: str, 
    name: str, 
    email: str = None
) -> dict:
    """Обновление данных пользователя."""
    # Логика обновления данных пользователя
    updated_user = {
        "id": user_id,
        "name": name,
        "email": email,
        "updated_at": "2023-01-01T12:00:00Z",
    }
    return updated_user
```

### Типизация параметров и возвращаемых значений

Для улучшения типизации и документации можно использовать Pydantic-модели:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserData(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    role: str = "user"

class UpdateUserRequest(BaseModel):
    user_id: str
    name: str
    email: Optional[str] = None

class UpdateUserResponse(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

@rpc_router.method("update_user_data")
async def update_user_data(
    bot: Bot, 
    event: SmartAppEvent, 
    request: UpdateUserRequest
) -> UpdateUserResponse:
    """Обновление данных пользователя с использованием Pydantic-моделей."""
    # Логика обновления данных пользователя
    return UpdateUserResponse(
        id=request.user_id,
        name=request.name,
        email=request.email,
    )
```

## Вызов RPC-методов из клиента

Для вызова RPC-методов из клиентской части SmartApp необходимо использовать специальный клиент, который отправляет запросы на сервер.

### JavaScript-клиент

```javascript
// Создаем RPC-клиент
const rpcClient = new SmartAppRPCClient();

// Вызываем RPC-метод
async function getUserData(userId) {
  try {
    const userData = await rpcClient.call('get_user_data', userId);
    console.log('Получены данные пользователя:', userData);
    return userData;
  } catch (error) {
    console.error('Ошибка при получении данных пользователя:', error);
    throw error;
  }
}

// Вызываем RPC-метод с несколькими параметрами
async function updateUserData(userId, name, email) {
  try {
    const updatedUser = await rpcClient.call('update_user_data', {
      user_id: userId,
      name: name,
      email: email
    });
    console.log('Пользователь обновлен:', updatedUser);
    return updatedUser;
  } catch (error) {
    console.error('Ошибка при обновлении пользователя:', error);
    throw error;
  }
}
```

## Отправка push-уведомлений

Push-уведомления позволяют серверу инициировать взаимодействие с клиентом. Это может быть полезно для уведомления пользователя о важных событиях или обновлениях данных.

### Отправка push-уведомления

```python
from pybotx_smartapp_rpc import send_push

@rpc_router.method("start_long_operation")
async def start_long_operation(bot: Bot, event: SmartAppEvent, operation_params: dict) -> dict:
    """Запуск длительной операции с отправкой push-уведомлений о прогрессе."""
    # Запускаем операцию
    operation_id = "op-" + str(uuid.uuid4())
    
    # Отправляем начальное уведомление
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="operation_progress",
        params={
            "operation_id": operation_id,
            "progress": 0,
            "status": "started",
        },
    )
    
    # Запускаем фоновую задачу для выполнения операции
    asyncio.create_task(
        process_long_operation(bot, event, operation_id, operation_params)
    )
    
    return {"operation_id": operation_id}

async def process_long_operation(
    bot: Bot, 
    event: SmartAppEvent, 
    operation_id: str, 
    params: dict
):
    """Фоновая задача для выполнения длительной операции."""
    try:
        # Имитация длительной операции с отправкой уведомлений о прогрессе
        for progress in range(10, 101, 10):
            # Выполняем часть операции
            await asyncio.sleep(1)  # Имитация работы
            
            # Отправляем уведомление о прогрессе
            await send_push(
                bot=bot,
                smartapp_event=event,
                method="operation_progress",
                params={
                    "operation_id": operation_id,
                    "progress": progress,
                    "status": "in_progress" if progress < 100 else "completed",
                },
            )
    except Exception as e:
        # В случае ошибки отправляем уведомление об ошибке
        await send_push(
            bot=bot,
            smartapp_event=event,
            method="operation_progress",
            params={
                "operation_id": operation_id,
                "status": "error",
                "error": str(e),
            },
        )
```

### Обработка push-уведомлений на клиенте

```javascript
// Регистрируем обработчик push-уведомлений
rpcClient.onPush('operation_progress', (data) => {
  const { operation_id, progress, status, error } = data;
  
  console.log(`Операция ${operation_id}: ${progress}% (${status})`);
  
  if (status === 'in_progress') {
    // Обновляем индикатор прогресса
    updateProgressBar(progress);
  } else if (status === 'completed') {
    // Операция завершена успешно
    showSuccessMessage(`Операция ${operation_id} успешно завершена!`);
  } else if (status === 'error') {
    // Произошла ошибка
    showErrorMessage(`Ошибка при выполнении операции: ${error}`);
  }
});
```

## Примеры использования

### Пример 1: Простой калькулятор

```python
from pybotx import Bot, HandlerCollector, SmartAppEvent
from pybotx_smartapp_rpc import RPCRouter, rpc_method
from pydantic import BaseModel
from typing import Literal, Union

# Создаем RPC-роутер
rpc_router = RPCRouter()

# Определяем модели данных
class CalculationRequest(BaseModel):
    operation: Literal["add", "subtract", "multiply", "divide"]
    a: float
    b: float

class CalculationResponse(BaseModel):
    result: float
    operation: str
    a: float
    b: float

# Декларируем RPC-метод
@rpc_router.method("calculate")
async def calculate(
    bot: Bot, 
    event: SmartAppEvent, 
    request: CalculationRequest
) -> CalculationResponse:
    """Выполнение математической операции."""
    a, b = request.a, request.b
    
    if request.operation == "add":
        result = a + b
        operation = "сложение"
    elif request.operation == "subtract":
        result = a - b
        operation = "вычитание"
    elif request.operation == "multiply":
        result = a * b
        operation = "умножение"
    elif request.operation == "divide":
        if b == 0:
            raise ValueError("Деление на ноль невозможно")
        result = a / b
        operation = "деление"
    else:
        raise ValueError(f"Неизвестная операция: {request.operation}")
    
    return CalculationResponse(
        result=result,
        operation=operation,
        a=a,
        b=b,
    )

# Регистрируем RPC-роутер в обработчике синхронных событий
collector = HandlerCollector()

@collector.sync_smartapp_event
async def handle_sync_smartapp_event(event: SmartAppEvent, bot: Bot):
    # Обрабатываем RPC-запросы
    return await rpc_router.handle(bot, event)
```

### Пример 2: Управление задачами с push-уведомлениями

```python
import uuid
import asyncio
from datetime import datetime
from pybotx import Bot, HandlerCollector, SmartAppEvent
from pybotx_smartapp_rpc import RPCRouter, send_push
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Создаем RPC-роутер
rpc_router = RPCRouter()

# Хранилище задач (в реальном приложении использовалась бы база данных)
tasks_storage: Dict[str, Dict[str, Any]] = {}

# Определяем модели данных
class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None

class UpdateTaskRequest(BaseModel):
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Декларируем RPC-методы
@rpc_router.method("get_tasks")
async def get_tasks(bot: Bot, event: SmartAppEvent) -> List[Task]:
    """Получение списка задач."""
    return list(tasks_storage.values())

@rpc_router.method("create_task")
async def create_task(
    bot: Bot, 
    event: SmartAppEvent, 
    request: CreateTaskRequest
) -> Task:
    """Создание новой задачи."""
    task = Task(
        title=request.title,
        description=request.description,
    )
    
    # Сохраняем задачу
    tasks_storage[task.id] = task
    
    # Отправляем push-уведомление всем клиентам о новой задаче
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="task_created",
        params=task.dict(),
    )
    
    return task

@rpc_router.method("update_task")
async def update_task(
    bot: Bot, 
    event: SmartAppEvent, 
    request: UpdateTaskRequest
) -> Task:
    """Обновление существующей задачи."""
    # Проверяем существование задачи
    if request.task_id not in tasks_storage:
        raise ValueError(f"Задача с ID {request.task_id} не найдена")
    
    # Получаем текущую задачу
    task = tasks_storage[request.task_id]
    
    # Обновляем поля
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.status is not None:
        task.status = request.status
    
    # Обновляем время изменения
    task.updated_at = datetime.now()
    
    # Сохраняем обновленную задачу
    tasks_storage[task.id] = task
    
    # Отправляем push-уведомление всем клиентам об обновлении задачи
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="task_updated",
        params=task.dict(),
    )
    
    return task

@rpc_router.method("delete_task")
async def delete_task(
    bot: Bot, 
    event: SmartAppEvent, 
    task_id: str
) -> dict:
    """Удаление задачи."""
    # Проверяем существование задачи
    if task_id not in tasks_storage:
        raise ValueError(f"Задача с ID {task_id} не найдена")
    
    # Удаляем задачу
    deleted_task = tasks_storage.pop(task_id)
    
    # Отправляем push-уведомление всем клиентам об удалении задачи
    await send_push(
        bot=bot,
        smartapp_event=event,
        method="task_deleted",
        params={"task_id": task_id},
    )
    
    return {"success": True, "task_id": task_id}

# Регистрируем RPC-роутер в обработчике синхронных событий
collector = HandlerCollector()

@collector.sync_smartapp_event
async def handle_sync_smartapp_event(event: SmartAppEvent, bot: Bot):
    # Обрабатываем RPC-запросы
    return await rpc_router.handle(bot, event)
```

### Пример 3: Интеграция с FastAPI

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from http import HTTPStatus
from pybotx import Bot, HandlerCollector, build_command_accepted_response
from pybotx_smartapp_rpc import RPCRouter

# Создаем RPC-роутер
rpc_router = RPCRouter()

# Декларируем RPC-методы
@rpc_router.method("hello")
async def hello(bot: Bot, event: SmartAppEvent, name: str) -> dict:
    """Простой метод для приветствия."""
    return {"message": f"Привет, {name}!"}

# Создаем коллектор обработчиков
collector = HandlerCollector()

# Регистрируем обработчик синхронных событий
@collector.sync_smartapp_event
async def handle_sync_smartapp_event(event: SmartAppEvent, bot: Bot):
    # Обрабатываем RPC-запросы
    return await rpc_router.handle(bot, event)

# Создаем бота
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

# Создаем FastAPI-приложение
app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)

# Эндпоинт для обработки команд (асинхронные события)
@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )

# Эндпоинт для обработки синхронных SmartApp-событий (включая RPC-запросы)
@app.post("/smartapps/request")
async def sync_smartapp_event_handler(request: Request) -> JSONResponse:
    response = await bot.sync_execute_raw_smartapp_event(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(response.jsonable_dict(), status_code=HTTPStatus.OK)

# Эндпоинт для получения статуса бота
@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(
        dict(request.query_params),
        request_headers=request.headers,
    )
    return JSONResponse(status)

# Эндпоинт для обработки коллбэков
@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    await bot.set_raw_botx_method_result(
        await request.json(),
        verify_request=False,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )
```

## См. также

- [Обзор SmartApp](overview.md)
- [Push-уведомления](push.md)
- [UI-компоненты](ui.md)
- [Интеграция с FastAPI](../integration/fastapi.md)
- [Обработка событий](../handlers/events.md)