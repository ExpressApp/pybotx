import asyncio
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
    KeyboardMarkup,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__markup__defaults_filled(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "bubble": [
                    [
                        {
                            "command": "/bubble-button",
                            "data": {},
                            "label": "Bubble button",
                            "opts": {"silent": True},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "data": {},
                            "label": "Keyboard button",
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
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/bubble-button",
        label="Bubble button",
    )

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command="/keyboard-button",
        label="Keyboard button",
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.send(
                "Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                bubbles=bubbles,
                keyboard=keyboard,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__markup__correctly_built(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "bubble": [
                    [
                        {
                            "command": "/bubble-button-1",
                            "data": {},
                            "label": "Bubble button 1",
                            "opts": {"silent": True},
                        },
                        {
                            "command": "/bubble-button-2",
                            "data": {},
                            "label": "Bubble button 2",
                            "opts": {"silent": True},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-3",
                            "data": {},
                            "label": "Bubble button 3",
                            "opts": {"silent": True},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-4",
                            "data": {},
                            "label": "Bubble button 4",
                            "opts": {"silent": True},
                        },
                        {
                            "command": "/bubble-button-5",
                            "data": {},
                            "label": "Bubble button 5",
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
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.send(
                "Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                bubbles=bubbles,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called
