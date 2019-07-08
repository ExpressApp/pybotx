`pybotx` provides 2 classes for writing bots that inherit handlers registration behaviour from `HandlersCollector`:

* `Bot(workers, credentials, disable_credentials)` - bot that provides a synchronous sdk.
    * `workers: int` - the number of threads to run handlers concurrent, the number of processors by default.
    * `credentials: Optional[BotCredentials] = None` - an instance of `BotCredentials` with a list of registered `CTS` and obtained tokens.
    * `disable_credentials: bool = False` - use the deprecated BotX API, which does not require tokens.
* `AsyncBot(credentials, disable_credentials)` - bot that provides a asynchronous sdk.
    * `credentials: Optional[BotCredentials] = None`
    * `disable_credentials: bool = False`
    
The main difference is the type of methods. `Bot` provides some functions as simple `def` functions and `AsyncBot` 
provides the `async def` coroutines:

### Lifespan methods
* `.start()` - runs the necessary parts that can not be run in the initializer.
* `.stop()` -  stops what was started at the `.start`.

### Commands execution
* `.execute_command(data)` - start the handler associated with the command from the date.
    * `data: Dict[str, Any]` - message payload, should be serializable into `Message`.
    
### Sending messages to `BotX API`
* `.reply(message)` - send a message using the `ReplyMessage` created earlier in the code manually.
    * `message: ReplyMessage` - previously created and configured message object.
* `.send_message(text, chat_id, bot_id, host, *, file, recipients, mentions, bubble, keyboard, opts)` - send chat message.
    * `text: str` - the text that will be send to chat.
    * `chat_id: Union[SyncID, UUID, List[UUID]]` - the identifier of the location where the text will be sent. 
You can send single message to many chats by passing a `list` of chat ids.
    * `bot_id: UUID` - the bot's identifier in the CTS instance.
    * `host: str` - the domain where the BotX API is running.
    * `file: Optional[Union[TextIO, BinaryIO] = None` - file-like object that will be attached to the message <b>(unsupported on clients for now)</b>.
    * `recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all` - the list of users  who receive the message, by default - all users in the chat.
    * `mentions: Optional[List[Mention]] = None` - the list of users that will be mentioned by the bot in the chat.
    * `bubble: Optional[List[List[BubbleElement]]] = None` - bubble buttons to be attached to the message.
    * `keyboard: Optional[List[List[KeyboardElement]]] = None` - keyboard buttons that will be displayed after clicking on the message with the icon.
    * `opts: Optional[NotificationOpts] = None` - options that specify showing notification to client and delivering of this notification by ignoring `do not disturb` settings.
* `.answer_message(text, message, *, file, recipients, mentions, bubble, keyboard, opts)` - send chat message using `message` passed to handler.
    * `text: str` - the text that will be send to chat.
    * `message: Message` - the message object passed to your handler
    * `file: Optional[Union[TextIO, BinaryIO]] = None`
    * `recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all`
    * `mentions: Optional[List[Mention]] = None`
    * `bubble: Optional[List[List[BubbleElement]]] = None`
    * `keyboard: Optional[List[List[KeyboardElement]]] = None`
    * `opts: Optional[NotificationOpts] = None`
    * `.send_file(file, sync_id, bot_id, host)` - send file to chat using message id.
    * `file: Union[TextIO, BinaryIO]` - file-like object that will be sent to user.
    * `chat_id: Union[SyncID, UUID]` - last message identifier.
    * `bot_id: UUID` - the bot's identifier in the CTS instance.
    * `host: str` - the domain where the BotX API is running.
    
### Properties

* `.credentials: BotCredentials` - collection of registered `CTS` with secretes and tokens in it.
* `.status: Status` - the status that should be returned to the BotX API when calling `/status`, and can also be useful in the create `/help` command.

### Handlers Registrations
* `.register_next_step_handler(message, callback, *args, **kwargs)` - register the handler that will be used to execute the next command from the user.
    * `message: Message` - message whose properties will be used to register the handler.
    * `callback: Callable` - callable object or coroutine to use as handler.
    * `*args: Any` - additional positional arguments that will be passed to the handler.
    * `**kwargs: Any` - additional key arguments to be passed to the handler.

### External setters/getters
* `.add_credentials(credentials)` - add credentials of known CTS with hosts and their secret keys.
    * `credentials: BotCredentials` - an instance of `BotCredentials` with a list of registered `CTS` and obtained tokens.
* `.add_cts(cts)` - register one instance of `CTS`.
    * `cts: CTS` - instance of the registered `CTS`.
* `.get_cts_by_host(host)` - helper to get `CTS` by host name.
    * `host: str` - `CTS` host name.
* `.get_token_from_cts(host)` - helper to get token from registered `CTS` instance if there was one get or raise` BotXException`.
    * `host: str` - `CTS` host name.


