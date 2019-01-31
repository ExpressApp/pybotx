class SyncID(str):
    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, *args, **kwargs)
