import pytest

from pybotx.presentation.asgi_lifespan import BotLifespanMiddleware, wrap_asgi_app


class _DummyBot:
    def __init__(self) -> None:
        self.started = 0
        self.stopped = 0

    async def startup(self) -> None:
        self.started += 1

    async def shutdown(self) -> None:
        self.stopped += 1


@pytest.mark.asyncio
async def test__bot_lifespan_middleware__handles_lifespan() -> None:
    bot = _DummyBot()
    sent = []
    messages = [
        {"type": "lifespan.startup"},
        {"type": "lifespan.ping"},
        {"type": "lifespan.shutdown"},
    ]

    async def receive():
        return messages.pop(0)

    async def send(message):  # type: ignore[no-untyped-def]
        sent.append(message)

    middleware = BotLifespanMiddleware(lambda *args, **kwargs: None, bot)

    await middleware(
        {"type": "lifespan"},
        receive,
        send,
    )

    assert bot.started == 1
    assert bot.stopped == 1
    assert sent == [
        {"type": "lifespan.startup.complete"},
        {"type": "lifespan.shutdown.complete"},
    ]


@pytest.mark.asyncio
async def test__bot_lifespan_middleware__passes_non_lifespan() -> None:
    called = []

    async def app(scope, receive, send):  # type: ignore[no-untyped-def]
        called.append(scope["type"])

    middleware = BotLifespanMiddleware(app, _DummyBot())

    await middleware(
        {"type": "http"},
        lambda: None,  # type: ignore[arg-type]
        lambda message: None,  # type: ignore[arg-type]
    )

    assert called == ["http"]


def test__wrap_asgi_app__disabled_returns_app() -> None:
    async def app(scope, receive, send):  # type: ignore[no-untyped-def]
        return None

    assert wrap_asgi_app(app, _DummyBot(), enabled=False) is app


def test__wrap_asgi_app__enabled_wraps() -> None:
    async def app(scope, receive, send):  # type: ignore[no-untyped-def]
        return None

    wrapped = wrap_asgi_app(app, _DummyBot(), enabled=True)

    assert isinstance(wrapped, BotLifespanMiddleware)
