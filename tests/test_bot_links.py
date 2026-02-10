import pytest

from pybotx.domain.bot_links import build_bot_command_link
from pybotx.domain.errors import InvalidBotCommandLinkError


HUID = "11111111-1111-1111-1111-111111111111"


def test__build_bot_command_link__base_only() -> None:
    assert (
        build_bot_command_link(huid=HUID)
        == "https://xlnk.ms/open/bot/11111111-1111-1111-1111-111111111111"
    )


def test__build_bot_command_link__with_ets_id() -> None:
    assert (
        build_bot_command_link(huid=HUID, ets_id="trace")
        == "https://xlnk.ms/open/bot/11111111-1111-1111-1111-111111111111?ets_id=trace"
    )


def test__build_bot_command_link__with_body_and_command() -> None:
    assert (
        build_bot_command_link(huid=HUID, body="hello world", command="/start")
        == "https://xlnk.ms/open/bot/11111111-1111-1111-1111-111111111111"
        "?body=hello+world&command=%2Fstart"
    )


def test__build_bot_command_link__with_all_params() -> None:
    assert (
        build_bot_command_link(
            huid=HUID,
            ets_id="abc",
            body="hello",
            command="/start",
        )
        == "https://xlnk.ms/open/bot/11111111-1111-1111-1111-111111111111"
        "?ets_id=abc&body=hello&command=%2Fstart"
    )


def test__build_bot_command_link__host_with_scheme() -> None:
    assert (
        build_bot_command_link(huid=HUID, host="https://xlnk.ms/")
        == "https://xlnk.ms/open/bot/11111111-1111-1111-1111-111111111111"
    )


def test__build_bot_command_link__invalid_params() -> None:
    with pytest.raises(InvalidBotCommandLinkError):
        build_bot_command_link(huid=HUID, body="hello")

    with pytest.raises(InvalidBotCommandLinkError):
        build_bot_command_link(huid=HUID, command="/start")

    with pytest.raises(InvalidBotCommandLinkError):
        build_bot_command_link(huid=HUID, host="")
