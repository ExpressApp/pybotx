* `HandlersCollector()` - base class for collecting handlers.

### Properties

* `handlers: Dict[Pattern, CommandHandler]` - dictionary of registered handlers with their command patterns.
        
### Handlers Registration

#### Common registration

* `.add_handler(handler, force_replace)` - low-level version of handlers registration.
    * `handler: CommandHandler` - an object to store information associated with the handler.
    * `force_replace: bool = False` - replace the existing `CommandHandler` with a new one if the new handler has a 
matching body with any of the existing ones, otherwise `.add_handler` will raise a `BotXException` exception if there are duplicates.
    
* `.include_handlers(collector, force_replace)` - copy all handlers registered in the `collector` argument to this instance of the `collector`.
    * `collector: HandleresCollector` - an instance of the `HandlersCollector` from which handlers should be copied.
    * `force_replace: bool = False` - replace all handlers with the same body with new instances.

#### Decorators

All registration decorators return original `callback` after registration.

* `.handler(callback, *, name, description, command, commands, use_as_default_handler, exclude_from_status)` - 
register a handler for a `command` or `commands`. Only a `callback` argument is required, others can be generated automatically.
    * `callback: Callable` - handler function that will be run to process the command.
    * `name: Optional[str] = None` - command name (useless field, maybe later will be use inside `pybotx`), 
by default the name of the function in lower case.
    * `description: Optional[str] = None` - description of the command that will be displayed in the status, 
by default built by the rule "`name.capitalize()` description" or by the `__doc__` attribute.
    * `command: Optional[Union[str, Pattern]] = None` - body of the command for which the instance of `Bot` will 
launch the associated handler, by default function name with the underscore replaced with a dash and a single forward slash added 
if not `Pattern` passed as an argument. If the `Pattern` is passed as an argument, then only the unchanged pattern is used.
    * `commands: Optional[List[str, Pattern]] = None` - list of command aliases that also start the execution of the handler.
Uses the same rules as the `command` argument.
    * `use_as_default_handler: bool = False` - indicates that the handler will be used in the absence of other handlers for the command.
    * `exclude_from_status: bool = False` - indicates that handler will not appear in the list of public commands.
* `.regex_handler(callback, *, name, command, commands)` - register a handler with a regular expression, 
such handlers will not appear in the command menu.
    * `callback: Callable`
    * `name: Optional[str] = None`
    * `command: Optional[Pattern] = None` - regular expression to handle the command.
    * `commands: Optional[List[Pattern]] = None` - list of regular expressions.
* `.hidden_command_handler(callback, *, name, command, commands)` - register handler that does not appear in the commands menu.
    * `callback: Callable`
    * `name: Optional[str] = None`
    * `command: Optional[Union[str, Pattern]] = None`
    * `commands: Optional[List[Union[str, Pattern]]] = None`
* `.file_handler(callback)` - handler for transferring one file to bot.
    * `callback: Callable`
* `.default_handler(callback)` - handler for any message that does not have an associated handler.
    * `callback: Callable`
* `.system_event_handler(callback, *, event, name)` - handler for system events, such handlers will not appear in the command menu.
    * `callback: Callable`
    * `event: Union[str, SystemEventsEnum]` - enum of system events that can be sent to the bot through the BotX API.
    * `name: Optional[str] = None`
* `.chat_created_handler(callback)` - handler for the `system:chat_created` system event.

#### Handlers callable signature

The signature of the callback should take 2 required arguments:

  * `message: Message` - the message that started the execution of the handler.
  * `bot: Union[Bot, AsyncBot]` - the bot that handlers the message.
    
It may also take additional arguments that will be passed to it during execution, 
but these arguments must have default values ​​or be asterisks arguments, 
or you must be sure that these arguments will be passed to the handler.