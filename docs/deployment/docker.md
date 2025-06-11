# Развертывание с Docker

В этом разделе описаны способы развертывания pybotx-приложений с использованием Docker, настройка Uvicorn+Gunicorn и реализация healthchecks.

## Введение

Docker — это платформа для разработки, доставки и запуска приложений в контейнерах. Использование Docker для развертывания pybotx-приложений имеет ряд преимуществ:

- **Изоляция** — приложение и его зависимости изолированы от хост-системы
- **Воспроизводимость** — одинаковое окружение в разработке и продакшн
- **Масштабируемость** — легко масштабировать приложение горизонтально
- **Портативность** — работает одинаково на любой платформе с Docker

В этом разделе мы рассмотрим, как создать Docker-образ для pybotx-приложения, настроить Uvicorn и Gunicorn для оптимальной производительности, а также реализовать healthchecks для мониторинга состояния приложения.

## Базовый Dockerfile

Вот пример базового Dockerfile для pybotx-приложения:

```dockerfile
# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Poetry
RUN pip install poetry==1.4.2

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Настраиваем Poetry для создания виртуального окружения в контейнере
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Копируем исходный код приложения
COPY . .

# Создаем непривилегированного пользователя
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Оптимизация Dockerfile

Для оптимизации размера образа и повышения безопасности рекомендуется:

1. **Использовать многоэтапную сборку**:

```dockerfile
# Этап сборки
FROM python:3.10-slim AS builder

WORKDIR /app

RUN pip install poetry==1.4.2

COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt > requirements.txt

# Этап финального образа
FROM python:3.10-slim

WORKDIR /app

# Устанавливаем зависимости
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем непривилегированного пользователя
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Добавить .dockerignore файл**:

```
# .dockerignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.git
.gitignore
.env
.venv
venv/
ENV/
.idea/
.vscode/
*.swp
*.swo
.DS_Store
```

## Настройка Uvicorn и Gunicorn

Для продакшн-окружения рекомендуется использовать комбинацию Uvicorn и Gunicorn. Gunicorn выступает в роли менеджера процессов, а Uvicorn — в роли ASGI-сервера.

### Установка зависимостей

Добавьте необходимые зависимости в `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.9"
pybotx = "^0.75.1"
fastapi = "^0.95.0"
uvicorn = {extras = ["standard"], version = "^0.21.1"}
gunicorn = "^20.1.0"
```

### Создание скрипта запуска

Создайте файл `gunicorn_conf.py` для настройки Gunicorn:

```python
# gunicorn_conf.py
import multiprocessing
import os

# Количество воркеров
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
max_workers_str = os.getenv("MAX_WORKERS")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)

workers_per_core = float(workers_per_core_str)
max_workers = int(max_workers_str) if max_workers_str else None

if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    cores = multiprocessing.cpu_count()
    web_concurrency = max(int(cores * workers_per_core), 2)
    if max_workers:
        web_concurrency = min(web_concurrency, max_workers)

# Настройки Gunicorn
bind = os.getenv("BIND", "0.0.0.0:8000")
workers = web_concurrency
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
timeout = 120
graceful_timeout = 30
accesslog = "-"  # Логирование в stdout
errorlog = "-"   # Логирование ошибок в stdout
```

Затем создайте скрипт запуска `start.sh`:

```bash
#!/bin/bash
# start.sh

# Запуск Gunicorn с настройками из gunicorn_conf.py
exec gunicorn app.main:app -c gunicorn_conf.py
```

Обновите Dockerfile:

```dockerfile
# ...

# Копируем конфигурационные файлы
COPY gunicorn_conf.py start.sh ./
RUN chmod +x start.sh

# ...

# Запускаем приложение через скрипт
CMD ["./start.sh"]
```

## Healthchecks

Healthchecks позволяют Docker и оркестраторам контейнеров (например, Kubernetes) проверять работоспособность приложения. Для pybotx-приложения рекомендуется реализовать два типа проверок:

1. **Liveness probe** — проверяет, что приложение запущено и отвечает на запросы
2. **Readiness probe** — проверяет, что приложение готово обрабатывать запросы (например, подключено к базе данных)

### Реализация эндпоинтов для healthchecks

Добавьте эндпоинты для проверки работоспособности в ваше FastAPI-приложение:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pybotx import Bot

app = FastAPI()

# ... настройка бота ...

@app.get("/health/live")
async def liveness_check():
    """
    Проверка, что приложение запущено и отвечает на запросы.
    """
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness_check(bot: Bot = Depends(get_bot)):
    """
    Проверка, что приложение готово обрабатывать запросы.
    Проверяет подключение к BotX API.
    """
    try:
        # Проверяем подключение к BotX API
        # Например, запрашиваем статус бота
        await bot.raw_get_status({})
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}",
        )
```

### Настройка Docker healthcheck

Добавьте инструкцию HEALTHCHECK в Dockerfile:

```dockerfile
# ...

# Настройка healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# ...
```

## Docker Compose

Для локальной разработки и простого развертывания можно использовать Docker Compose. Вот пример `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bot:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - BOT_ID=123e4567-e89b-12d3-a456-426655440000
      - CTS_URL=https://cts.example.com
      - SECRET_KEY=e29b417773f2feab9dac143ee3da20c5
      - LOG_LEVEL=INFO
      - WORKERS_PER_CORE=1
      - MAX_WORKERS=4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

## Примеры конфигураций

### Пример для продакшн-окружения

Вот полный пример конфигурации для продакшн-окружения:

#### Dockerfile

