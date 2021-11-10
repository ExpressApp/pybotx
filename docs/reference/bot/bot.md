# Bot API reference

---

## **Bots API**

::: botx.bot.bot.Bot
    handler: python
    selection:
      members:
        - get_token

---

## **Chats API**

::: botx.bot.bot.Bot
    handler: python
    selection:
      members:
        - list_chats
        - add_users_to_chat
        - remove_users_from_chat
        - create_chat

---

## **Notifications API**

::: botx.bot.bot.Bot
    handler: python
    selection:
      members:
        - answer
        - send
        - send_internal_bot_notification

---

## **Files API**

::: botx.bot.bot.Bot
    handler: python
    selection:
      members:
        - download_file
        - upload_file
