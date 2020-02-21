## 0.13.2 (Feb 14, 2020)

### Fixed

* Check that there are futures while stopping bot.
* Strip command in `Handler.command_for` so no space at the end.

## 0.13.1 (Feb 6, 2020)

### Added

* Stealth mode enable/disable methods `Bot.stealth_enable` and `Bot.stealth_disable`.

## 0.13.0 (Jan 20, 2020)

!!! warning
    A lot of breaking changes. See API reference for more information.

### Added
* Added `Silent buttons`.
* Added `botx.TestClient` for writing tests for bots.
* Added `botx.MessageBuilder` for building message for tests.
* `botx.Bot` can now accept sequence of `collecting.Handler`.
* `botx.Message` is now not a pydantic model.  Use `botx.IncomingMessage` in webhooks.

### Changed

* `AsyncBot` renamed to `Bot` in `botx.bots`.
* `.stop` method was renamed to `.shutdown` in `botx.Bot`.
* `UserKindEnum` renamed to `UserKinds`.
* `ChatTypeEnum` renamed to `ChatTypes`.

### Removed

* Removed `botx.bots.BaseBot`, only `botx.bots.Bot` is now available.
* Removed `botx.BotCredentials`. Credentials for bot should be registered via
sequence of `botx.ExpressServer` instances.
* `.credentials` property, `.add_credentials`, `.add_cts` methods were removed in `botx.Bot`. 
Known hosts can be obtained via `.known_hosts` field.
* `.start` method in `botx.Bot` was removed.

## 0.12.4 (Oct 12, 2019)

### Added

* Add `cts_user` value to `UserKindEnum`.

## 0.12.3 (Oct 12, 2019)

### Changed

* Update `httpx` to `0.7.5`.
* Use `https` for connecting to BotX API.

### Fixed

* Remove reference about `HandlersCollector.regex_handler` from docs.

## 0.12.2 (Sep 8, 2019)

### Fixed

* Clear `AsyncBot` tasks on shutdown.

## 0.12.1 (Sep 2, 2019)

### Changed

* Upgrade `pydantic` to `0.32.2`.

### Added

* Added `channel` type to `ChatTypeEnum`.

### Fixed

* Export `UserKindEnum` from `botx`.


## 0.12.0 (Aug 30, 2019)

### Changed

* `HandlersCollector.system_command_handler` now takes an `event` argument of type `SystemEventsEnum` instead of the deleted argument `comamnd`.
* `MessageCommand.data` field will now automatically converted to events data types corresponding to special events,
such as creating a new chat with a bot.
* Replaced `requests` and `aiohttp` with `httpx`.
* Moved synchronous `Bot` to `botx.sync` module. The current `Bot` is an alias to the `AsyncBot`.
* `Bot.status` again became a coroutine to add the ability to receive different commands for different users
depending on different conditions defined in the handlers (to be added to future releases, when BotX API support comes up).
* <b>Changed methods signatures</b>. See `api-reference` for details.

### Added

* Added logging via `loguru`.
* `Bot` can now accept both coroutines and normal functions.
* Added mechanism for catching exceptions.
* Add ability to use sync and async functions to send data from `Bot`.
* Added dependency injection system
* Added parsing command params into handler arguments.

### Removed

* `system_command_handler` argument has been removed from the `HandlersCollector.handler` method.
* Dropped `aiojobs`.

### Fixed

* Fixed `opts` shape.

## 0.11.3 (Jul 24, 2019)

### Fixed

* Catch `IndexError` when trying to get next step handler for the message and there isn't available.

## 0.11.2 (Jul 17, 2019)

### Removed

* `.data` field in `BubbleElement` and `KeyboardElement` was removed to fix problem in displaying markup on some clients.

## 0.11.1 (Jun 28, 2019)

### Fixed

* Exception won't be raised on successful status codes from the BotX API.

## 0.11.0 (Jun 27, 2019)

### Changed

* `MkDocs` documentation and move to `github`.
* `BotXException` will be raised if there is an error in sending message, obtaining tokens, parsing incoming message data and some other cases.
* Rename `CommandRouter` to `HandlersCollector`, changed methods, added some new decorators for specific commands.
* Replaced `Bot.parse_status` method with the `Bot.status` property.
* Added generating message for `BotXException` error.

### Added

* `ReplyMessage` class and `.reply` method to bots were added for building answers in command in more comfortable way.
* Options for message notifications.
* Bot's handlers can be registered as next step handlers.
* `MessageUser` has now `email`.

## 0.10.3 (May 31, 2019)

### Fixed

* Fixed passing positional and key arguments into logging wrapper for next step handlers.

## 0.10.2 (May 31, 2019)

### Added

* Next step handlers can now receive positional and key arguments that are passed through their registration.

## 0.10.1 (May 31, 2019)

### Fixed

* Return handler function from `CommandRouter.command` decorator instead of `CommandHandler` instance.

## 0.10.0 (May 28, 2019)

### Changed

* Move `requests`, `aiohttp` and `aiojobs` to optional dependencies.
* All handlers now receive a bot instance that processes current command execution as second argument for handler.
* Files renamed using snake case.
* Returned response text and status from methods for sending messages.

### Added

* Export `pydantic`'s `ValidationError` directly from `botx`.
* Add Readme.md for library.
* Add support for BotX API tokens for bots.
* Add `py.typed` file for `mypy`.
* Add `CommandRouter` for gathering command handlers together and some methods for handling specific commands.
* Add ability to change handlers processing behaviour by using next step handlers.
* Add `botx.bots.Bot.answer_message` method to bots for easier generating answers in commands.
* Add mentions for users in chats.
* Add abstract methods to `BaseBot` and `BaseDispatcher`.

### Fixed

* Fixed some mypy types issues.
* Removed print.

## 0.9.4 (Apr 23, 2019)

### Changed

* Change generation of command bodies for bot status by not forcing leading slash.

## 0.9.3 (Apr 4, 2019)

### Fixed

* Close `aiohttp.client.ClientSession` when calling `AsyncBot.stop()`.

## 0.9.2 (Mar 27, 2019)

### Removed

* Delete unused for now argument `bot` from thread wrapper.

## 0.9.1 (Mar 27, 2019)

### Fixed

* Log unhandled exception from synchronous handlers.

## 0.9.0 (Mar 18, 2019)

### Added

* First public release in PyPI.
* Synchronous and asynchronous API for building bots.
