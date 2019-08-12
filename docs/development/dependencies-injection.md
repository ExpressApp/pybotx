`pybotx` has an dependency injection mechanism heavily inspired by [`FastAPI`](https://fastapi.tiangolo.com/tutorial/dependencies/first-steps/).

## Usage

First, create a function that will execute some logic. It can be a coroutine or a simple function.
Then write a handler for bot that will use this dependency:

```python3  hl_lines="7"
from botx import Bot, Message, Depends
...
def get_user_huid(message: Message) -> UUID:
    return message.user_huid

@bot.handler
async def handler(user_huid: UUID = Depends(get_user_huid)):
    print(f"Message from {user_huid}")
```

## Dependencies with dependencies

Each of your dependencies function can contain parameters with other dependencies. And all this will be solved at the runtime:

```python3  hl_lines="6"
from botx import Bot, Message, Depends
...
def get_user_huid(message: Message) -> UUID:
    return message.user_huid

async def get_user(user_huid: UUID = Depends(get_user_huid)) -> User:
    return await get_user_by_huid(user_huid)

@bot.handler
def handler(user: User = Depends(get_user)):
    print(f"Message from {user.username}")
...
```

## Optional dependencies for bot and message

`Bot` and `Message` objects and special case of dependencies. If you put an annotation for them into your function then 
this objects will be passed inside. It can be useful if you write something like authentication dependency:

```python3 hl_lines="3 7 9x"
from botx import Bot, Message, BotXDependecyFailure
...
def authenticate_user(message: Message, bot: Bot) -> None:
    ...
    if not user.authenticated:
        bot.answer_message("You should login first", message)
        raise BotXDependencyFailure

@bot.handler(dependecies=[authenticate_user])
async def handler():
    pass
...
```

## Background dependencies


If you define a list of callable objects in the initialization of `HandlersColletor` or in `HandlersCollector.handler`, 
then these dependencies will be processed as background dependencies. 
They will be executed before the handler and the dependencies of this handler in the following order:

 * Dependencies defined in the `HandlersCollector` init.
 * Dependencies defined in the handler decorator.