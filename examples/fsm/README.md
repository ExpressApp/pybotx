## General

A bot that defines middleware that process request in finite-state machine way.

State is an enum (`enum.Enum`) with several values that are changed using 
`bot.middleware.change_state` function.

This example shows definition of custom middleware and handlers processing logic.

## Run

start `uvicorn` ASGI server with bot on 8000 port with following command:
```bash
$ uvicorn bot.web:app
``` 