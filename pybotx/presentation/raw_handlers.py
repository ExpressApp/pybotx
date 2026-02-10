from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from pydantic import TypeAdapter, ValidationError

from pybotx.presentation.contracts.commands import (
    BotAPIIncomingMessage,
    BotAPISystemEvent,
)
from pybotx.presentation.contracts.enums import BotAPICommandTypes
from pybotx.presentation.contracts.method_callbacks import (
    BotXMethodCallback as BotXMethodCallbackDTO,
)
from pybotx.presentation.contracts.status import (
    BotAPIStatusRecipient,
    build_bot_status_response,
)
from pybotx.presentation.contracts.sync_smartapp_event import (
    BotAPISyncSmartAppEvent,
    BotAPISyncSmartAppEventResponse,
    convert_sync_smartapp_event_response,
)
from pybotx.domain.errors import (
    BotCommandValidationError,
    StatusRequestValidationError,
    SyncSmartAppEventValidationError,
)
from pybotx.domain.logger import log_incoming_request, logger, pformat_jsonable_obj
from pybotx.domain.models.commands import BotCommand
from pybotx.domain.models.method_callbacks import BotXMethodCallback
from pybotx.domain.models.status import BotMenu, StatusRecipient
from pybotx.domain.models.sync_smartapp_event import SyncSmartAppEventResponse
from pybotx.domain.models.system_events.smartapp_event import SmartAppEvent


class RawInputHandlerPort(Protocol):
    def verify_request(
        self,
        headers: Mapping[str, str] | None,
        *,
        trusted_issuers: set[str] | None = None,
    ) -> None: ...  # pragma: no cover

    def async_execute_bot_command(self, bot_command: BotCommand) -> Any: ...  # pragma: no cover

    async def sync_execute_smartapp_event(
        self,
        smartapp_event: SmartAppEvent,
    ) -> SyncSmartAppEventResponse | BotAPISyncSmartAppEventResponse: ...  # pragma: no cover

    async def get_status(self, status_recipient: StatusRecipient) -> BotMenu: ...  # pragma: no cover

    async def set_botx_method_result(
        self,
        callback: BotXMethodCallback,
    ) -> None: ...  # pragma: no cover


def async_execute_raw_bot_command(
    bot: RawInputHandlerPort,
    raw_bot_command: dict[str, Any],
    *,
    verify_request: bool = True,
    request_headers: Mapping[str, str] | None = None,
    logging_command: bool = True,
    trusted_issuers: set[str] | None = None,
) -> None:
    if logging_command:
        log_incoming_request(raw_bot_command, message="Got command: ")

    if verify_request:
        bot.verify_request(request_headers, trusted_issuers=trusted_issuers)

    try:
        command_type = raw_bot_command.get("command", {}).get("command_type")
        if command_type == BotAPICommandTypes.USER:
            bot_api_command = BotAPIIncomingMessage.model_validate(raw_bot_command)
        else:
            bot_api_command = TypeAdapter(BotAPISystemEvent).validate_python(
                raw_bot_command
            )
    except ValidationError as validation_exc:
        raise BotCommandValidationError(
            "Bot command validation error",
        ) from validation_exc

    bot_command = bot_api_command.to_domain(raw_bot_command)
    bot.async_execute_bot_command(bot_command)


async def sync_execute_raw_smartapp_event(
    bot: RawInputHandlerPort,
    raw_smartapp_event: dict[str, Any],
    *,
    verify_request: bool = True,
    request_headers: Mapping[str, str] | None = None,
    logging_command: bool = True,
    trusted_issuers: set[str] | None = None,
) -> BotAPISyncSmartAppEventResponse:
    if logging_command:
        log_incoming_request(
            raw_smartapp_event,
            message="Got sync smartapp event: ",
        )

    if verify_request:
        bot.verify_request(request_headers, trusted_issuers=trusted_issuers)

    try:
        bot_api_smartapp_event = BotAPISyncSmartAppEvent.model_validate(
            raw_smartapp_event
        )
    except ValidationError as validation_exc:
        raise SyncSmartAppEventValidationError(
            "Sync smartapp event validation error",
        ) from validation_exc

    smartapp_event = bot_api_smartapp_event.to_domain(raw_smartapp_event)
    response = await bot.sync_execute_smartapp_event(smartapp_event)
    return convert_sync_smartapp_event_response(response)


async def raw_get_status(
    bot: RawInputHandlerPort,
    query_params: dict[str, str],
    *,
    verify_request: bool = True,
    request_headers: Mapping[str, str] | None = None,
    trusted_issuers: set[str] | None = None,
) -> dict[str, Any]:
    logger.opt(lazy=True).debug(
        "Got status: {status}",
        status=lambda: pformat_jsonable_obj(query_params),
    )

    if verify_request:
        bot.verify_request(request_headers, trusted_issuers=trusted_issuers)

    try:
        bot_api_status_recipient = BotAPIStatusRecipient.model_validate(query_params)
    except ValidationError as exc:
        raise StatusRequestValidationError(
            "Status request validation error",
        ) from exc

    status_recipient = bot_api_status_recipient.to_domain()

    bot_menu = await bot.get_status(status_recipient)
    return build_bot_status_response(bot_menu)


async def set_raw_botx_method_result(
    bot: RawInputHandlerPort,
    raw_botx_method_result: dict[str, Any],
    *,
    verify_request: bool = True,
    request_headers: Mapping[str, str] | None = None,
    trusted_issuers: set[str] | None = None,
) -> None:
    logger.debug("Got callback: {callback}", callback=raw_botx_method_result)

    if verify_request:
        bot.verify_request(request_headers, trusted_issuers=trusted_issuers)

    callback: BotXMethodCallback = TypeAdapter(
        BotXMethodCallbackDTO
    ).validate_python(raw_botx_method_result)

    await bot.set_botx_method_result(callback)
