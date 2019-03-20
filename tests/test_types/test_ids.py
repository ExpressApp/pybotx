import uuid

from botx import SyncID


def test_sync_id_from_uuid():
    some_uuid = uuid.uuid4()
    SyncID(some_uuid)
