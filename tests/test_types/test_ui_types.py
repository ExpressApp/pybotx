from botx import BubbleElement, KeyboardElement


def test_bubble():
    bubble = BubbleElement(command="bubble")
    assert bubble.command == bubble.label == "bubble"

    bubble = BubbleElement(command="command", label="label")
    assert bubble.command == "command" and bubble.label == "label"


def test_keyboard():
    keyboard = KeyboardElement(command="bubble")
    assert keyboard.command == keyboard.label == "bubble"

    keyboard = KeyboardElement(command="command", label="label")
    assert keyboard.command == "command" and keyboard.label == "label"