```dockerfile
# Этап сборки
FROM python:3.10-slim AS builder

WORKDIR /app

RUN pip install poetry==1.4.2

COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt > requirements.txt

# Этап финального образа
FROM python:3.10-slim

WORKDIR /app

# Устанавливаем зависимости и необходимые пакеты
COPY --from=builder /app/requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Копируем исходный код и конфигурационные файлы
COPY . .
COPY gunicorn_conf.py start.sh ./
RUN chmod +x start.sh

# Создаем директорию для логов
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Создаем непривилегированного пользователя
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Настройка healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Запускаем приложение
CMD ["./start.sh"]
```

#### gunicorn_conf.py

```python
import multiprocessing
import os

# Количество воркеров
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
max_workers_str = os.getenv("MAX_WORKERS")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)

workers_per_core = float(workers_per_core_str)
max_workers = int(max_workers_str) if max_workers_str else None

if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    cores = multiprocessing.cpu_count()
    web_concurrency = max(int(cores * workers_per_core), 2)
    if max_workers:
        web_concurrency = min(web_concurrency, max_workers)

# Настройки Gunicorn
bind = os.getenv("BIND", "0.0.0.0:8000")
workers = web_concurrency
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
timeout = 120
graceful_timeout = 30

# Логирование
accesslog = os.getenv("ACCESS_LOG", "-")
errorlog = os.getenv("ERROR_LOG", "-")
loglevel = os.getenv("LOG_LEVEL", "info")

# Настройки для работы за прокси
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
proxy_allow_ips = os.getenv("PROXY_ALLOW_IPS", "*")
```

#### start.sh

```bash
#!/bin/bash

# Запуск миграций или других подготовительных операций
# ...

# Запуск Gunicorn с настройками из gunicorn_conf.py
exec gunicorn app.main:app -c gunicorn_conf.py
```

#### app/main.py

```python
import os
import logging
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pybotx import (
    Bot, BotAccountWithSecret, HandlerCollector,
    IncomingMessage, build_command_accepted_response,
)

# Настройка логирования
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Создаем коллектор обработчиков
collector = HandlerCollector()

# Регистрируем обработчик команды
@collector.command("/hello", description="Поприветствовать пользователя")
async def hello_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(f"Привет, {message.sender.username}!")

# Создаем экземпляр бота
bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            id=UUID(os.getenv("BOT_ID", "123e4567-e89b-12d3-a456-426655440000")),
            cts_url=os.getenv("CTS_URL", "https://cts.example.com"),
            secret_key=os.getenv("SECRET_KEY", "e29b417773f2feab9dac143ee3da20c5"),
        ),
    ],
)

# Создаем экземпляр FastAPI
app = FastAPI()

# Добавляем обработчики событий для запуска и остановки бота
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://express.ms"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Bot-Key"],
)

# Эндпоинт для обработки команд
@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    try:
        request_body = await request.json()
        logger.debug(f"Received command: {request_body}")
        
        bot.async_execute_raw_bot_command(
            request_body,
            request_headers=request.headers,
        )
        
        return JSONResponse(
            build_command_accepted_response(),
            status_code=202,
        )
    except Exception as e:
        logger.exception(f"Error processing command: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500,
        )

# Эндпоинт для получения статуса бота
@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    try:
        status = await bot.raw_get_status(
            dict(request.query_params),
            request_headers=request.headers,
        )
        return JSONResponse(status)
    except Exception as e:
        logger.exception(f"Error getting status: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500,
        )

# Эндпоинт для обработки коллбэков
@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    try:
        request_body = await request.json()
        logger.debug(f"Received callback: {request_body}")
        
        await bot.set_raw_botx_method_result(
            request_body,
            verify_request=False,
        )
        
        return JSONResponse(
            build_command_accepted_response(),
            status_code=202,
        )
    except Exception as e:
        logger.exception(f"Error processing callback: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500,
        )

# Эндпоинты для healthchecks
@app.get("/health/live")
async def liveness_check():
    """
    Проверка, что приложение запущено и отвечает на запросы.
    """
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness_check():
    """
    Проверка, что приложение готово обрабатывать запросы.
    Проверяет подключение к BotX API.
    """
    try:
        # Проверяем, что бот запущен
        if not bot.is_running:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Bot is not running",
            )
        
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}",
        )
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - BOT_ID=${BOT_ID}
      - CTS_URL=${CTS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - LOG_LEVEL=INFO
      - WORKERS_PER_CORE=1
      - MAX_WORKERS=4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

### Пример для Kubernetes

Если вы используете Kubernetes для оркестрации контейнеров, вот пример манифеста для развертывания pybotx-приложения:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pybotx-bot
  labels:
    app: pybotx-bot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pybotx-bot
  template:
    metadata:
      labels:
        app: pybotx-bot
    spec:
      containers:
      - name: pybotx-bot
        image: your-registry/pybotx-bot:latest
        ports:
        - containerPort: 8000
        env:
        - name: BOT_ID
          valueFrom:
            secretKeyRef:
              name: pybotx-secrets
              key: bot-id
        - name: CTS_URL
          valueFrom:
            configMapKeyRef:
              name: pybotx-config
              key: cts-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: pybotx-secrets
              key: secret-key
        - name: LOG_LEVEL
          value: "INFO"
        - name: WORKERS_PER_CORE
          value: "1"
        - name: MAX_WORKERS
          value: "4"
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "500m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: pybotx-bot
spec:
  selector:
    app: pybotx-bot
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pybotx-bot
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: bot.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pybotx-bot
            port:
              number: 80
  tls:
  - hosts:
    - bot.example.com
    secretName: bot-tls-secret
```

## См. также

- [CI/CD для pybotx](ci_cd.md)
- [Интеграция с FastAPI](../integration/fastapi.md)
- [Жизненный цикл бота](../architecture/lifecycle.md)
- [Отладка и логирование](../debug/logging.md)