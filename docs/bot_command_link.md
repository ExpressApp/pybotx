# Bot Command Link

`build_bot_command_link` генерирует ссылку, которая открывает чат с ботом и
отправляет ему команду. Это удобно для внешних UI, SmartApp или админ‑панелей.

## Пример

```python
from pybotx import build_bot_command_link

link = build_bot_command_link(
    huid=bot_huid,
    command="/start",
    body="/start",
)
```

## Параметры

- `huid`: UUID бота (его HUID)
- `command`: команда, например `/start` или `/help`
- `body`: текст сообщения (если указан `command`, `body` обязателен)
- `host`: по умолчанию `xlnk.ms`
- `scheme`: по умолчанию `https`

## Рекомендации

- Храните ссылку в UI и показывайте пользователю только при необходимости.
- Команда должна быть валидной BotX командой.
