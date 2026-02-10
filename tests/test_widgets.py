from uuid import UUID, uuid4

import pytest

from pybotx.domain.errors import InvalidWidgetPayloadError
from pybotx.domain.missing import Undefined
from pybotx.domain.widgets import MultiMessageWidget, SingleMessageWidget


def _rows(bubbles):
    return list(bubbles)


def test__single_widget__renders_buttons() -> None:
    widget = SingleMessageWidget(command="/widget")

    body, metadata, bubbles = widget.render(elems=[1, 2, 3], current_index=0)
    assert body == "1"
    assert metadata == {"elems": [1, 2, 3]}
    rows = _rows(bubbles)
    assert len(rows) == 1
    assert rows[0][0].label == "Вперед"
    assert rows[0][0].data == {"current_index": 1}

    body, metadata, bubbles = widget.render(elems=[1, 2, 3], current_index=1)
    assert body == "2"
    rows = _rows(bubbles)
    assert len(rows) == 1
    assert [btn.label for btn in rows[0]] == ["Назад", "Вперед"]
    assert rows[0][0].data == {"current_index": 0}
    assert rows[0][1].data == {"current_index": 2}

    body, metadata, bubbles = widget.render(elems=[1, 2, 3], current_index=2)
    assert body == "3"
    rows = _rows(bubbles)
    assert len(rows) == 1
    assert rows[0][0].label == "Назад"
    assert rows[0][0].data == {"current_index": 1}


