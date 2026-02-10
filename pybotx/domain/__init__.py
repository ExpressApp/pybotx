__all__ = (
    "attachment_factory",
    "constants",
    "converters",
    "errors",
    "logger",
    "missing",
    "models",
    "message_builder",
    "bot_links",
    "text_builder",
    "widgets",
    "ports",
)


def __getattr__(name: str):  # type: ignore[override]
    if name in __all__:
        return __import__(f"{__name__}.{name}", fromlist=[name])
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
