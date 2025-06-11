# CI/CD для pybotx

В этом разделе описаны подходы к настройке непрерывной интеграции и доставки (CI/CD) для проектов на pybotx с использованием GitHub Actions.

## Введение

Непрерывная интеграция и доставка (CI/CD) — это практика автоматизации процессов сборки, тестирования и развертывания приложений. Для проектов на pybotx CI/CD позволяет:

- Автоматически запускать тесты при каждом изменении кода
- Проверять качество кода с помощью линтеров и статического анализа
- Собирать и публиковать Docker-образы
- Автоматически обновлять документацию
- Развертывать приложение в различных окружениях

В этом разделе мы рассмотрим, как настроить CI/CD для проектов на pybotx с использованием GitHub Actions.

## GitHub Actions

[GitHub Actions](https://github.com/features/actions) — это инструмент для автоматизации рабочих процессов разработки, встроенный в GitHub. Он позволяет создавать пользовательские workflow для автоматизации различных задач, включая CI/CD.

### Основные понятия

- **Workflow** — автоматизированный процесс, который запускается при определенных событиях
- **Job** — набор шагов, которые выполняются на одном раннере
- **Step** — отдельная задача, которая может запускать команды или действия
- **Action** — повторно используемый блок кода, который можно включить в workflow

### Структура файла workflow

Файлы workflow хранятся в директории `.github/workflows/` вашего репозитория и имеют формат YAML:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install
      
      - name: Run tests
        run: poetry run pytest
```

## Настройка тестирования

Для проектов на pybotx рекомендуется настроить автоматическое тестирование при каждом изменении кода. Вот пример workflow для тестирования:

```yaml
name: Tests

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry config virtualenvs.create false
          poetry install
      
      - name: Lint with flake8
        run: |
          poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Check types with mypy
        run: |
          poetry run mypy .
      
      - name: Run tests with pytest
        run: |
          poetry run pytest --cov=./ --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### Настройка Poetry

Для проектов, использующих Poetry, рекомендуется кэшировать зависимости для ускорения сборки:

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'

- name: Cache Poetry dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pypoetry
    key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}
    restore-keys: |
      ${{ runner.os }}-poetry-

- name: Install Poetry
  run: |
    curl -sSL https://install.python-poetry.org | python3 -
    poetry config virtualenvs.create false

- name: Install dependencies
  run: poetry install
```

## Деплой документации

Для проектов на pybotx часто требуется автоматически обновлять документацию при изменении кода. Вот пример workflow для деплоя документации на GitHub Pages с использованием MkDocs:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main, master ]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mkdocs-material
          pip install mkdocstrings[python]
      
      - name: Deploy documentation
        run: mkdocs gh-deploy --force
```

### Настройка MkDocs

Для использования MkDocs с GitHub Pages необходимо настроить файл `mkdocs.yml`:

```yaml
site_name: pybotx
site_url: https://username.github.io/pybotx
repo_url: https://github.com/username/pybotx
repo_name: username/pybotx

theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.expand
    - navigation.indexes
    - content.code.annotate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          setup_commands:
            - import sys
            - sys.path.append(".")
          selection:
            docstring_style: google
          rendering:
            show_source: true

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - admonition
  - toc:
      permalink: true

nav:
  - Введение: index.md
  - Быстрый старт: quick_start.md
  - Архитектура:
    - Обзор: architecture/overview.md
    - Жизненный цикл: architecture/lifecycle.md
    - Типизация: architecture/typing.md
  # ... другие разделы
```

## Сборка и публикация Docker-образов

Для автоматической сборки и публикации Docker-образов можно использовать следующий workflow:

```yaml
name: Build and Publish Docker Image

on:
  push:
    branches: [ main, master ]
    tags: [ 'v*' ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: username/pybotx-bot
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=username/pybotx-bot:buildcache
          cache-to: type=registry,ref=username/pybotx-bot:buildcache,mode=max
```

