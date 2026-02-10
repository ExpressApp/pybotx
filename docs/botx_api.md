# BotX API

Высокоуровневый интерфейс представлен через `Bot`. Низкоуровневый API реализован в `HttpBotXApi` и строится через `BotXApiMethodFactory`.

Рекомендуемый путь работы:

- Использовать методы `Bot`
- Использовать builders и bulk операции
- Использовать `MessageOptions` для единообразного API

Если нужны transport DTO:

- Inbound contracts для входящих payloads
- Outbound contracts для исходящих API payloads

