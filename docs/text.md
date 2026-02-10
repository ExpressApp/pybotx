# TextBuilder и упоминания

`TextBuilder` и `MentionComposer` упрощают сборку текста и упоминаний без ручного `<embed_mention>`.

## Базовый пример

```python
from pybotx import TextBuilder

text = (
    TextBuilder()
    .append("Hello ")
    .mention_user_named("Alice", user_id)
    .space()
    .append("welcome!")
    .build()
)
```

## Join helper

```python
text = TextBuilder().join(["one", "two", "three"], separator=", ").build()
```

## Mention helpers

```python
builder = TextBuilder()
text = (
    builder
    .mention_user(user_id, "Alice")
    .space()
    .mention_chat(chat_id, "Developers")
    .space()
    .mention_channel(channel_id, "Announcements")
    .build()
)
```

