## 0.12.1

* Export `UserKindEnum` from `botx`.
* Upgrade `pydantic` to `0.32.2`.
* Added `channel` type to `ChatTypeEnum`.

## 0.12.0

* `system_command_handler` argument has been removed from the `HandlersCollector.handler` method.
* `HandlersCollector.system_command_handler` now takes an `event` argument of type `SystemEventsEnum` instead of the deleted argument `comamnd`.
* `MessageCommand.data` field will now automatically converted to events data types corresponding to special events, 
such as creating a new chat with a bot.
* Added logging via `loguru`.
* Dropped `aiojobs`.
* Replaced `requests` and `aiohttp` with `httpx`.
* `Bot` can now accept both coroutines and normal functions.
* Moved synchronous `Bot` to `botx.sync` module. The current `Bot` is an alias to the `AsyncBot`.
* `Bot.status` again became a coroutine to add the ability to receive different commands for different users 
depending on different conditions defined in the handlers (to be added to future releases, when BotX API support comes up).
* Added mechanism for catching exceptions.
* Add ability to use sync and async functions to send data from `Bot`.
* <b>Changed methods signatures</b>. See `api-reference` for details.
* Fixed `opts` shape.
* Added dependency injection system
* Added parsing command params into handler arguments. 

## 0.11.3

* Fixed `IndexError` when trying to get next step handler for the message.

## 0.11.2

* Removed the `data` field in bubbles and keyboards to fix display problem on some clients.

## 0.11.1

* Fixed raising exception on successful status codes from the BotX API.

## 0.11.0

* `BotXException` will be raised if there is an error in sending message, obtaining tokens, parsing incoming message data and some other cases.
* Renamed `CommandRouter` to `HandlersCollector`, changed methods, added some new decorators for specific commands.
* Added new `ReplyMessage` class and `.reply` method to bots for building answers in more comfortable way.
* Added notification options.
* Removed `parse_status` method and replace it with the `status` property for bots.
* Added the ability to register bot's handlers as next step handlers and pass extra arguments for them.
* Added `email` property to `MessageUser`.

## 0.10.3

* Fixed passing positional and key arguments into logging wrapper for next step handlers.

## 0.10.2

* The next step handlers can now receive positional and key arguments that are passed through their registration.

## 0.10.1

* Fixed returning `CommandHandler` instance from `CommandRouter.command` decorator instead of handler's function.

## 0.10.0

* Moved `requests`, `aiohttp` and `aiojobs` to optional dependencies.
* Added `py.typed` file.
* Fixed some mypy types issues.
* Added `CommandRouter` for gathering command handlers together and some methods for handling specific commands.
* Added ability to change handlers processing behaviour by using next step handlers.
* All handlers receive a bot instance that processes current command execution as second argument.
* Added `.answer_message` method to bots for easier interaction.
* Added mentions.

## 0.9.4

* Temporary change in the generation of bot command bodies.

## 0.9.3

* Fixed closing `aiohttp.client.ClientSession` when calling `AsyncBot.stop()`.

## 0.9.2

* Removed unused for now argument `bot` from thread wrapper.

## 0.9.1

* Wrapping synchronous functions for logging unhandled exceptions.

## 0.9.0

* First public release in PyPI.