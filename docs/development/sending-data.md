`Bot` and `AsyncBot` classes from `pybotx` provide you 3 methods for sending message to the user (with some additional data) and 1 for sending the file:

* `.send_message` - send message by passing text, `sync_id`, `group_chat_id` or list of them, `bot_id` and `host`. 
* `.answer_message` - send a message by passing text and the original message that was passed to the command handler.
* `.reply` - send a message by passing a `ReplyMessage` instance.

!!! info
    Note about using different values to send messages
    
    
    * `sync_id` is the `UUID` accosiated with the message in Express. For proper work, it must be always an instance of the `SyncID` class. You can cast an existing `UUID` to this type by passing the value to the init method.
    * `group_chat_id` - is the `UUID` accosiated with one of the chats in Express. In most cases, you can use it to send messages, but you must use `sync_id` to send a file. However, in such cases it can be either an instance of `SyncID` or `UUID`.
    

### Using `send_message`

`Bot.send_message` accepts 4 required positional arguments and many optional:

 * `text: str` - the text that will be send to chat.
 * `chat_id: Union[SyncID, UUID, List[UUID]]` - the identifier of the location where the text will be sent. 
You can send single message to many chats by passing a `list` of chat ids.
 * `bot_id: UUID` - the bot's identifier in the CTS instance.
 * `host: str` - the domain where the BotX API is running.
 
 ---
 
 * `file: Union[TextIO, BinaryIO] = None` - file-like object that will be attached to the message <b>(unsupported on clients for now)</b>.
 * `recipients: Union[List[UUID], str] = "all"` - the list of users  who receive the message, by default - all users in the chat.
 * `mentions: List[Mention] = None` - the list of users that will be mentioned by the bot in the chat.
 * `bubble: List[List[BubbleElement]] = None` - bubble buttons to be attached to the message.
 * `keyboard: List[List[KeyboardElement]] = None` - keyboard buttons that will be displayed after clicking on the message with the icon.
 * `opts: NotificationOpts = None` - options that specify showing notification to client and delivering of this notification by ignoring `do not disturb` settings.

### Using `answer_message`

`Bot.answer_message` accepts 2 required positional arguments and the same optional arguments like `Bot.send_message`:

 * `text: str` - the text that will be send to chat
 * `message: Message` - the message object passed to your handler

### Using `reply`

`Bot.reply` uses another method to send a message. Under the hood, he still uses `Bot.send_message` to perform send operations,
but provides a way for more easily create massive responses. It takes only 1 argument:

* `message: ReplyMessage` - is the <b>answer</b> message from bot

Here is an example of using this method outside from handler:

```Python3
def some_function():
    reply = ReplyMessage(
        text="You were chosen by random.", 
        chat_id=get_random_chat_id(), 
        bot_id=BOT_ID, 
        host=CTS_HOST,
    )
    bot.reply(reply)
```

or inside command handler:

```Python3
@bot.handler
def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message("Answer from `.reply` method.", message)
    bot.reply(reply)
```

### Send file with message

To attach a file to your message, simply pass it to the `file` argument for tje `Bot.send_message` or `Bot.answer_message` methods 
or use `ReplyMessage.add_file` if you use `Bot.reply`. This will create an instance of the `File` class that will be used to send result. 
If you want to use the same file several times, you can create a `File` object manually and use the `File.file` property to reuse the data.

```Python3
@bot.handler
def my_handler(message: Message, bot: Bot)
    with open('file.txt') as f:
        file = File.from_file(f)
       
    bot.answer_message('Your file", message, file=file.file)
    
    reply = ReplyMessage.from_message("Your file (again)", message)
    reply.add_file(file)
    bot.reply(reply)
```

### Send file separately

`Bot` and `AsyncBot` have `.send_file` method that takes 4 required arguments:

 * `file: Union[TextIO, BytesIO]` - file-like object that will be sent to user.
 * `sync_id: Union[SyncID, UUID]` - last message identifier.
 * `bot_id: UUID` - the bot's identifier in the CTS instance.
 * `host: str` - the domain where the BotX API is running.

### Add `Bubble` and `Keyboard`

You can attach bubbles or keyboard buttons to your message. 
A `Bubble` is a button that is stuck to your message. 
`Keyboard` is a panel that will be displayed when you click on the messege with the icon.

Adding these elements to your message is pretty easy. 
If you use the `.send_message` or `.answer_message` methods, you must pass a matrix of elements (`BubbleElement` or `KeyboardElement`) to corresponding arguments.
Each array in this matrix will be a new row.

For example, if you want to add 3 buttons to a message (1 in the first line and 2 in the second):

```Python3
@bot.handler
def my_handler(message: Message, bot: Bot):
    bot.answer_message(
        "Bubble",
        message,
        bubble=[
            [BubbleElement(label="buble 1", command="")],
            [
                BubbleElement(label="buble 2", command=""),
                BubbleElement(label="buble 3", command=""),
            ],
        ],
    )
```

or add keyboard buttons using `.reply`:

```Python3
@bot.handler
def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message(message)
    reply.add_keyboard_button(command="", label="key 1")

    reply.add_keyboard_button(command="", label="key 1")
    reply.add_keyboard_button(command="", label="key 1", new_row=False)
    
    bot.reply(reply)
```

### Mention users in message

You can mention users in your messages and they will receive notification from the chat, even if this chat was muted.

Using `.reply`:

```Python3
@bot.handler
def my_handler(message: Message, bot: Bot):
    user_huid = get_random_user()

    reply = ReplyMessage.from_message(message)
    reply.mention_user(user_huid)
    
    bot.reply(reply)
```

### Select Message Recipients

Similar to the mentions, you can specify the users who will receive your message by filling in `recipients` argument with list of users identifiers. 

### Change Notification Options

`Bot.send_message` and `Bot.answer_message` also take and additional argument `opts`, which is an instance of the `NotificationOpts` class 
and can control message delivery notifications.

`NotificationOpts` take the following arguments:

 * `send: bool` - send a push notification to the user, by default `True`.
 * `force_dnd` - ignore mute mode in chat with user, by default `False`.
 
Using `.reply`, it will look like this to disable the message delivery notification:

```Python3
@bot.handler
def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message(message)
    reply.show_notification(False)
    
    bot.reply(reply)
```

or like this to ignore user's mute mode for the chat with the bot:

```Python3
@bot.handler
def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message(message)
    reply.force_notification(True)
    
    bot.reply(reply)
```