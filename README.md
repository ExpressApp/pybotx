# pybotx

*Библиотека для создания чат-ботов и SmartApps для мессенджера eXpress*

[![PyPI version](https://badge.fury.io/py/pybotx.svg)](https://badge.fury.io/py/pybotx)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pybotx)
[![Coverage](https://codecov.io/gh/ExpressApp/pybotx/branch/master/graph/badge.svg)](https://codecov.io/gh/ExpressApp/pybotx/branch/master)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## Особенности

* Простая для использования
* Поддерживает коллбэки BotX
* Легко интегрируется с асинхронными веб-фреймворками
* Полное покрытие тестами
* Полное покрытие аннотациями типов


## Установка

Используя `poetry`:

```bash
poetry add pybotx
```

**Предупреждение:** Данный проект находится в активной разработке (`0.y.z`) и
его API может быть изменён при повышении минорной версии.


## Информация о мессенджере eXpress и платформе BotX

Документацию по мессенджеру (включая руководство пользователя и администратора)
можно найти на [официальном сайте](https://express.ms/).

Перед тем, как продолжать знакомство с библиотекой `pybotx`,
советуем прочитать данные статьи: [Что такое чат-боты и SmartApp
](https://docs.express.ms/chatbots/developer-guide/getting-started/what-is-chatbot/)
и [Взаимодействие с Bot API и BotX API
](https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/).
В этих статьях находятся исчерпывающие примеры работы с платформой, которые
легко повторить, используя `pybotx`.

Также не будет лишним ознакомиться с [документацией по плаформе BotX
](https://hackmd.ccsteam.ru/s/botx_platform).


## Примеры готовых проектов на базе pybotx

* [Next Feature Bot](https://github.com/ExpressApp/next-feature-bot) - бот,
  используемый для тестирования функционала платформы BotX.
* [ToDo Bot](https://github.com/ExpressApp/todo-bot) - бот для ведения списка
  дел.
* [Weather SmartApp](https://github.com/ExpressApp/weather-smartapp) -
  приложение для просмотра погоды.


## Минимальный пример бота (интеграция с FastAPI)

```python
from http import HTTPStatus
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# В этом и последующих примерах импорт из `pybotx` будет производиться
# через звёздочку для краткости. Однако, это не является хорошей практикой.
from pybotx import *

collector = HandlerCollector()


@collector.command("/echo", description="Send back the received message body")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(message.body)


# Сюда можно добавлять свои обработчики команд
# или копировать примеры кода, расположенные ниже.


bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            # Не забудьте заменить эти учётные данные на настоящие,
            # когда создадите бота в панели администратора.
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            cts_url="https://cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
)

app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


# На этот эндпоинт приходят команды BotX
# (сообщения и системные события).
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


# На этот эндпоинт приходят события BotX для SmartApps, обрабатываемые синхронно.
@app.post("/smartapps/request")
async def sync_smartapp_event_handler(request: Request) -> JSONResponse:
    response = await bot.sync_execute_raw_smartapp_event(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(response.jsonable_dict(), status_code=HTTPStatus.OK)


# К этому эндпоинту BotX обращается, чтобы узнать
# доступность бота и его список команд.
@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(
        dict(request.query_params),
        request_headers=request.headers,
    )
    return JSONResponse(status)


# На этот эндпоинт приходят коллбэки с результатами
# выполнения асинхронных методов в BotX.
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

## Примеры


### Получение сообщений

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D1%8B%D1%85-%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D0%B9))*

```python
from uuid import UUID

from pybotx import *

ADMIN_HUIDS = (UUID("123e4567-e89b-12d3-a456-426614174000"),)

collector = HandlerCollector()


@collector.command("/visible", description="Visible command")
async def visible_handler(_: IncomingMessage, bot: Bot) -> None:
    # Обработчик команды бота. Команда видимая, поэтому описание
    # является обязательным.
    print("Hello from `/visible` handler")


@collector.command("/_invisible", visible=False)
async def invisible_handler(_: IncomingMessage, bot: Bot) -> None:
    # Невидимая команда - не отображается в списке команд бота
    # и не нуждается в описании.
    print("Hello from `/invisible` handler")


async def is_admin(status_recipient: StatusRecipient, bot: Bot) -> bool:
    return status_recipient.huid in ADMIN_HUIDS


@collector.command("/admin-command", visible=is_admin)
async def admin_command_handler(_: IncomingMessage, bot: Bot) -> None:
    # Команда показывается только если пользователь является админом.
    # Список команд запрашивается при открытии чата в приложении.
    print("Hello from `/admin-command` handler")


@collector.default_message_handler
async def default_handler(_: IncomingMessage, bot: Bot) -> None:
    # Если команда не была найдена, вызывается `default_message_handler`,
    # если он определён. Такой обработчик может быть только один.
    print("Hello from default handler")
```


### Получение системных событий

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D1%8B%D1%85-%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D0%B9))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.chat_created
async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    # Работа с событиями производится с помощью специальных обработчиков.
    # На каждое событие можно объявить только один такой обработчик.
    print(f"Got `chat_created` event: {event}")


@collector.smartapp_event
async def smartapp_event_handler(event: SmartAppEvent, bot: Bot) -> None:
    print(f"Got `smartapp_event` event: {event}")
```


### Получение синхронных SmartApp событий

```python
from pybotx import *

collector = HandlerCollector()


# Обработчик синхронных Smartapp событий, приходящих на эндпоинт `/smartapps/request`
@collector.sync_smartapp_event
async def handle_sync_smartapp_event(
    event: SmartAppEvent, bot: Bot,
) -> BotAPISyncSmartAppEventResultResponse:
    print(f"Got sync smartapp event: {event}")
    return BotAPISyncSmartAppEventResultResponse.from_domain(
        data={},
        files=[],
    )
```


### Middlewares

*(Этот функционал относится исключительно к `pybotx`)*

```python
from httpx import AsyncClient

from pybotx import *

collector = HandlerCollector()


async def custom_api_client_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    # До вызова `call_next` (обязателен в каждой миддлвари) располагается
    # код, который выполняется до того, как сообщение дойдёт до
    # своего обработчика.
    async_client = AsyncClient()

    # У сообщения есть объект состояния, в который миддлвари могут добавлять
    # необходимые данные.
    message.state.async_client = async_client

    await call_next(message, bot)

    # После вызова `call_next` выполняется код, когда обработчик уже
    # завершил свою работу.
    await async_client.aclose()


@collector.command(
    "/fetch-resource",
    description="Fetch resource from passed URL",
    middlewares=[custom_api_client_middleware],
)
async def fetch_resource_handler(message: IncomingMessage, bot: Bot) -> None:
    async_client = message.state.async_client
    response = await async_client.get(message.argument)
    print(response.status_code)
```

### Сборщики обработчиков

*(Этот функционал относится исключительно к `pybotx`)*

```python
from uuid import UUID, uuid4

from pybotx import *

ADMIN_HUIDS = (UUID("123e4567-e89b-12d3-a456-426614174000"),)


async def request_id_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    message.state.request_id = uuid4()
    await call_next(message, bot)


async def ensure_admin_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    if message.sender.huid not in ADMIN_HUIDS:
        await bot.answer_message("You are not admin")
        return

    await call_next(message, bot)


# Для того чтобы добавить новый обработчик команды,
# необходимо создать экземпляр класса `HandlerCollector`.
# Позже этот сборщик будет использован при создании бота.
main_collector = HandlerCollector(middlewares=[request_id_middleware])

# У сборщиков (как у обработчиков), могут быть собственные миддлвари.
# Они автоматически применяются ко всем обработчикам данного сборщика.
admin_collector = HandlerCollector(middlewares=[ensure_admin_middleware])

# Сборщики можно включать друг в друга. В данном примере у
# `admin_collector` будут две миддлвари. Первая - его собственная,
# вторая - полученная при включении в `main_collector`.
main_collector.include(admin_collector)
```


### Отправка сообщения

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F))*
```python
from uuid import UUID

from pybotx import *

collector = HandlerCollector()


@collector.command("/answer", description="Answer to sender")
async def answer_to_sender_handler(message: IncomingMessage, bot: Bot) -> None:
    # Т.к. нам известно, откуда пришло сообщение, у `pybotx` есть необходимый
    # контекст для отправки ответа.
    await bot.answer_message("Text")


@collector.command("/send", description="Send message to specified chat")
async def send_message_handler(message: IncomingMessage, bot: Bot) -> None:
    try:
        chat_id = UUID(message.argument)
    except ValueError:
        await bot.answer_message("Invalid chat id")
        return

    # В данном случае нас интересует не ответ, а отправка сообщения
    # в другой чат. Чат должен существовать и бот должен быть в нём.
    try:
        await bot.send_message(
            bot_id=message.bot.id,
            chat_id=chat_id,
            body="Text",
        )
    except Exception as exc:
        await bot.answer_message(f"Error: {exc}")
        return

    await bot.answer_message("Message was send")


@collector.command("/prebuild-answer", description="Answer with prebuild message")
async def prebuild_answer_handler(message: IncomingMessage, bot: Bot) -> None:
    # С помощью OutgoingMessage можно выносить логику
    # формирования ответов в другие модули.
    answer = OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body="Text",
    )
    await bot.send(message=answer)
```


#### Отправка сообщения с кнопками

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-%D1%81-%D0%BA%D0%BD%D0%BE%D0%BF%D0%BA%D0%B0%D0%BC%D0%B8))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/bubbles", description="Send buttons")
async def bubbles_handler(message: IncomingMessage, bot: Bot) -> None:
    # Если вам нужна клавиатура под полем для ввода сообщения,
    # используйте `KeyboardMarkup`. Этот класс имеет те же методы,
    # что и `BubbleMarkup`.
    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/choose",
        label="Red",
        data={"pill": "red"},
        background_color="#FF0000",
    )
    bubbles.add_button(
        command="/choose",
        label="Blue",
        data={"pill": "blue"},
        background_color="#0000FF",
        new_row=False,
    )

    # В кнопку можно добавит ссылку на ресурс,
    # для этого нужно добавить url в аргумент `link`, а `command` оставить пустым,
    # `alert` добавляется в окно подтверждения при переходе по ссылке.
    bubbles.add_button(
        label="Bubble with link",
        alert="alert text",
        link="https://example.com",
    )

    await bot.answer_message(
        "The time has come to make a choice, Mr. Anderson:",
        bubbles=bubbles,
    )
```


#### Упоминание пользователя

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D1%83%D0%BF%D0%BE%D0%BC%D0%B8%D0%BD%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/send-contact", description="Send author's contact")
async def send_contact_handler(message: IncomingMessage, bot: Bot) -> None:
    contact = MentionBuilder.contact(message.sender.huid)
    await bot.answer_message(f"Author is {contact}")


@collector.command("/echo-contacts", description="Send back recieved contacts")
async def echo_contact_handler(message: IncomingMessage, bot: Bot) -> None:
    if not (contacts := message.mentions.contacts):
        await bot.answer_message("Please send at least one contact")
        return

    answer = ", ".join(map(str, contacts))
    await bot.answer_message(answer)
```


#### Отправка файла в сообщении

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0-%D1%84%D0%B0%D0%B9%D0%BB%D0%B0-%D0%B2-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B8))*
```python
from aiofiles.tempfile import NamedTemporaryFile

from pybotx import *

collector = HandlerCollector()


@collector.command("/send-file", description="Send file")
async def send_file_handler(message: IncomingMessage, bot: Bot) -> None:
    # Для создания файла используется file-like object
    # с поддержкой асинхронных операций.
    async with NamedTemporaryFile("wb+") as async_buffer:
        await async_buffer.write(b"Hello, world!\n")
        await async_buffer.seek(0)

        file = await OutgoingAttachment.from_async_buffer(async_buffer, "test.txt")

    await bot.answer_message("Attached file", file=file)


@collector.command("/echo-file", description="Echo file")
async def echo_file_handler(message: IncomingMessage, bot: Bot) -> None:
    if not (attached_file := message.file):
        await bot.answer_message("Attached file is required")
        return

    await bot.answer_message("", file=attached_file)
```

### Редактирование сообщения

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D1%80%D0%B5%D0%B4%D0%B0%D0%BA%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/increment", description="Self-updating widget")
async def increment_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.source_sync_id:  # ID сообщения, в котором была нажата кнопка.
        current_value = message.data["current_value"]
        next_value = current_value + 1
    else:
        current_value = 0
        next_value = 1

    answer_text = f"Counter: {current_value}"
    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/increment",
        label="+",
        data={"current_value": next_value},
    )

    if message.source_sync_id:
        await bot.edit_message(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
            body=answer_text,
            bubbles=bubbles,
        )
    else:
        await bot.answer_message(answer_text, bubbles=bubbles)
```

### Удаление сообщения

*([подробное описание функции](
https://hackmd.ccsteam.ru/s/E9MPeOxjP#%D0%A3%D0%B4%D0%B0%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/deleted-message", description="Self-deleted message")
async def deleted_message_handler(message: IncomingMessage, bot: Bot) -> None:
    if message.source_sync_id:  # ID сообщения, в котором была нажата кнопка.
        await bot.delete_message(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
        )
        return

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/deleted-message",
        label="Delete",
    )

    await bot.answer_message("Self-deleted message", bubbles=bubbles)
```


### Обработчики ошибок

*(Этот функционал относится исключительно к `pybotx`)*

```python
from loguru import logger

from pybotx import *


async def internal_error_handler(
    message: IncomingMessage,
    bot: Bot,
    exc: Exception,
) -> None:
    logger.exception("Internal error:")

    await bot.answer_message(
        "**Error:** internal error, please contact your system administrator",
    )


# Для перехвата исключений существуют специальные обработчики.
# Бот принимает словарь из типов исключений и их обработчиков.
bot = Bot(
    collectors=[],
    bot_accounts=[],
    exception_handlers={Exception: internal_error_handler},
)
```

### Создание чата

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5-%D1%87%D0%B0%D1%82%D0%B0))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/create-group-chat", description="Create group chat")
async def create_group_chat_handler(message: IncomingMessage, bot: Bot) -> None:
    if not (contacts := message.mentions.contacts):
        await bot.answer_message("Please send at least one contact")
        return

    try:
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name="New group chat",
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[contact.entity_id for contact in contacts],
        )
    except (ChatCreationProhibitedError, ChatCreationError) as exc:
        await bot.answer_message(str(exc))
        return

    chat_mention = MentionBuilder.chat(chat_id)
    await bot.answer_message(f"Chat created: {chat_mention}")
