from botx.models.buttons import Button


class CustomButton(Button):
    """Button without custom behaviour."""


def test_label_will_be_set_to_command_if_none():
    assert CustomButton(command="/tmp").label == "/tmp"


def test_label_can_be_set_if_passed_explicitly():
    assert CustomButton(command="/tmp", label="temp").label == "temp"


def test_setting_ui_flag_on_buttons():
    assert CustomButton(command="/cmd").data.get("ui")
