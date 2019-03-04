FROM python:3.7

WORKDIR /botx

COPY . .

RUN pip install poetry && \
    poetry install --no-dev && \
    poetry build && \
    pip install dist/botx-0.1.0.tar.gz
