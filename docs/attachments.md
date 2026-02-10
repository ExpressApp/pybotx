# AttachmentFactory

`AttachmentFactory` изолирует I/O и даёт удобные методы для создания `OutgoingAttachment`.

## From bytes

```python
attachment = await attachment_factory.from_bytes(
    b"hello",
    filename="hello.txt",
)
```

## From file path

```python
attachment = await attachment_factory.from_path("/path/to/file.txt")
```

## From file object

```python
from io import BytesIO

buffer = BytesIO(b"content")
attachment = await attachment_factory.from_file(buffer, filename="demo.txt")
```

## Использование с builder

```python
message = (
    OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="file")
    .with_file(attachment)
    .build()
)
await bot.send(message=message)
```

