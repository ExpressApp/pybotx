from pybotx import BubbleMarkup


def test__mentions_list_properties__filled() -> None:
    # - Arrange -
    bubbles = BubbleMarkup()
    bubbles.add_button("command1", "label1")
    bubbles.add_button("command2", "label2")
    bubbles.add_button("command3", "label3", new_row=False)

    # - Assert -
    assert (
        bubbles.__repr__()
        == "row 1: command1 (label1)\nrow 2: command2 (label2) | command3 (label3)"
    )
