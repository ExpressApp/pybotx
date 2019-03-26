FROM python:3.7

ENV PYTHONUNBUFFERED 1

WORKDIR /botx_sdk_python

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install

COPY . .

RUN pytest
