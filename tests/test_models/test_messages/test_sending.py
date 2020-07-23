from botx import BubbleElement, KeyboardElement, MessageMarkup, UpdatePayload


def test_message_markup_will_add_row_if_there_is_no_existed_and_not_new_row() -> None:
    markup1 = MessageMarkup()
    markup1.add_bubble("/command", new_row=False)

    markup2 = MessageMarkup()
    markup2.add_bubble("/command")

    assert markup1 == markup2


def test_update_markup_will_can_be_set_from_markup() -> None:
    markup = MessageMarkup()
    markup.add_bubble("/command")
    markup.add_keyboard_button("/command")

    update = UpdatePayload()
    update.set_markup(markup)

    assert update.markup == markup
    assert update.bubbles == markup.bubbles
    assert update.keyboard == markup.keyboard


def test_adding_markup_by_elements() -> None:
    bubble = BubbleElement(command="/command")
    keyboard = KeyboardElement(command="/command")

    markup = MessageMarkup()
    markup.add_bubble_element(bubble)
    markup.add_keyboard_button_element(keyboard)

    assert markup == MessageMarkup(bubbles=[[bubble]], keyboard=[[keyboard]])
