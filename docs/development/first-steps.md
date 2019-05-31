Let's create a new bot, which will ask the user for his data, and then send some statistics from the collected information. 
Take echo-bot, from the [Introduction](/), and gradually improve it step by step.

## Starting point

Right now we have the following code:

```Python3
from botx import Bot, Message, Status
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_202_ACCEPTED

bot = Bot(disable_credentials=True)


@bot.default_handler
def echo_handler(message: Message, bot: Bot):
    bot.answer_message(message.body, message)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status", response_model=Status, status_code=HTTP_202_ACCEPTED)
def bot_status():
    return bot.status


@app.post("/command")
def bot_command(message: Message):
    bot.execute_command(message.dict())
```

## First, let's see how this code works
<small>We will explain only those parts that relate to `pybotx`, and not to the frameworks used in this documentation.</small>

### Step 1: import `Bot`, `Message` and `Status` classes

```Python3 hl_lines="1"
from botx import Bot, Message, Status
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_202_ACCEPTED
...
```

* `Bot` is a Python class that provides all the functions to your bots.

* `Message` is a class that provides data to your handlers for commands.

* `Status` is a class that is used here only to document the `FastAPI` route.

### Step 2: initialize your `Bot`

```Python3 hl_lines="2"
...
bot = Bot(disable_credentials=True)
...
```

The `bot` variable will be an "instance" of the class `Bot`.
We also disable obtaining tokens for cts servers for simplifying.

### Step 3: define default handler

```Python3 hl_lines="2 3"
...
@bot.default_handler
def echo_handler(message: Message, bot: Bot):
    bot.answer_message(message.body, message)
...
```

This handler will be called for all commands that have not appropriate handlers.

### Step 4: send text to user

```Python3 hl_lines="4"
...
@bot.default_handler
def echo_handler(message: Message, bot: Bot):
    bot.answer_message(message.body, message)
...
```

`Bot.answer_message` will send some text to the user by using sync_id, bot_id and host data from the `Message` instance.
This is a simple wrapper for the `Bot.send_message` method, which is used to gain more control over sending messages process, 
allowing you to specify a different host, bot_id, sync_id, group_chat_id or a list of them.

### Step 5: register lifespan events for bot proper initialization

```Python3 hl_lines="2 3"
...
app.add_event_handler("startup", bot.start)
app.add_event_handler("shutdown", bot.stop)
...
```

The `Bot.start` and `Bot.stop` methods are used to initialize some data that cannot be initialized when creating a `Bot` instance.
You must call them to be sure that the bot will work properly. 

### Step 6: define webhooks for bot

```Python3 hl_lines="4 9"
...
@app.get("/status", response_model=Status, status_code=HTTP_202_ACCEPTED)
def bot_status():
    return bot.status


@app.post("/command")
def bot_command(message: Message):
    bot.execute_command(message.dict())
...
```

Here we define to `FastAPI` routes:

 * `GET` on `/status` will tell BotX API which commands are available for your bot.
 * `POST` on `/command` will receive data for incoming messages for your bot and execute handlers for commands.

!!! warning

    If `Bot.execute_command` did not find a handler for the command in the message, it will raise an `BotXException`, 
    which you probably want to handle. You can register default handler to process all commands that do not have their own handler.

## Define new handlers

Let's define a new handler that will trigger a chain of questions for the user to collect information. 

We'll use the `/fill-info` command to start the chain:

```Python3 
...
users_data = {}

bot = Bot(disable_credentials)

@bot.handler
def fill_info(message: Message, bot: Bot):
    if message.user_huid not in users_data:
        text = (
            "Hi! I'm a bot that will ask some questions about you.\n"
            "First of all: what is your name?"
        )
        bot.answer_message(text, message)
    else:
        text = (
            "You've already filled out infomation about yourself.\n"
            "You can view it by typing `/my-info` command.\n"
            "You can also view the processed information by typing `/info` command."
        )
        bot.answer_message(text, message)
...
```

Here is nothing new for now. Everything was explained in previous sections. 