```

### Поиск пользователей

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D0%BF%D0%BE%D0%B8%D1%81%D0%BA-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F))*
```python
import dataclasses

from pybotx import *

collector = HandlerCollector()


@collector.command("/my-info", description="Get info of current user")
async def search_user_handler(message: IncomingMessage, bot: Bot) -> None:
    try:
        user_info = await bot.search_user_by_huid(
            bot_id=message.bot.id,
            huid=message.sender.huid,
        )
    except UserNotFoundError:  # Если пользователь и бот находятся на разных CTS
        await bot.answer_message("User not found. Maybe you are on a different cts.")
        return

    await bot.answer_message(f"Your info:\n{dataclasses.asdict(user_info)}\n")
```

### Получение списка пользователей

*([подробное описание функции](
https://docs.express.ms/chatbots/developer-guide/development-and-debugging/backend/interaction-with-bot-api-and-botx-api/#%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B0-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D0%B5%D0%B9-%D0%BD%D0%B0-cts))*
```python
from pybotx import *

collector = HandlerCollector()


@collector.command("/get_users_list", description="Get a list of users")
async def users_list_handler(message: IncomingMessage, bot: Bot) -> None:
    async with bot.users_as_csv(
        bot_id=message.bot.id,
        cts_user=True,
        unregistered=False,
        botx=False,
    ) as users:
        async for user in users:
            print(user)
```
