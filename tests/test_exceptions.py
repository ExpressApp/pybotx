from botx import ServerUnknownError


def test_server_unknwon_error_string_representation() -> None:
    s = str(ServerUnknownError("cts.example.com"))
    assert s == "unknown server cts.example.com"