### Настройка секретов

Для публикации Docker-образов необходимо настроить секреты в репозитории GitHub:

1. Перейдите в настройки репозитория
2. Выберите "Secrets and variables" > "Actions"
3. Добавьте секреты `DOCKERHUB_USERNAME` и `DOCKERHUB_TOKEN`

## Полный пример workflow

Вот полный пример workflow для проекта на pybotx, который включает тестирование, сборку Docker-образа и деплой документации:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, master ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache Poetry dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pypoetry
          key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}
          restore-keys: |
            ${{ runner.os }}-poetry-
      
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          poetry config virtualenvs.create false
      
      - name: Install dependencies
        run: poetry install
      
      - name: Lint with flake8
        run: |
          poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Check types with mypy
        run: |
          poetry run mypy .
      
      - name: Run tests with pytest
        run: |
          poetry run pytest --cov=./ --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
  
  build-and-push:
    needs: test
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master' || startsWith(github.ref, 'refs/tags/v'))
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: username/pybotx-bot
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=username/pybotx-bot:buildcache
          cache-to: type=registry,ref=username/pybotx-bot:buildcache,mode=max
  
  deploy-docs:
    needs: test
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mkdocs-material
          pip install mkdocstrings[python]
      
      - name: Deploy documentation
        run: mkdocs gh-deploy --force
```

### Пример workflow для автоматического релиза

Для автоматического создания релизов при публикации тегов можно использовать следующий workflow:

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry config virtualenvs.create false
          poetry install
      
      - name: Build package
        run: poetry build
      
      - name: Generate changelog
        id: changelog
        run: |
          PREVIOUS_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
          if [ -z "$PREVIOUS_TAG" ]; then
            echo "CHANGELOG<<EOF" >> $GITHUB_ENV
            git log --pretty=format:"* %s (%h)" >> $GITHUB_ENV
            echo "EOF" >> $GITHUB_ENV
          else
            echo "CHANGELOG<<EOF" >> $GITHUB_ENV
            git log --pretty=format:"* %s (%h)" $PREVIOUS_TAG..HEAD >> $GITHUB_ENV
            echo "EOF" >> $GITHUB_ENV
          fi
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body: ${{ env.CHANGELOG }}
          files: |
            dist/*.whl
            dist/*.tar.gz
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: ${{ secrets.PYPI_API_TOKEN }}
```

## Примеры для различных сценариев

### Тестирование с использованием тестовой базы данных

Если ваш проект использует базу данных, вы можете настроить тестовую базу данных в GitHub Actions:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      # ... другие шаги ...
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          poetry run pytest
```

### Деплой на сервер через SSH

Для деплоя на сервер через SSH можно использовать следующий workflow:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /path/to/project
            git pull
            docker-compose down
            docker-compose up -d --build
```

### Деплой в Kubernetes

Для деплоя в Kubernetes можно использовать следующий workflow:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'
      
      - name: Configure kubectl
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG }}" > $HOME/.kube/config
          chmod 600 $HOME/.kube/config
      
      - name: Update deployment
        run: |
          kubectl set image deployment/pybotx-bot pybotx-bot=username/pybotx-bot:latest
          kubectl rollout status deployment/pybotx-bot
```

```mermaid
graph TD
    A[Push to GitHub] --> B{Branch?}
    B -->|main/master| C[Run Tests]
    B -->|feature| D[Run Tests]
    B -->|tag v*| E[Run Tests]
    C --> F[Build Docker Image]
    C --> G[Deploy Documentation]
    E --> H[Build Docker Image]
    E --> I[Create Release]
    E --> J[Publish to PyPI]
    F --> K[Deploy to Production]
    H --> L[Tag Docker Image]
```

## См. также

- [Развертывание с Docker](docker.md)
- [Интеграция с FastAPI](../integration/fastapi.md)
- [Тестирование](../testing/unit.md)
- [Отладка и логирование](../debug/logging.md)