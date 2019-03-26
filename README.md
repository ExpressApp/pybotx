# pyBotX
Version: 1.0.0a9
###### tags: `documentation`, `library`, `botx`, `sdk`, `python`, `bots`

## Содержание
1. [Требования](#requirements)
2. [Пример бота](#simple-example)
3. [Доступные типы](#types)

## Требования <a id="requirements"/>
1. HTTP-сервер с двумя обработчиками для зарезервированных endpoints:
    * `/status` 
    * `/command`

## Пример бота <a id="simple-example"/>
```python
import json

from aiohttp import web
from botx import AsyncBot, Message, BotCredentials

CREDENTIALS = {
  "known_cts": {
    "random.cts.com": [
      {
        "host": "random.cts.com",
        "secret_key": "secret"
      },
      None
    ]
  }
}

bot = AsyncBot(credentials=BotCredentials(**CREDENTIALS))
router = web.RouteTableDef()

@bot.command(description='Send back command argument')
async def echo(message: Message, bot: AsyncBot):
    await bot.send_message(message.command.cmd_arg, message.sync_id, message.bot_id, message.host)

@router.get('/status')
async def status(request: web.Request) -> web.Response:
    return web.json_response((await bot.parse_status()).dict())

@router.post('/command')    
async def command(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"status": "bad request"}, status=400)

    await bot.parse_command(data)
    return web.json_response({"status": "accepted"}, status=202)

async def start_bot_on_startup(app: web.Application):
    await bot.start()
    
async def stop_bot_on_shutdown(app: web.Application):
    await bot.stop()

async def create_app():
    app = web.Application()
    
    app.add_routes(router)
    app.on_startup.append(start_bot_on_startup)
    app.on_shutdown.append(stop_bot_on_shutdown)
    
    await bot.start()
    
    return app


def main():
    web.run_app(create_app(), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
```

## Доступные типы <a id="types"/>
Все типы поддерживают конвертацию в dict или в json, с помощью соответсвующих методов.
1. Элементы интерфейса:
   * BubbleElement:
     * command: str
     * label: Optional[str] = self.command
   * KeyboardElement:
     * command: str
     * label: Optional[str] = self.command
   * CommandUIElement:
     * type: str
     * label: str
     * order: Optional[int] = None
     * value: Optional[Any] = None
     * name: Optional[str] = None
     * disabled: Optional[bool] = None
   * MenuCommand:
     * description: str
     * body: str
     * name: str
     * options: Dict[str, Any] = {}
     * elements: List[CommandUIElement] = []
2. Перечисления:
   * StatusEnum:
      * ok: str = "ok"
      * error: str = "error"
   * ResponseRecipientsEnum:
      * all: str = "all"
   * ChatTypeEnum:
     * chat: str = "chat"
     * group_chat: str = "group_chat"
   * RequestTypeEnum:
      * status: str = "status"
      * command: str = "command"
   * MentionTypeEnum:
      * user: str = "user"
      * all: str = "all"
      * cts: str = "cts"
      * channel: str = "channel"
3. Типы в сообщениях:
   * SyncID(UUID)
   * File:
     * data: str
     * file_name: str
     * file: BinaryIO | [readonly property]
     * raw_data: bytes | [readonly property]
     * media_type: str | [readonly property]
     * from_file(file: Union[TextIO, BinaryIO]) -> File | [classmethod]
   * MentionUser:
     * user_huid: UUID
     * name: str
   * Mention:
     * mention_type: MentionTypeEnum = MentionTypeEnum.user
     * mention_data: MentionUser
   * MessageUser:
      * user_huid: Optional[UUID]
      * group_chat_id: UUID
      * chat_type: ChatTypeEnum
      * ad_login: Optional[str]
      * ad_domain: Optional[str]
      * username: Optional[str]
      * host: str
   * MessageCommand:
      * body: str
      * data: Dict[str, Any] = {}
      * cmd: str | [readonly property]
      * cmd_arg: str | [readonly property]
   * Message:
      * sync_id: SyncID
      * command: MessageCommand
      * file: Optional[File] = None
      * user: MessageUser | ["from" при конвертации в dict и в json]
      * bot_id: UUID
      * body: str | [readonly property]
      * data: Dict[str, Any] | [readonly property]
      * user_huid: Optional[UUID] | [readonly property]
      * ad_login: Optional[str] | [readonly property]
      * group_chat_id: UUID | [readonly property]
      * chat_type: ChatTypeEnum | [readonly property]
      * host: str | [readonly property]
4. Типы в статусе:
   * StatusResult:
     * enabled: bool = True
     * status_message: str = "Bot is working"
     * commands: List[MenuCommand] = []
   * Status:
     * status: StatusEnum = StatusEnum.ok
     * result: StatusResult = StatusResult()
5. Типы для авторизации бота:
   * CTS:
     * host: str
     * secret_key: str
     * calculate_signature(bot_id: UUID) -> str
   * CTSCredentials:
     * bot_id: UUID
     * token: str
   * BotCredentials:
     * known_cts: Dict[str, Tuple[CTS, Optional[CTSCredentials]]] = {}

## Классы для использования ботами <a id="types"/>
1. CommandHandler:
    * name: str
    * command: str
    * description: str
    * func: Callable
    * exclude_from_status: bool = False
    * use_as_default_handler: bool = False
    * options: Dict[str, Any] = {}
    * elements: List[CommandUIElement] = []
    * system_command_handler: bool = False
    * to_status_command() -> Optional[MenuCommand]
2. CommandRouter:
   * add_handler(handler: CommandHandler)
   * add_commands(router: CommandRouter)
   * command(func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        body: Optional[str] = None,
        use_as_default_handler: bool = False,
        exclude_from_status: bool = False,
        system_command_handler: bool = False) -> Callable | [decorator]
   * Bot | AsyncBot [часть методов асинхронные]
     * \_\_init__(*, credentials: Optional[BotCredentials] = None,
        disable_credentials: bool = False) # в зависимости от бота могут быть дополнительные аргументы
     * start()
     * stop()
     * parse_status() -> Status
     * parse_command(data: Dict[str, Any]) -> bool
     * send_message(text: str,
        chat_id: Union[SyncID, UUID, List[UUID]],
        bot_id: UUID,
        host: str,
        *,
        file: Optional[Union[TextIO, BinaryIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        mentions: Optional[List[Mention]] = None,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None) -> Tuple[str, int]
     * send_file(self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str) -> Tuple[str, int]
