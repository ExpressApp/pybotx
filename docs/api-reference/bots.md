`pybotx` provides `Bot` class writing bots that inherit handlers registration behaviour from `HandlersCollector`:

* `Bot(*, concurrent_tasks, credentials)` - bot that provides an asynchronous sdk.
    * `concurrent_tasks: int = 1500` - the number of coroutines that can be executed by the bot at the same time, the rest will be in the queue.
    * `credentials: Optional[BotCredentials] = None`
* `sync.Bot(*, tasks_limit, credentials)` - bot that provides a synchronous sdk.
    * `tasks_limit: int` - the number of threads that can be used by the bot to execute handlers at the same time, by default - numbers of CPU cores X 4
    * `credentials: Optional[BotCredentials] = None`
    
### Lifespan methods
* `.start()` - runs the necessary parts that can not be run in the initializer.
* `.stop()` -  stops what was started at the `.start`.

### Commands execution
* `.execute_command(data)` - start the handler associated with the command from the date.
    * `data: Dict[str, Any]` - message payload, should be serializable into `Message`.
    
### Sending messages to `BotX API`
* `.reply(message)` - send a message using the `ReplyMessage` created earlier in the code manually.
    * `message: ReplyMessage` - previously created and configured message object.
* `.send_message(text, credentials, *, file, markup, options)` - send message to chat.
    * `text: str` - the text that will be send to chat.
    * `credentials: SendingCredentials` - an object to specify data for sending message.
    * `file: Optional[Union[TextIO, BinaryIO] = None` - file-like object that will be attached to the message <b>(unsupported on clients for now)</b>.
    * `markup: Optional[Union[BinaryIO, TextIO]] = None` - an object to add specials UI elements to the message, like bubbles and keyboard buttons.
    * `options: Optional[NotifyOptions] = None` - an object for specifying additional configuration for messages, for example, 
for displaying notifications, users who will receive messages and mentions.
* `.answer_message(text, message, *, file, recipients, mentions, bubble, keyboard, opts)` - send chat message using `message` passed to handler.
    * `text: str` - the text that will be send to chat.
    * `message: Message` - the message object passed to your handler
    * `file: Optional[Union[TextIO, BinaryIO]] = None`
    * `markup: Optional[Union[BinaryIO, TextIO]] = None`
    * `options: Optional[NotifyOptions] = None`
* `.send_file(file, sync_id, bot_id, host)` - send file to chat using message id.
    * `file: Union[TextIO, BinaryIO]` - file-like object that will be sent to user.
    * `credentials: SendingCredentials`

### Properties

* `.credentials: BotCredentials` - collection of registered `CTS` with secretes and tokens in it.

### Handlers Registrations
* `.register_next_step_handler(message, callback, *args, **kwargs)` - register the handler that will be used to execute the next command from the user.
    * `message: Message` - message whose properties will be used to register the handler.
    * `callback: Callable` - callable object or coroutine to use as handler.
    * `*args: Any` - additional positional arguments that will be passed to the handler.
    * `**kwargs: Any` - additional key arguments to be passed to the handler.

### Errors Handlers Registrations
* `exception_catcher(exceptions, force_replace)` - decorator to register a handler that will be used when an exception occurs during 
the execution of a handler for a command.
    * `exceptions: List[Type[Exception]]` - list of exception types that will be handled by exception handler
    * `force_replace: bool = False` - replace the existing handler for exception with a new one if the new one, 
otherwise `.exception_catcher` will raise a `BotXException` exception if there are duplicates.

### External setters/getters
* `.add_credentials(credentials)` - add credentials of known CTS with hosts and their secret keys.
    * `credentials: BotCredentials` - an instance of `BotCredentials` with a list of registered `CTS` and obtained tokens.
* `.add_cts(cts)` - register one instance of `CTS`.
    * `cts: CTS` - instance of the registered `CTS`.
* `.get_cts_by_host(host) -> str` - helper to get `CTS` by host name.
    * `host: str` - `CTS` host name.
* `.get_token_from_cts(host) -> str` - helper to get token from registered `CTS` instance if there was one get or raise` BotXException`.
    * `host: str` - `CTS` host name.
* `.status() -> Status` - the status that should be returned to the BotX API when calling `/status`, and can also be useful in the create `/help` command.
