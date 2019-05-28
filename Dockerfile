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

RUN pytest --cov-report term-missing --cov=botx botx tests
