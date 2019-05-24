FROM python:3.7.3-slim-stretch

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /pybotx

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install --extras "sync async test"

COPY . .

RUN isort --check-only --recursive --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=88 botx tests && \
    black --check botx tests && \
    isort --recursive --force-single-line botx tests && \
    autoflake --recursive --check --remove-all-unused-imports --remove-duplicate-keys --remove-unused-variables botx tests && \
    flake8 botx && \
    mypy botx && \
    pylint --disable=no-member  --disable=missing-docstring --disable=bad-continuation --disable=too-few-public-methods --disable=too-many-arguments --disable=duplicate-code botx && \
    pytest --cov-report term-missing --cov=botx botx tests
