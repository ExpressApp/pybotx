from typing import List, Literal, NoReturn
from uuid import UUID

import httpx

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.chats import (
    CantUpdatePersonalChatError,
    InvalidUsersListError,
)
from pybotx.client.exceptions.common import ChatNotFoundError, PermissionDeniedError
from pybotx.client.exceptions.http import InvalidBotXStatusCodeError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIAddAdminRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    user_huids: List[UUID]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        huids: List[UUID],
    ) -> "BotXAPIAddAdminRequestPayload":
        return cls(group_chat_id=chat_id, user_huids=huids)


class BotXAPIAddAdminResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


def bad_request_error_handler(response: httpx.Response) -> NoReturn:
    reason = response.json().get("reason")

    if reason == "chat_members_not_modifiable":
        raise CantUpdatePersonalChatError.from_response(
            response,
            "Personal chat couldn't have admins",
        )
    elif reason == "admins_not_changed":
        raise InvalidUsersListError.from_response(
            response,
            "Specified users are already admins or missing from chat",
        )

    raise InvalidBotXStatusCodeError(response)


class AddAdminMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        400: bad_request_error_handler,
        403: response_exception_thrower(PermissionDeniedError),
        404: response_exception_thrower(ChatNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIAddAdminRequestPayload,
    ) -> None:
        path = "/api/v3/botx/chats/add_admin"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(BotXAPIAddAdminResponsePayload, response)