Now let's define another 2 handlers for the commands that were mentioned in the message text that we send to the user: 

 * `/my-info` will just send the information that users have filled out about themselves.
 * `/info` will send back the number of users who filled in information about themselves, their average age and number of male and female users.
 * `/infomation` is an alias to `/info` command.
 
```Python3 hl_lines="2 19"
...
@bot.handler(command='my-info')
def get_info_for_user(message: Message, bot: Bot):
    if message.user_huid not in users_data:
        text = (
            "I have no infomation about you :(\n"
            "Type `/fill-info` so I can collect it, please."
        )
        bot.answer_message(text, message)
    else:
        text = (
            f"Your name: {users_data[message.user_huid]['name']}\n"
            f"Your age: {users_data[message.user_huid]['age']}\n"
            f"Your gender: {users_data[message.user_huid]['gender']}\n"
            "This is all that I have now."
        )
        bot.answer_message(text, message)
        
@bot.handler(commands=['info', '/infomation'])
def get_processed_infomation(message: Message, bot: Bot):
    users_count = len(users_data)
    average_age = sum(user['age'] for user in users_data) / users_count
    gender_array = [1 if user['gender'] == 'male' else 2 for user in users_data]
    text = (
        f"Count of users: {users_count}\n"
        f"Average age: {average_age}\n"
        f"Male users count: {gender_array.count(1)}\n"    
        f"Female users count: {gender_array.count(2)}"    
    )
    
    bot.answer_message(text, message)
...
```

Take a look at highlighted lines. `Bot.handler` method takes a different number of arguments. 
The most commonly used arguments are `command` and `commands`. 
`command` is a single string that defines a command for a handler. 
`commands` is a list of strings that can be used to define a variety of aliases for a handler. 
You can use them together. In this case, they simply merge into one array as if you specified only `commands` argument.

See also at how the commands themselves are declared:

 * for the `fill_info` function we have not defined any `command` but it will be implicitly converted to the `fill-info` command.
 * for the `get_info_for_user` function we had explicitly specified `my-info` string, but it will be converted to `/my-info` inside the `Bot.handler` decorator.
 * for the `get_processed_information` we specified a `commands` argument to define many aliases for the handler. All commands strings will also be converted to have only one leading slash.
 
## Register next step handlers

`pybotx` provide you the ability to change mechanism of handlers processing.
To use it, you must define a function that accepts 2 required positional arguments, as in usual handlers for commands: 
first for the message and then for the bot. 
You can also add additional positional and key arguments to the handler that will be passed when it is called.

Lets' define these handlers and, finally, create a chain of questions from the bot to the user:

```Python3 hl_lines="10"
...
@bot.handler
def fill_info(message: Message, bot: Bot):
    if message.user_huid not in users_data:
        text = (
            "Hi! I'm a bot that will ask some questions about you.\n"
            "First of all: what is your name?"
        )
        bot.answer_message(text, message)
        bot.register_next_step_handler(message, get_name)
    else:
        text = (
            "You've already filled out infomation about yourself.\n"
            "You can view it by typing `/my-info` command.\n"
            "You can also view the processed information by typing `/info` command."
        )
        bot.answer_message(text, message)
...
def get_name(message: Message, bot: Bot):
    users_data[message.user_huid]["name"] = message.body
    bot.answer_message("Good! Move next: how old are you?", message)
    bot.register_next_step_handler(message, get_age)


def get_age(message: Message, bot: Bot):
    try:
        age = int(message.body)
        if age <= 5:
            bot.answer_message(
                "Sorry, but it's not true. Say your real age, please!", message
            )
        else:
            users_data[message.user_huid]["age"] = age
            bot.answer_message("Got it! Final question: your gender?", message)
            bot.register_next_step_handler(message, get_gender)
    except ValueError:
        bot.answer_message("No, no, no. Pleas tell me your age in numbers!", message)
        bot.register_next_step_handler(message, get_age)


def get_gender(message: Message, bot: Bot):
    gender = message.body
    if gender in ["male", "female"]:
        users_data[message.user_huid]["gender"] = gender
        bot.answer_message("Ok! Thanks for taking the time to answer my questions.", message)
    else:
        bot.answer_message(
            "Sorry, but I can not recognize your answer! Type 'male' or 'female', please!",
            message,
        )
        bot.register_next_step_handler(message, get_gender)
...
```