def test__single_widget__build_edit_from_message(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/widget")
    message = incoming_message_factory()
    message.data = {"current_index": "1"}
    message.metadata = {"elems": ["a", "b", "c"]}
    message.source_sync_id = uuid4()

    edit = widget.build_edit_from_message(message)

    assert edit.sync_id == message.source_sync_id
    assert edit.body == "b"
    assert edit.metadata == {"elems": ["a", "b", "c"]}


def test__single_widget__invalid_payload(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/widget")
    message = incoming_message_factory()

    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.data = {"current_index": 0}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.metadata = {"elems": [1]}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.metadata = {"elems": "nope"}
    message.source_sync_id = uuid4()
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.metadata = {"elems": [1]}
    message.data = {"current_index": True}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.data = {"current_index": "bad"}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.data = {"current_index": 1.5}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    with pytest.raises(InvalidWidgetPayloadError):
        widget.render(elems=[], current_index=0)

    with pytest.raises(InvalidWidgetPayloadError):
        widget.render(elems=[1], current_index=2)


def test__single_widget__build_outgoing() -> None:
    widget = SingleMessageWidget(command="/widget")
    bot_id = uuid4()
    chat_id = uuid4()

    outgoing = widget.build_outgoing(
        bot_id=bot_id,
        chat_id=chat_id,
        elems=["x", "y"],
        current_index=1,
    )

    assert outgoing.bot_id == bot_id
    assert outgoing.chat_id == chat_id
    assert outgoing.body == "y"
    assert outgoing.metadata == {"elems": ["x", "y"]}


def test__single_widget__metadata_without_state() -> None:
    widget = SingleMessageWidget(command="/widget")

    body, metadata, _bubbles = widget.render(elems=[1, 2], current_index=0)
    assert body == "1"
    assert metadata == {"elems": [1, 2]}


def test__single_widget__metadata_with_state() -> None:
    widget = SingleMessageWidget(
        command="/widget",
        include_state_in_metadata=True,
    )

    _body, metadata, _bubbles = widget.render(elems=[1, 2], current_index=1)
    assert metadata == {"elems": [1, 2], "current_index": 1}


def test__single_widget__invalid_params() -> None:
    with pytest.raises(InvalidWidgetPayloadError, match="command must be a string"):
        SingleMessageWidget(command=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="render_item must be callable"):
        SingleMessageWidget(command="/widget", render_item=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="prev_label must be a string"):
        SingleMessageWidget(command="/widget", prev_label=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="next_label must be a string"):
        SingleMessageWidget(command="/widget", next_label=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="elems_key must be a string"):
        SingleMessageWidget(command="/widget", elems_key=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="index_key must be a string"):
        SingleMessageWidget(command="/widget", index_key=object())  # type: ignore[arg-type]


def test__multi_widget__build_head_and_tail_messages() -> None:
    widget = MultiMessageWidget(command="/widget", page_size=3)
    bot_id = uuid4()
    chat_id = uuid4()
    sync_ids = [uuid4(), uuid4()]

    head_messages = widget.build_outgoing_head_messages(
        bot_id=bot_id,
        chat_id=chat_id,
        elems=[1, 2, 3, 4, 5, 6],
        page=0,
    )
    assert [msg.body for msg in head_messages] == ["1", "2"]
    assert all(msg.metadata is Undefined for msg in head_messages)

    tail_message = widget.build_outgoing_tail_message(
        bot_id=bot_id,
        chat_id=chat_id,
        elems=[1, 2, 3, 4, 5, 6],
        page=0,
        sync_ids=sync_ids,
    )
    assert tail_message.body == "3"
    assert tail_message.metadata == {
        "elems": [1, 2, 3, 4, 5, 6],
        "sync_ids": [str(sync_id) for sync_id in sync_ids],
    }
    rows = _rows(tail_message.bubbles)
    assert len(rows) == 1
    assert rows[0][0].label == "Вперед"
    assert rows[0][0].data == {"page": 1}


def test__multi_widget__metadata_without_state() -> None:
    widget = MultiMessageWidget(command="/widget", page_size=2)
    bot_id = uuid4()
    chat_id = uuid4()
    sync_ids = [uuid4()]

    tail_message = widget.build_outgoing_tail_message(
        bot_id=bot_id,
        chat_id=chat_id,
        elems=[1, 2],
        page=0,
        sync_ids=sync_ids,
    )

    assert tail_message.metadata == {
        "elems": [1, 2],
        "sync_ids": [str(sync_ids[0])],
    }


def test__multi_widget__metadata_with_state() -> None:
    widget = MultiMessageWidget(
        command="/widget",
        page_size=2,
        include_state_in_metadata=True,
    )
    bot_id = uuid4()
    chat_id = uuid4()
    sync_ids = [uuid4()]

    tail_message = widget.build_outgoing_tail_message(
        bot_id=bot_id,
        chat_id=chat_id,
        elems=[1, 2],
        page=0,
        sync_ids=sync_ids,
    )

    assert tail_message.metadata == {
        "elems": [1, 2],
        "sync_ids": [str(sync_ids[0])],
        "page": 0,
    }


def test__multi_widget__invalid_params() -> None:
    with pytest.raises(InvalidWidgetPayloadError, match="command must be a string"):
        MultiMessageWidget(command=object(), page_size=1)  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="empty_text must be a string"):
        MultiMessageWidget(command="/widget", page_size=1, empty_text=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="render_item must be callable"):
        MultiMessageWidget(command="/widget", page_size=1, render_item=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="prev_label must be a string"):
        MultiMessageWidget(command="/widget", page_size=1, prev_label=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="next_label must be a string"):
        MultiMessageWidget(command="/widget", page_size=1, next_label=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="elems_key must be a string"):
        MultiMessageWidget(command="/widget", page_size=1, elems_key=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="sync_ids_key must be a string"):
        MultiMessageWidget(command="/widget", page_size=1, sync_ids_key=object())  # type: ignore[arg-type]

    with pytest.raises(InvalidWidgetPayloadError, match="page_key must be a string"):
        MultiMessageWidget(command="/widget", page_size=1, page_key=object())  # type: ignore[arg-type]


def test__multi_widget__edit_from_message(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/widget", page_size=3)
    message = incoming_message_factory()
    sync_ids = [uuid4(), uuid4()]

    message.source_sync_id = uuid4()
    message.data = {"page": 1}
    message.metadata = {
        "elems": [1, 2, 3, 4, 5, 6],
        "sync_ids": [str(sync_id) for sync_id in sync_ids],
        "page": 0,
    }

    edits = widget.build_edit_from_message(message)
    assert [edit.sync_id for edit in edits] == [sync_ids[0], sync_ids[1], message.source_sync_id]
    assert [edit.body for edit in edits] == ["4", "5", "6"]
    rows = _rows(edits[-1].bubbles)
    assert len(rows) == 1
    assert rows[0][0].label == "Назад"
    assert rows[0][0].data == {"page": 0}


def test__multi_widget__empty_slots() -> None:
    widget = MultiMessageWidget(command="/widget", page_size=2)
    bot_id = uuid4()
    chat_id = uuid4()

    head_messages = widget.build_outgoing_head_messages(
        bot_id=bot_id,
        chat_id=chat_id,
        elems=[],
        page=0,
    )
    assert [msg.body for msg in head_messages] == ["Конец списка"]

    tail_message = widget.build_outgoing_tail_message(
        bot_id=bot_id,
        chat_id=chat_id,
        elems=[],
        page=0,
        sync_ids=[uuid4()],
    )
    assert tail_message.body == "Конец списка"


def test__multi_widget__invalid_payload(incoming_message_factory) -> None:
    with pytest.raises(InvalidWidgetPayloadError):
        MultiMessageWidget(command="/widget", page_size=0)

    widget = MultiMessageWidget(command="/widget", page_size=2)
    bot_id = uuid4()
    chat_id = uuid4()

    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_outgoing_tail_message(
            bot_id=bot_id,
            chat_id=chat_id,
            elems=[1, 2],
            page=0,
            sync_ids=[],
        )

    message = incoming_message_factory()
    message.source_sync_id = uuid4()
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.data = {"page": 0}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.metadata = {"elems": [1, 2]}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.metadata = {"elems": [1, 2], "sync_ids": ["invalid"]}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.metadata = {"elems": [1, 2], "sync_ids": [str(uuid4())]}
    message.data = {"page": 2}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)

    message.metadata = {"elems": [1, 2], "sync_ids": [123]}
    message.data = {"page": 0}
    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)


def test__multi_widget__sync_ids_length_mismatch_edit(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/widget", page_size=3)
    message = incoming_message_factory()
    message.source_sync_id = uuid4()
    message.data = {"page": 0}
    message.metadata = {"elems": [1, 2, 3], "sync_ids": [str(uuid4())]}

    with pytest.raises(InvalidWidgetPayloadError):
        widget.build_edit_from_message(message)


def test__multi_widget__page_size_one_without_sync_ids(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/widget", page_size=1)
    message = incoming_message_factory()
    message.source_sync_id = uuid4()
    message.data = {"page": 0}
    message.metadata = {"elems": [1]}

    edits = widget.build_edit_from_message(message)
    assert len(edits) == 1


def test__multi_widget__accepts_uuid_sync_ids(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/widget", page_size=2)
    message = incoming_message_factory()
    sync_id = uuid4()

    message.source_sync_id = uuid4()
    message.data = {"page": 0}
    message.metadata = {"elems": [1, 2], "sync_ids": [sync_id]}

    edits = widget.build_edit_from_message(message)
    assert isinstance(edits[0].sync_id, UUID)
