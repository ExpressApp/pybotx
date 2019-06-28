## 0.11.1

* Fixed raising exception on successful status codes from BotX API.

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