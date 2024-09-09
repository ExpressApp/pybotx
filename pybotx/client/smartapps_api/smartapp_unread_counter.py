from typing import Literal, Optional
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPISmartAppUnreadCounterRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    counter: int

    @classmethod
    def from_domain(
        cls,
        group_chat_id: UUID,
        counter: int,
    ) -> "BotXAPISmartAppUnreadCounterRequestPayload":
        return cls(
            group_chat_id=group_chat_id,
            counter=counter,
        )


class BotXAPISyncIdResult(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotXAPISmartAppUnreadCounterResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


class SmartAppUnreadCounterMethod(AuthorizedBotXMethod):
    error_callback_handlers = {
        **AuthorizedBotXMethod.error_callback_handlers,
    }

    async def execute(
        self,
        payload: BotXAPISmartAppUnreadCounterRequestPayload,
        wait_callback: bool,
        callback_timeout: Optional[float],
        default_callback_timeout: float,
    ) -> BotXAPISmartAppUnreadCounterResponsePayload:
        path = "/api/v4/botx/smartapps/unread_counter"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        api_model = self._verify_and_extract_api_model(
            BotXAPISmartAppUnreadCounterResponsePayload,
            response,
        )

        await self._process_callback(
            api_model.result.sync_id,
            wait_callback,
            callback_timeout,
            default_callback_timeout,
        )

        return api_model
