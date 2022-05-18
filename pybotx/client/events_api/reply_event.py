from typing import Any, Dict, List, Literal, Union
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.attachments import (
    BotXAPIAttachment,
    IncomingFileAttachment,
    OutgoingAttachment,
)
from pybotx.models.message.markup import (
    BotXAPIMarkup,
    BubbleMarkup,
    KeyboardMarkup,
    api_markup_from_domain,
)
from pybotx.models.message.mentions import (
    BotXAPIMention,
    find_and_replace_embed_mentions,
)


class BotXAPIReplyEventMessageOpts(UnverifiedPayloadBaseModel):
    silent_response: Missing[bool]
    buttons_auto_adjust: Missing[bool]


class BotXAPIReplyEvent(UnverifiedPayloadBaseModel):
    status: Literal["ok"]
    body: str
    metadata: Missing[Dict[str, Any]]
    opts: Missing[BotXAPIReplyEventMessageOpts]
    bubble: Missing[BotXAPIMarkup]
    keyboard: Missing[BotXAPIMarkup]
    mentions: Missing[List[BotXAPIMention]]


class BotXAPIReplyEventNestedOpts(UnverifiedPayloadBaseModel):
    send: Missing[bool]
    force_dnd: Missing[bool]


class BotXAPIReplyEventOpts(UnverifiedPayloadBaseModel):
    raw_mentions: Literal[True]
    stealth_mode: Missing[bool]
    notification_opts: Missing[BotXAPIReplyEventNestedOpts]


class BotXAPIReplyEventRequestPayload(UnverifiedPayloadBaseModel):
    source_sync_id: UUID
    reply: BotXAPIReplyEvent
    file: Missing[BotXAPIAttachment]
    opts: BotXAPIReplyEventOpts

    @classmethod
    def from_domain(
        cls,
        sync_id: UUID,
        body: str,
        metadata: Missing[Dict[str, Any]],
        bubbles: Missing[BubbleMarkup],
        keyboard: Missing[KeyboardMarkup],
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]],
        silent_response: Missing[bool],
        markup_auto_adjust: Missing[bool],
        stealth_mode: Missing[bool],
        send_push: Missing[bool],
        ignore_mute: Missing[bool],
    ) -> "BotXAPIReplyEventRequestPayload":
        api_file: Missing[BotXAPIAttachment] = Undefined
        if file:
            api_file = BotXAPIAttachment.from_file_attachment(file)

        body, mentions = find_and_replace_embed_mentions(body)

        return cls(
            source_sync_id=sync_id,
            reply=BotXAPIReplyEvent(
                status="ok",
                body=body,
                metadata=metadata,
                opts=BotXAPIReplyEventMessageOpts(
                    buttons_auto_adjust=markup_auto_adjust,
                    silent_response=silent_response,
                ),
                bubble=api_markup_from_domain(bubbles) if bubbles else bubbles,
                keyboard=api_markup_from_domain(keyboard) if keyboard else keyboard,
                mentions=mentions or Undefined,
            ),
            file=api_file,
            opts=BotXAPIReplyEventOpts(
                raw_mentions=True,
                stealth_mode=stealth_mode,
                notification_opts=BotXAPIReplyEventNestedOpts(
                    send=send_push,
                    force_dnd=ignore_mute,
                ),
            ),
        )


class BotXAPIReplyEventResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class ReplyEventMethod(AuthorizedBotXMethod):
    async def execute(self, payload: BotXAPIReplyEventRequestPayload) -> None:
        path = "/api/v3/botx/events/reply_event"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(
            BotXAPIReplyEventResponsePayload,
            response,
        )
