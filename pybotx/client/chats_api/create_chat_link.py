from typing import Literal, NoReturn
from uuid import UUID

import httpx

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.chats import (
    ChatLinkCreationError,
    ChatLinkCreationProhibitedError,
)
from pybotx.client.exceptions.common import ChatNotFoundError
from pybotx.client.exceptions.http import InvalidBotXStatusCodeError
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.chats import ChatLink
from pybotx.models.enums import ChatLinkTypes


class BotXAPIChatLinkParams(UnverifiedPayloadBaseModel):
    link_type: ChatLinkTypes
    access_code: Missing[str | None]
    link_ttl: Missing[int | None]

    @classmethod
    def from_domain(
        cls,
        link_type: ChatLinkTypes,
        access_code: Missing[str | None],
        link_ttl: Missing[int | None],
    ) -> "BotXAPIChatLinkParams":
        return cls(
            link_type=link_type,
            access_code=access_code,
            link_ttl=link_ttl,
        )


class BotXAPICreateChatLinkRequestPayload(UnverifiedPayloadBaseModel):
    chat_id: UUID
    link: BotXAPIChatLinkParams

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        link_type: ChatLinkTypes,
        access_code: Missing[str | None] = Undefined,
        link_ttl: Missing[int | None] = Undefined,
    ) -> "BotXAPICreateChatLinkRequestPayload":
        return cls(
            chat_id=chat_id,
            link=BotXAPIChatLinkParams.from_domain(
                link_type=link_type,
                access_code=access_code,
                link_ttl=link_ttl,
            ),
        )


class BotXAPIChatLinkResult(VerifiedPayloadBaseModel):
    url: str
    link_type: ChatLinkTypes
    access_code: str | None
    link_ttl: int | None

    def to_domain(self) -> ChatLink:
        return ChatLink(
            url=self.url,
            link_type=self.link_type,
            access_code=self.access_code,
            link_ttl=self.link_ttl,
        )


class BotXAPICreateChatLinkResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIChatLinkResult

    def to_domain(self) -> ChatLink:
        return self.result.to_domain()


def server_error_handler(response: httpx.Response) -> NoReturn:
    reason = response.json().get("reason")

    if reason == "error_from_messaging_service":
        raise ChatLinkCreationError.from_response(response)

    raise InvalidBotXStatusCodeError(response)


class CreateChatLinkMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        403: response_exception_thrower(ChatLinkCreationProhibitedError),
        404: response_exception_thrower(ChatNotFoundError),
        500: server_error_handler,
    }

    async def execute(
        self,
        payload: BotXAPICreateChatLinkRequestPayload,
    ) -> BotXAPICreateChatLinkResponsePayload:
        path = "/api/v3/botx/chats/create_link"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPICreateChatLinkResponsePayload,
            response,
        )
