from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    BubbleMarkup,
    Button,
    HandlerCollector,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
async def test__markup__build_succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "bubbles": [
                    [
                        {
                            "command": "/bubble-button-1",
                            "label": "Bubble button 1",
                            "data": {},
                            "opts": {"silent": True},
                        },
                        {
                            "command": "/bubble-button-2",
                            "label": "Bubble button 2",
                            "data": {},
                            "opts": {"silent": True},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-3",
                            "label": "Bubble button 3",
                            "data": {},
                            "opts": {"silent": True},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-4",
                            "label": "Bubble button 4",
                            "data": {},
                            "opts": {"silent": True},
                        },
                        {
                            "command": "/bubble-button-5",
                            "label": "Bubble button 5",
                            "data": {},
                            "opts": {"silent": True},
                        },
                    ],
                ],
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    bubbles = BubbleMarkup()

    bubbles.add_button(
        command="/bubble-button-1",
        label="Bubble button 1",
        new_row=False,
    )
    bubbles.add_button(
        command="/bubble-button-2",
        label="Bubble button 2",
        new_row=False,
    )
    bubbles.add_button(
        command="/bubble-button-3",
        label="Bubble button 3",
    )

    button_4 = Button(
        command="/bubble-button-4",
        label="Bubble button 4",
    )
    button_5 = Button(
        command="/bubble-button-5",
        label="Bubble button 5",
    )
    bubbles.add_row([button_4, button_5])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        message_id = await bot.send(
            "Hi!",
            bot_id=bot_id,
            chat_id=chat_id,
            bubbles=bubbles,
        )

    # - Assert -
    assert message_id == sync_id
    assert endpoint.called
