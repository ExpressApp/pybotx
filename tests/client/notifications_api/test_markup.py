import asyncio
from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import BubbleMarkup, Button, KeyboardMarkup
from pybotx.models.message.markup import ButtonTextAlign
from tests.testkit import BotXRequest, mock_botx, ok_payload

pytestmark = [
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v4/botx/notifications/direct"
CHAT_ID = "054af49e-5e18-4dca-ad73-4f96b6de63fa"
SYNC_ID = "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"


@pytest.mark.asyncio
async def test__markup__defaults_filled(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "bubble": [
                    [
                        {
                            "command": "/bubble-button",
                            "data": {},
                            "label": "Bubble button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "data": {},
                            "label": "Keyboard button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
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

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
                bubbles=bubbles,
                keyboard=keyboard,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called


@pytest.mark.asyncio
async def test__markup__correctly_built(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "bubble": [
                    [
                        {
                            "command": "/bubble-button-1",
                            "data": {},
                            "label": "Bubble button 1",
                            "opts": {"silent": True, "align": "center"},
                        },
                        {
                            "command": "/bubble-button-2",
                            "data": {},
                            "label": "Bubble button 2",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-3",
                            "data": {},
                            "label": "Bubble button 3",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-4",
                            "data": {},
                            "label": "Bubble button 4",
                            "opts": {"silent": True, "align": "center"},
                        },
                        {
                            "command": "/bubble-button-5",
                            "data": {},
                            "label": "Bubble button 5",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
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
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
                bubbles=bubbles,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called


@pytest.mark.asyncio
async def test__markup__color_and_align(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {
                "body": "Buttons styles:",
                "bubble": [
                    [
                        {
                            "command": "/button",
                            "data": {},
                            "label": "Green font, left align",
                            "opts": {
                                "font_color": "#25B43D",
                                "align": "left",
                                "silent": True,
                            },
                        },
                    ],
                    [
                        {
                            "command": "/button",
                            "data": {},
                            "label": "Green background, center align",
                            "opts": {
                                "background_color": "#25B43D",
                                "align": "center",
                                "silent": True,
                            },
                        },
                    ],
                    [
                        {
                            "command": "/button",
                            "data": {},
                            "label": "Red font, green background, right align",
                            "opts": {
                                "font_color": "#ED4747",
                                "background_color": "#25B43D",
                                "align": "right",
                                "silent": True,
                            },
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard",
                            "data": {},
                            "label": "Green background, left align",
                            "opts": {
                                "background_color": "#25B43D",
                                "align": "left",
                                "silent": True,
                            },
                        },
                    ],
                ],
                "status": "ok",
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    bubbles = BubbleMarkup()

    bubbles.add_button(
        command="/button",
        label="Green font, left align",
        text_color="#25B43D",
        align=ButtonTextAlign.LEFT,
    )
    bubbles.add_button(
        command="/button",
        label="Green background, center align",
        background_color="#25B43D",
        align=ButtonTextAlign.CENTER,
    )
    bubbles.add_button(
        command="/button",
        label="Red font, green background, right align",
        text_color="#ED4747",
        background_color="#25B43D",
        align=ButtonTextAlign.RIGHT,
    )

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command="/keyboard",
        label="Green background, left align",
        background_color="#25B43D",
        align=ButtonTextAlign.LEFT,
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Buttons styles:",
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
                bubbles=bubbles,
                keyboard=keyboard,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called


@pytest.mark.asyncio
async def test__markup__link(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "group_chat_id": CHAT_ID,
            "notification": {
                "body": "Buttons links:",
                "bubble": [
                    [
                        {
                            "data": {},
                            "label": "Open me",
                            "opts": {
                                "silent": True,
                                "align": "center",
                                "handler": "client",
                                "link": "https://example.com",
                            },
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "data": {},
                            "label": "Open me",
                            "opts": {
                                "silent": True,
                                "align": "center",
                                "handler": "client",
                                "link": "https://example.com",
                            },
                        },
                    ],
                ],
                "status": "ok",
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"sync_id": SYNC_ID}),
        HTTPStatus.ACCEPTED,
    )

    bubbles = BubbleMarkup()
    bubbles.add_button(
        label="Open me",
        silent=True,
        link="https://example.com",
    )

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        label="Open me",
        silent=True,
        link="https://example.com",
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Buttons links:",
                bot_id=bot_id,
                chat_id=UUID(CHAT_ID),
                bubbles=bubbles,
                keyboard=keyboard,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": SYNC_ID,
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert (await task) == UUID(SYNC_ID)
    assert endpoint.called


def test__markup__bubble_without_command_error_raised() -> None:
    # - Arrange -
    bubbles = BubbleMarkup()

    # - Act -
    with pytest.raises(ValueError) as exc:
        bubbles.add_button(
            label="label",
            silent=True,
        )

    # - Assert -
    assert "Command arg is required" in str(exc.value)


def test__markup__built_button_without_command_error_raised2() -> None:
    # - Arrange -
    with pytest.raises(ValueError) as exc:
        Button(
            label="Bubble",
        )

    # - Assert -
    assert "Either 'command' or 'link' must be provided" in str(exc.value)


def test__markup__comparison() -> None:
    # - Arrange -
    button = Button("/test", "test")

    # - Assert -
    assert BubbleMarkup([[button]]) == BubbleMarkup([[button]])
