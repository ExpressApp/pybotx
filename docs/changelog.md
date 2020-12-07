## 0.16.0 (Dec 02, 2020)

### Added

* Support of attachments in messages for bot's api v4
* Support of reply in messages for bot's api v4
* Builder of attachments in MessageBuilder
* Test content in RFC 2397 format
* Entity building methods for `MessageBuilder`
* Flag `is_forward` for `Message`
* Bot's method `reply` for reply by message

### Changed

* Type of `message.entities` from `List[Attachment]` to is `EntityList`
* `send()` sending only direct notification, not command result

## 0.15.17 (Nov 20, 2020)

### Changed

* Now you can update attached file while updating message


## 0.15.16 (Nov 19, 2020)

### Added

* New event `left_from_chat`, which stores HUIDs of members who left the chat


## 0.15.15 (Nov 17, 2020)

### Added

* New event `deleted_from_chat`, which stores deleted members HUIDs


## 0.15.14 (Nov 13, 2020)

### Fixed

* `added_to_chat` event is created properly now


## 0.15.13 (Nov 6, 2020)

## Added

* Add `bot_id` to outgoing messages debug logs. Incoming messages already have it


## 0.15.12 (Oct 30, 2020)

### Added

* Added width weight for bubbles and keyboard buttons (`h_size`). The more width weight,
  the more horizontal space is occupied by button.


## 0.15.11 (Oct 30, 2020)

### Added

* Added `.sig`, `.mp3` and `.mp4` to allowed file formats


## 0.15.10 (Oct 29, 2020)

### Added

* Added alerts (toast on button press) for bubbles and keyboard buttons


## 0.15.9 (Oct 28, 2020)

### Added

* New message option 'silent_response' to hide next user messages in chat


## 0.15.8 (Oct 23, 2020)

### Changed

* `httpx` dependency was updated to 0.16
* `loguru` dependency was updated to 0.5


## 0.15.7 (Oct 22, 2020)

### Added

* New bot method `add_admin_roles` for promoting users to admins (bot should have
  admin role itself)


## 0.15.6 (Oct 12, 2020)

### Fixed

* Fix `system:chat_created` event (`UserInChatCreated.name` now optional)


## 0.15.5 (Sep 16, 2020)

### Added

* Added `.ppt` and `.pptx` to allowed file formats


## 0.15.4 (Sep 4, 2020)

### Added

* Update accepted extensions list (`.jpg`, `.jpeg`, `.gif`, `.png`, `.json`, `.zip`, `.rar`)


## 0.15.3 (Aug 26, 2020)

### Added

* Models were added to API Reference

### Fixed

* Fix "handler not found" error message


## 0.15.2 (Aug 7, 2020)

### Fixed

* Fix overwriting SendingMessage credentials


## 0.15.1 (Aug 4, 2020)

### Fixed

* Fix optional fields in UserFromSearch model


## 0.15.0 (Jul 23, 2020)

### Added

* Added startup and shutdown lifespan events.
* Added support for synchronous requests (now `molten` is required for tests).
* Added support for `system:added_to_chat` event.
* Added support for forwarded messages.
* Added support for passing additional arguments to `Bot.status()`.
* Added methods for:
    * chat creation;
    * information about chat retrieving;
    * search user by email, user HUID or AD login/domain.
* Add client flag for logger.
* Allow to update message through `.send()` from bot.
* Add `metadata` property to message.

### Fixed

* Fix information about sender for `system:chat_created` event.
* Fix crash when forwarding message to bot.
* Fix error on creating empty credentials.

### Changed

* Simplify middlewares. Now sync middlewares will receive sync `call_next` and
asynchronous async `call_next`.
* `TestClient` will now propagate unhandled errors.
* Rewrite inner clients. They now work with `methods` classes.
* Update `httpx` to `^0.13.0`
* Use bot as default dependency overrides provider.
* Simplify cache key.


## 0.14.1 (Apr 29, 2020)

### Added

* Add flag for messages sent from buttons.

### Fixed

* Attach dependencies on default handler when collector is included by another.
* Suppress `KeyError` when dropping key from next steps storage.

## 0.14.0 (Apr 3, 2020)

### Added

* Support for external entities in incoming message, like mentions.
* Add ability to specify custom message id for new message from bot.

### Changed

* Refactor exceptions to be more usefule. Now exceptions have additional properties with extra data.
* If there will be an error when convering function to handler or dependency, then exception will contain information about failed attributes.
* Collector will iterate through handlers in right order.
* Change deploing documentation to github pages from master branch.

### Fixed

* Fix shape for `bot_disabled` response.

## 0.13.6 (Mar 20, 2020)

### Added

* Add Netlify for documention preview.
* Parse handler docstring as `full_description` for handler.
* Preserve order of added handlers.

### Changed

* Skip validation for incoming file, so files with unsupported extensions.

### Fixed

* Fix logging file.

## 0.13.5 (Mar 6, 2020)

### Added

* Add channel type into `MentionTypes`.

### Changed

* Replace travis with github actions.

### Fixed

* Fix dependencies extending when use `Collector.include_collector` and dependencies are
defined in collector initialization.
* Fix default handler including into another collector.
* Fix message text logging.
* Fix internal links in docs.

## 0.13.4 (Mar 3, 2020)

### Added

* Examples of bots that are built using `pybotx`:
    * Bot that defines finite-state machine behaviour for handlers.

### Changed

* Log exception traceback with `logger.exception` instead of `logger.error` when error was
not caught.
* Default handler will be excluded from status by default (as it was in library versions before 0.13.0).

## 0.13.3 (Feb 26, 2020)

### Added

* Add background dependencies to next step middleware.
* Next step break handler can be registered as function.
* Add methods to add/remove users to/from chat using `Bot.add_users_into_chat()` and `Bot.remove_users_from_chat()`.

### Fixed

* Add missing `dependency_overrides_provider` to `botx.collecting.Collector.add_handler`.
* Encode message update payload by alias.

### Changed

* Refactored next step middleware
* Next step middleware won't now lookup for handler in bot.
* Disable `loguru` logger by default.

## 0.13.2 (Feb 14, 2020)

### Fixed

* Check that there are futures while stopping bot.
* Strip command in `Handler.command_for` so no space at the end.

## 0.13.1 (Feb 6, 2020)

### Added

* Stealth mode enable/disable methods `Bot.enable_stealth_mode()` and `Bot.disable_stealth_mode()`.

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
* Added parsing command query_params into handler arguments.

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
