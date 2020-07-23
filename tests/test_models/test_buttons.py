from botx.models.buttons import Button


class CustomButton(Button):
    pass


def test_label_will_be_set_to_command_if_none() -> None:
    assert CustomButton(command="/tmp").label == "/tmp"


def test_label_can_be_set_if_passed_explicitly() -> None:
    assert CustomButton(command="/tmp", label="temp").label == "temp"


def test_setting_ui_flag_on_buttons() -> None:
    assert CustomButton(command="/cmd").data.get("ui")
