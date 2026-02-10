# Пример todo-бота

Путь: `/Users/aleksandrosovskii/PycharmProjects/pybotx/example/todo_bot`

## Конфигурация

Используемые переменные окружения:

- `BOT_ID`
- `BOT_SECRET`
- `CTS_URL`
- `BOT_AUTH_VERSION`
- `VERIFY_REQUESTS`
- `HTTP_BACKEND`
- `HTTP_TIMEOUT`
- `USE_RAW_HTTP_CLIENT`
- `HTTP_RETRY_ENABLED`
- `HTTP_RETRY_BACKEND`
- `HTTP_RETRY_STREAM`
- `HTTP_RETRY_MAX_ATTEMPTS`
- `HTTP_RETRY_MIN_DELAY`
- `HTTP_RETRY_MAX_DELAY`
- `HTTP_RETRY_MULTIPLIER`
- `HTTP_RETRY_JITTER`
- `TODO_STORAGE`
- `BOT_DEDUP_ENABLED`
- `BOT_DEDUP_TTL`
- `BOT_DEDUP_BACKEND`
- `WIDGET_STATE_BACKEND`
- `WIDGET_STATE_REDIS_URL`
- `WIDGET_STATE_REDIS_PREFIX`
- `WIDGET_STATE_SERIALIZER`
- `WIDGET_STATE_SERIALIZER_VERSION`
- `WIDGET_INCLUDE_STATE_IN_METADATA`
- `TODO_DEMO_ENABLED`
- `TODO_DEMO_ALLOW_RISKY`

## Demo-тогглы

Demo-команды вынесены в отдельный модуль и могут быть отключены в проде.

- `TODO_DEMO_ENABLED=false` отключает все demo-команды
- `TODO_DEMO_ALLOW_RISKY=true` включает рискованные команды

## Основные команды

- `/todo_add <text>`
- `/todo_list`
- `/todo_done <id>`
- `/todo_delete <id>`
- `/todo_clear`
- `/todo_help`

## Demo-команды

Список зависит от флагов. Используйте `/demo_help`.

## Демонстрация фасетов

В demo-командах покрыты основные фасеты:

### Chats

- `/demo_list_chats`
- `/demo_chat_info [chat_id]`
- `/demo_personal_chat <huid>`
- `/demo_ensure_personal_chat <huid>` (risky)
- `/demo_create_chat [name]` (risky)
- `/demo_chat_link <chat_id> [type]` (risky)
- `/demo_add_users <chat_id> <huid1,huid2>` (risky)
- `/demo_remove_users <chat_id> <huid1,huid2>` (risky)
- `/demo_promote_admins <chat_id> <huid1,huid2>` (risky)
- `/demo_create_thread <sync_id>` (risky)
- `/demo_pin <sync_id>` (risky)
- `/demo_unpin [chat_id]` (risky)
- `/demo_enable_stealth [chat_id]` (risky)
- `/demo_disable_stealth [chat_id]` (risky)

### Users

- `/demo_users_email <email>`
- `/demo_users_emails <email1,email2>`
- `/demo_users_huid <huid>`
- `/demo_users_other_id <id>`
- `/demo_users_ad <login> <domain>`
- `/demo_users_csv` (risky)
- `/demo_user_update <public_name>` (risky)

### Stickers

- `/demo_sticker_packs`
- `/demo_sticker_pack <pack_id>`
- `/demo_sticker <pack_id> <sticker_id>`
- `/demo_sticker_pack_create <name>` (risky)
- `/demo_sticker_add <pack_id> <emoji>` (risky)
- `/demo_sticker_delete <pack_id> <sticker_id>` (risky)
- `/demo_sticker_pack_delete <pack_id>` (risky)
- `/demo_sticker_pack_edit <pack_id> <name> <preview_id> <sticker_ids...>` (risky)

### Files

- `/demo_files_upload` (risky)
- `/demo_files_download <file_id> [chat_id]` (risky)
- `/demo_files_download_url <url>` (risky)

### SmartApps

- `/demo_smartapps_list` (risky)
- `/demo_smartapp_event` (risky)
- `/demo_smartapp_notification` (risky)
- `/demo_smartapp_custom` (risky)
- `/demo_smartapp_unread` (risky)
- `/demo_smartapp_manifest` (risky)
- `/demo_upload_static` (risky)

### Bot links

- `/demo_bot_command_link [command]`

## Виджеты

В примере используются обычные виджеты и `WidgetSession`.

- `/demo_widget_single`
- `/demo_widget_multi`
- `/demo_widget_session_single`
- `/demo_widget_session_multi`
- `/todo_widget_single`
- `/todo_widget_multi`
- `/todo_widget_session_single`
- `/todo_widget_session_multi`

### Bot.widget_session пример

Демо-команды `/demo_widget_session_single` и `/demo_widget_session_multi` используют `bot.widget_session(...)`:

```python
session = bot.widget_session(widget=single_widget, ttl_seconds=3600)
await session.send_single(
    bot=bot,
    bot_id=message.bot.id,
    chat_id=message.chat.id,
    elems=items,
)
```

## Attachment demo

- `/demo_attachment_factory`
- `/demo_attachment_from_path`
- `/demo_attachment_from_file`

Эти команды доступны только при `TODO_DEMO_ALLOW_RISKY=true`.
