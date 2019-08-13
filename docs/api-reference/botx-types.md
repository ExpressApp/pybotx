All these classes are `pydantic` models except `BotXException` and enums.

### CommandHandler

* `CommandHandler`
    * `.name: str`
    * `.command: Pattern`
    * `.description: str`
    * `.callback: CommandCallback`
    * `.exclude_from_status: bool = False`
    * `.use_as_default_handler: bool = False`
    * `.options: Dict[str, Any] = {}`
    * `.elements: List[CommandUIElement] = []`
    * `.to_status_command() -> Optional[MenuCommand]`

#### CommandCallback
* `CommandCallback`
    * `.callback: Callable`
    * `.args: Tuple[Any, ...] = ()`
    * `.kwargs: Dict[str, Any] = {}`
    * `.background_dependencies: List[Dependency] = []`

### Dependencies

* `Dependency`
    * `.call: Callable`
   
* `Depends(dependency: Callable) -> Any`

### Status

* `Status`
    * `.status: StatusEnum = StatusEnum.ok`
    * `.result: StatusResult = StatusResult()`

#### StatusResult

* `StatusResult`
    * `.enabled: bool = True`
    * `.status_message: str = "Bot is working"`
    * `.commands: List[MenuCommand] = []`

#### MenuCommand

* `MenuCommand`
    * `.description: str`
    * `.body: str`
    * `.name: str`
    * `.options: Dict[str, Any] = {}`
    * `.elements: List[CommandUIElement] = []`

#### CommandUIElement

* `CommandUIElement`
    * `.type: str`
    * `.label: str`
    * `.order: Optional[int] = None`
    * `.value: Optional[Any] = None`
    * `.name: Optional[str] = None`
    * `.disabled: Optional[bool] = None`

### SendingCredentials

* `SendingCredentials`
    * `.sync_id: Optional[UUID] = None`
    * `.chat_ids: List[UUID] = []`
    * `.bot_id: UUID`
    * `.host: str`
    * `.token: Optional[str] = None`


### Message

* `Message`
    * `.sync_id: UUID`
    * `.command: MessageCommand`
    * `.file: Optional[File] = None`
    * `.user: MessageUser`
    * `.bot_id: UUID`
    * `.body: str`
    * `.data: CommandDataType`
    * `.user_huid: Optional[UUID]`
    * `.ad_login: Optional[str]`
    * `.group_chat_id: UUID`
    * `.chat_type: str`
    * `.host: str`

#### MessageUser

* `MessageUser`
    * `.user_huid: Optional[UUID]`
    * `.group_chat_id: UUID`
    * `.chat_type: ChatTypeEnum`
    * `.ad_login: Optional[str]`
    * `.ad_domain: Optional[str]`
    * `.username: Optional[str]`
    * `.is_admin: bool`
    * `.is_creator: bool`
    * `.host: str`
    * `.email: Optional[str]`

#### MessageCommand

* `MessageCommand`
    * `.body: str`
    * `.command_type: CommandTypeEnum`
    * `.data: CommandDataType = {}`
    * `.command: str`
    * `.arguments: List[str]`
    * `.single_argument: str`

### ReplyMessage

* `ReplyMessage`
    * `.text: str`
    * `.sync_id: UUID`
    * `.chat_ids: List[UUID]`
    * `.bot_id: UUID`
    * `.host: str`
    * `.recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all`
    * `.mentions: List[Mention] = []`
    * `.bubble: List[List[BubbleElement]] = []`
    * `.keyboard: List[List[KeyboardElement]] = []`
    * `.opts: NotificationOpts = NotificationOpts()`
    * `.file: Optional[File] = None`
    ---
    
    * `.chat_id: UUID readonly`
    
    ---
    * `.add_file(file)`
    * `.mention_user(user_huid, name)`
    * `.add_recipient(recipient)`
    * `.add_recipients(recipients)`
    * `.add_bubble(command, label, *, data, new_row)`
    * `.add_keyboard_button(command, label, *, data, new_row)`
    * `.show_notification(show)`
    * `.force_notification(force)`
    ---
    * `ReplyMessage.from_message(text, message) -> ReplyMessage`
    

### File

* `File`
    * `.data: str`
    * `.file_name: str`
    * `.file: BinaryIO`
    * `.raw_data: bytes`
    * `.media_type: str`
    ---
    * `File.from_file(file) -> File`


### Markup

* `MessageMarkup`
    * `bubbles: List[List[BubbleElement]] = []`
    * `keyboard: List[List[KeyboardElement]] = []`


#### Bubbles

* `BubbleElement`
    * `.command: str`
    * `.label: Optional[str] = None`
    * `.data: Dict[str, Any] = {}` 

#### Keyboards

* `KeyboardElement`
    * `.command: str`
    * `.label: Optional[str] = None`
    * `.data: Dict[str, Any] = {}` 

### Options

* `MessageOptions`
    * `.recipients: Union[List[UUID], ResponseRecipientsEnum, str] = ResponseRecipientsEnum.all`
    * `.mentions: List[Mention] = []`
    * `.notifications: NotificationOpts = NotificationOpts()`


### Mention

* `Mention`
    * `.mention_type: MentionTypeEnum = MentionTypeEnum.user`
    * `.mention_data: MentionUser`

#### MentionUser

* `MentionUser`
    * `.user_huid: UUID`
    * `.name: Optional[str] = None`

### NotificationOpts

* `NotificationOpts`
    * `.send: bool = True`
    * `.force_dnd: bool = False`

### BotCredentials

* `BotCredentials`
    * `.known_cts: List[CTS] = []`

#### CTS

* `CTSCredentials`
    * `.bot_id: UUID`
    * `.token: str`

#### CTSCredentials

* `CTS`:
    * `.host: str`
    * `.secret_key: str`
    * `.credentials: Optional[CTSCredentials] = None`
    ---
    
    * `.calculate_signature(bot_id: UUID) -> str`

### System Events Data

#### `system:chat_created`

* `UserInChatCreated`
    * `.huid: UUID`
    * `.user_kind: UserKindEnum`
    * `.name: str`
    * `.admin: bool`


* `ChatCreatedData`
    * `.group_chat_id: UUID`
    * `.chat_type: ChatTypeEnum`
    * `.name: str`
    * `.creator: UUID`
    * `.members: List[UserInChatCreated]`


### Enums

#### StatusEnum

* `StatusEnum`
    * `.ok: str = "ok"`
    * `.error: str = "error"`


#### ResponseRecipientsEnum

* `ResponseRecipientsEnum`
    * `.all: str = "all"`


#### ChatTypeEnum

* `ChatTypeEnum`
    * `.chat: str = "chat"`
    * `.group_chat: str = "group_chat"`

#### MentionTypeEnum

* `MentionTypeEnum`
    * `.user: str = "user"`
    * `.all: str = "all"`
    * `.cts: str = "cts"`
    * `.channel: str = "channel"`


#### SystemEventsEnum

* `SystemEventsEnum`
    * `.chat_created: str = "system:chat_created"`

#### UserKindEnum

* `UserKindEnum`
    * `.bot: str = "botx"`
    * `.user: str = "user"`

#### CommandTypeEnum

* `CommandTypeEnum`
    * `.user: str = "user"`
    * `.system: str = "system"`


#### BotXException

* `BotXException(message, data)`
    * `.message: str = ""`
    * `.data: Optional[Dict[str, Any]] = None`


* `BotXDependencyFailure`
