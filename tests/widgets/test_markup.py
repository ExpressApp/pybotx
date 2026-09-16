from pybotx.widgets.markup import MessageMarkup, clone_markup, merge_message_markup


def test__message_markup__add_buttons() -> None:
    markup = MessageMarkup()

    markup.add_bubble(command="/bubble", label="Bubble")
    markup.add_keyboard(command="/keyboard", label="Keyboard")

    bubble_rows = [[button.label for button in row] for row in markup.bubbles]
    keyboard_rows = [[button.label for button in row] for row in markup.keyboard]

    assert bubble_rows == [["Bubble"]]
    assert keyboard_rows == [["Keyboard"]]


def test__clone_markup__copy_rows() -> None:
    markup = MessageMarkup()
    markup.add_bubble(command="/bubble-1", label="Bubble 1")
    markup.add_bubble(command="/bubble-2", label="Bubble 2", new_row=False)

    cloned = clone_markup(markup.bubbles)
    cloned.add_button(command="/bubble-3", label="Bubble 3")

    original_rows = [[button.label for button in row] for row in markup.bubbles]
    cloned_rows = [[button.label for button in row] for row in cloned]

    assert original_rows == [["Bubble 1", "Bubble 2"]]
    assert cloned_rows == [["Bubble 1", "Bubble 2"], ["Bubble 3"]]


def test__merge_message_markup__merge_bubbles_and_keyboard() -> None:
    primary = MessageMarkup()
    primary.add_bubble(command="/bubble-1", label="Bubble 1")
    primary.add_keyboard(command="/keyboard-1", label="Keyboard 1")

    additional = MessageMarkup()
    additional.add_bubble(command="/bubble-2", label="Bubble 2")
    additional.add_keyboard(command="/keyboard-2", label="Keyboard 2")

    merged = merge_message_markup(primary, additional)

    assert [[button.label for button in row] for row in merged.bubbles] == [
        ["Bubble 1"],
        ["Bubble 2"],
    ]
    assert [[button.label for button in row] for row in merged.keyboard] == [
        ["Keyboard 1"],
        ["Keyboard 2"],
    ]
