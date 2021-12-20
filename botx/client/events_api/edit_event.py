from typing import Any, Dict, List, Union
from uuid import UUID

from typing_extensions import Literal  # For python 3.7 support

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.missing import Missing, MissingOptional, Undefined
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.attachments import (
    BotXAPIAttachment,
    IncomingFileAttachment,
    OutgoingAttachment,
)
from botx.models.message.markup import (
    BotXAPIMarkup,
    BubbleMarkup,
    KeyboardMarkup,
    api_markup_from_domain,
)
from botx.models.message.mentions import BotXAPIMention, find_and_replace_embed_mentions


class BotXAPIEditEventOpts(UnverifiedPayloadBaseModel):
    buttons_auto_adjust: Missing[bool]


class BotXAPIEditEvent(UnverifiedPayloadBaseModel):
    body: Missing[str]
    metadata: Missing[Dict[str, Any]]
    opts: Missing[BotXAPIEditEventOpts]
    bubble: Missing[BotXAPIMarkup]
    keyboard: Missing[BotXAPIMarkup]
    mentions: Missing[List[BotXAPIMention]]


class BotXAPIEditEventRequestPayload(UnverifiedPayloadBaseModel):
    sync_id: UUID
    payload: BotXAPIEditEvent
    file: Missing[BotXAPIAttachment]

    @classmethod
    def from_domain(
        cls,
        sync_id: UUID,
        body: Missing[str],
        metadata: Missing[Dict[str, Any]],
        bubbles: Missing[BubbleMarkup],
        keyboard: Missing[KeyboardMarkup],
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment, None]],
        markup_auto_adjust: Missing[bool],
    ) -> "BotXAPIEditEventRequestPayload":
        api_file: MissingOptional[BotXAPIAttachment] = Undefined
        if file:
            assert not file.is_async_file, "async_files not supported"
            api_file = BotXAPIAttachment.from_file_attachment(file)
        elif file is None:
            api_file = None

        mentions: Missing[List[BotXAPIMention]] = Undefined
        if isinstance(body, str):
            body, mentions = find_and_replace_embed_mentions(body)

        return cls(
            sync_id=sync_id,
            payload=BotXAPIEditEvent(
                body=body,
                # TODO: Metadata can be cleaned with `{}`
                metadata=metadata,
                opts=BotXAPIEditEventOpts(
                    buttons_auto_adjust=markup_auto_adjust,
                ),
                bubble=api_markup_from_domain(bubbles) if bubbles else bubbles,
                keyboard=api_markup_from_domain(keyboard) if keyboard else keyboard,
                mentions=mentions,
            ),
            file=api_file,
        )


class BotXAPIEditEventResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class EditEventMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIEditEventRequestPayload,
    ) -> None:
        path = "/api/v3/botx/events/edit_event"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(
            BotXAPIEditEventResponsePayload,
            response,
        )