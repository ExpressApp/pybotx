from typing import Literal, Union
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.users import InvalidProfileDataError, UserNotFoundError
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.attachments import (
    BotXAPIAttachment,
    IncomingFileAttachment,
    OutgoingAttachment,
)


class BotXAPIUpdateUserProfileRequestPayload(UnverifiedPayloadBaseModel):
    user_huid: UUID
    name: Missing[str] = Undefined
    public_name: Missing[str] = Undefined
    avatar: Missing[BotXAPIAttachment] = Undefined
    company: Missing[str] = Undefined
    company_position: Missing[str] = Undefined
    description: Missing[str] = Undefined
    department: Missing[str] = Undefined
    office: Missing[str] = Undefined
    manager: Missing[str] = Undefined

    @classmethod
    def from_domain(
        cls,
        user_huid: UUID,
        avatar: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
        name: Missing[str] = Undefined,
        public_name: Missing[str] = Undefined,
        company: Missing[str] = Undefined,
        company_position: Missing[str] = Undefined,
        description: Missing[str] = Undefined,
        department: Missing[str] = Undefined,
        office: Missing[str] = Undefined,
        manager: Missing[str] = Undefined,
    ) -> "BotXAPIUpdateUserProfileRequestPayload":
        api_avatar: Missing[BotXAPIAttachment] = Undefined
        if avatar:
            api_avatar = BotXAPIAttachment.from_file_attachment(avatar)

        return BotXAPIUpdateUserProfileRequestPayload(
            user_huid=user_huid,
            name=name,
            public_name=public_name,
            avatar=getattr(api_avatar, "data", Undefined),
            company=company,
            company_position=company_position,
            description=description,
            department=department,
            office=office,
            manager=manager,
        )


class BotXAPIUpdateUserProfileResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: Literal[True]


class UpdateUsersProfileMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        400: response_exception_thrower(InvalidProfileDataError),
        404: response_exception_thrower(UserNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIUpdateUserProfileRequestPayload,
    ) -> BotXAPIUpdateUserProfileResponsePayload:
        path = "/api/v3/botx/users/update_profile"

        response = await self._botx_method_call(
            "PUT",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIUpdateUserProfileResponsePayload,
            response,
        )
