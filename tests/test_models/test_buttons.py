import pytest
from pydantic import ValidationError

from botx.models.buttons import Button, ButtonOptions


class CustomButton(Button):
    """Button without custom behaviour."""


def test_label_will_be_set_to_command_if_none():
    assert CustomButton(command="/cmd").label == "/cmd"


def test_label_can_be_set_if_passed_explicitly():
    assert CustomButton(command="/cmd", label="temp").label == "temp"


def test_setting_ui_flag_on_buttons():
    assert CustomButton(command="/cmd").data.get("ui")


def test_create_button_options_with_invalid_hsize():
    with pytest.raises(ValidationError) as exc_info:
        ButtonOptions(h_size=0)

    assert "should be positive integer" in str(exc_info)
