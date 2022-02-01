# BotX API

---

## [Bots API](https://hackmd.ccsteam.ru/s/E9MPeOxjP#Bots-API)

### [Получение токена](https://hackmd.ccsteam.ru/s/E9MPeOxjP#%D0%9F%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%82%D0%BE%D0%BA%D0%B5%D0%BD%D0%B0)

Токен можно получить для каждого из добавленных аккаунтов бота. Для выбора аккаунта
используется его ID.

!!! note

    Вряд ли вам когда-нибудь понадобится запрашивать токен вручную, `pybotx`
    получает их автоматически.

``` py
--8<-- "docs/snippets/client/bots_api/get_token.py"
```
