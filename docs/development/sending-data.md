[Bot][botx.bots.Bot] from `pybotx` provide you 3 methods for sending message to the user (with some additional data) and 1 for sending the file:

* [`.send`][botx.bots.Bot.send] - send a message by passing a [SendingMessage][botx.models.messages.SendingMessage].
* [`.answer_message`][botx.bots.Bot.answer_message] - send a message by passing text and the original [message][botx.models.messages.Message] that was passed to the command handler.
* [`.send_message`][botx.bots.Bot.send_message] - send message by passing text, `sync_id`, `group_chat_id` or list of them, `bot_id` and `host`. 
At most cases you'll prefer [`.send`][botx.bots.Bot.send] method over this one.
* [`.send_file`][botx.bots.Bot.send_file] - send file using file-like object.

!!! info
    Note about using different values to send messages
    
    
    * `sync_id` is the `UUID` accosiated with the message in Express. 
    You should use it only in command handlers as answer on command or when changing already sent message.
    * `group_chat_id` - is the `UUID` accosiated with one of the chats in Express. In most cases, you should use it to 
    send messages, outside of handlers.
    

### Using `.send`

[`.send`][botx.bots.Bot.send] is used to send a message. 

Here is an example of using this method outside from handler:

```Python3
{!./src/development/sending_data/sending_data0.py!}
```

or inside command handler:

```Python3
{!./src/development/sending_data/sending_data1.py!}
```

### Using `.answer_message`

[`.answer_message`][botx.bots.Bot.answer_message] is very useful for replying to command.

```Python3
{!./src/development/sending_data/sending_data2.py!}
```

### Send file

There are several ways to send a file from bot:

* [Attach file][botx.models.messages.SendingMessage.add_file] to an instance of [SendingMessage][botx.models.messages.SendingMessage].
* Pass file to `file` argument into [`.answer_message`][botx.bots.Bot.answer_message] or [`.send_message`][botx.bots.Bot.send_message] methods.
* Use [`.send_file`][botx.bots.Bot.send_file].

#### Attach file to already built message or during initialization

```Python3
{!./src/development/sending_data/sending_data3.py!}
```

#### Pass file as argument

```Python3
{!./src/development/sending_data/sending_data4.py!}
```

#### Using `.send_file`

```Python3
{!./src/development/sending_data/sending_data5.py!}
```

### Attach interactive buttons to your message

You can attach bubbles or keyboard buttons to your message. This can be done using 
[MessageMarkup][botx.models.sending.MessageMarkup] class.
A [Bubble][botx.models.buttons.ButtonElement] is a button that is stuck to your message. 
A [Keyboard][botx.models.buttons.KeyboardElement] is a panel that will be displayed when 
you click on the messege with the icon.

An attached collection of bubbles or keyboard buttons is a matrix of buttons.

Adding these elements to your message is pretty easy. 
For example, if you want to add 3 buttons to a message (1 in the first line and 2 in the second)
you can do something like this:

```Python3
{!./src/development/sending_data/sending_data6.py!}
```

Or like this:

```Python3
{!./src/development/sending_data/sending_data7.py!}
```


Also you can attach buttons to [SendingMessage][botx.models.message.SendingMessage] passing it
into `__init__` or after:

```Python3
{!./src/development/sending_data/sending_data8.py!}
```

### Mention users or another chats in message

You can mention users or another chats in your messages and they will receive notification 
from the chat, even if this chat was muted.

There are 2 types of mentions for users:

* Mention user in chat where message will be sent
* Mention just user account

Here is an example

```Python3
{!./src/development/sending_data/sending_data9.py!}
```
