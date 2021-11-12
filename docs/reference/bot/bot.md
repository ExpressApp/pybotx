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
        - chat_info
        - add_users_to_chat
        - remove_users_from_chat
        - enable_stealth 
        - disable_stealth
        - create_chat

---

## **Users API**

::: botx.bot.bot.Bot
    handler: python
    selection:
      members:
        - search_user_by_email
        - search_user_by_huid
        - search_user_by_ad

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
