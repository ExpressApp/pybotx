from typing import List

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.users_api.user_from_search import (
    BotXAPISearchUserByEmailsResponsePayload,
)
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPISearchUserByEmailsRequestPayload(UnverifiedPayloadBaseModel):
    emails: List[str]

    @classmethod
    def from_domain(
        cls,
        emails: List[str],
    ) -> "BotXAPISearchUserByEmailsRequestPayload":
        return cls(emails=emails)


class SearchUserByEmailsMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPISearchUserByEmailsRequestPayload,
    ) -> BotXAPISearchUserByEmailsResponsePayload:
        path = "/api/v3/botx/users/by_email"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISearchUserByEmailsResponsePayload,
            response,
        )