What's going on here? We added one line to our `/fill-info` command to start a chain of questions for our user.
We also defined 3 functions, whose signature is similar to the usual handler signature, but instead of registration them using the `Bot.handler` decorator, 
we do this using the `Bot.register_next_step_handler` method, 
passing it our message as the first argument and the handler that will be executed for the next user message as the second.
We also can pass positional and key arguments if we need them, but this not our case now.

## Complete example

That is all! Here is full listing:

```Python3
from botx import Bot, Message, Status
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_202_ACCEPTED

users_data = {}

bot = Bot(disable_credentials=True)


@bot.default_handler
def echo_handler(message: Message, bot: Bot):
    bot.answer_message(message.body, message)


@bot.handler
def fill_info(message: Message, bot: Bot):
    if message.user_huid not in users_data:
        users_data[message.user_huid] = {}
        text = (
            "Hi! I'm a bot that will ask some questions about you.\n"
            "First of all: what is your name?"
        )
        bot.answer_message(text, message)
        bot.register_next_step_handler(message, get_name)
    else:
        text = (
            "You've already filled out infomation about yourself.\n"
            "You can view it by typing `/my-info` command.\n"
            "You can also view the processed information by typing `/info` command."
        )
        bot.answer_message(text, message)


@bot.handler(command='my-info')
def get_info_for_user(message: Message, bot: Bot):
    if message.user_huid not in users_data:
        text = (
            "I have no infomation about you :(\n"
            "Type `/fill-info` so I can collect it, please."
        )
        bot.answer_message(text, message)
    else:
        text = (
            f"Your name: {users_data[message.user_huid]['name']}\n"
            f"Your age: {users_data[message.user_huid]['age']}\n"
            f"Your gender: {users_data[message.user_huid]['gender']}\n"
            "This is all that I have now."
        )
        bot.answer_message(text, message)
        
        
@bot.handler(commands=['info', '/infomation'])
def get_processed_infomation(message: Message, bot: Bot):
    users_count = len(users_data)
    average_age = sum(user['age'] for user in users_data.values()) / users_count
    gender_array = [1 if user['gender'] == 'male' else 2 for user in users_data.values()]
    text = (
        f"Count of users: {users_count}\n"
        f"Average age: {average_age}\n"
        f"Male users count: {gender_array.count(1)}\n"    
        f"Female users count: {gender_array.count(2)}"    
    )
    
    bot.answer_message(text, message)
    

def get_name(message: Message, bot: Bot):
    users_data[message.user_huid]["name"] = message.body
    bot.answer_message("Good! Move next: how old are you?", message)
    bot.register_next_step_handler(message, get_age)


def get_age(message: Message, bot: Bot):
    try:
        age = int(message.body)
        if age <= 5:
            bot.answer_message(
                "Sorry, but it's not true. Say your real age, please!", message
            )
        else:
            users_data[message.user_huid]["age"] = age
            bot.answer_message("Got it! Final question: your gender?", message)
            bot.register_next_step_handler(message, get_gender)
    except ValueError:
        bot.answer_message("No, no, no. Pleas tell me your age in numbers!", message)
        bot.register_next_step_handler(message, get_age)


def get_gender(message: Message, bot: Bot):
    gender = message.body
    if gender in ["male", "female"]:
        users_data[message.user_huid]["gender"] = gender
        bot.answer_message("Ok! Thanks for taking the time to answer my questions.", message)
    else:
        bot.answer_message(
            "Sorry, but I can not recognize your answer! Type 'male' or 'female', please!",
            message,
        )
        bot.register_next_step_handler(message, get_gender)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status", response_model=Status, status_code=HTTP_202_ACCEPTED)
def bot_status():
    return bot.status


@app.post("/command")
def bot_command(message: Message):
    bot.execute_command(message.dict())
```