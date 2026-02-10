# Message Builders и Options

## MessageOptions

`MessageOptions` упаковывает delivery-опции в один объект.

```python
from pybotx import MessageOptions

options = MessageOptions(
    silent_response=True,
    markup_auto_adjust=True,
    stealth_mode=True,
    send_push=False,
    ignore_mute=True,
)
```

## OutgoingMessageBuilder

```python
from pybotx import OutgoingMessageBuilder

message = (
    OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="Hi!")
    .silent()
    .auto_adjust_buttons()
    .stealth()
    .no_push()
    .force_notification()
    .build()
)

await bot.send(message=message)
```

`with_options` применяет `MessageOptions` к builder.

```python
message = OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="Hi")
message = message.with_options(options).build()
```

## ReplyMessageBuilder

### From incoming message

```python
builder = ReplyMessageBuilder.for_incoming_message(message, body="Reply text")
reply = builder.with_options(options).build()
await bot.reply(message=reply)
```

### Explicit sync_id

```python
builder = ReplyMessageBuilder.for_incoming(message, body="Reply", sync_id=sync_id)
reply = builder.build()
```

## EditMessageBuilder

### From source sync id

```python
builder = EditMessageBuilder.for_incoming_source_id(message)
edit = builder.with_body("Updated text").build()
await bot.edit(message=edit)
```

### Clear helpers

```python
edit = (
    EditMessageBuilder.for_incoming_source_id(message)
    .clear_body()
    .clear_metadata()
    .clear_bubbles()
    .clear_keyboard()
    .clear_file()
    .build()
)
```

