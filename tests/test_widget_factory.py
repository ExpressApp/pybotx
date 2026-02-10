from dependency_injector import providers

from pybotx.application.widgets.factory import WidgetFactory
from pybotx.container import BotXContainer
from pybotx.domain.ports import WidgetStateStorePort


def test__widget_factory__defaults() -> None:
    factory = WidgetFactory()
    widget = factory.single(command="/widget")
    assert widget.include_state_in_metadata is False
    assert widget.elems_key == "elems"
    assert widget.index_key == "current_index"


def test__widget_factory__override_per_widget() -> None:
    factory = WidgetFactory(include_state_in_metadata=False)
    widget = factory.multi(command="/widget", page_size=1, include_state_in_metadata=True)
    assert widget.include_state_in_metadata is True
    assert widget.elems_key == "elems"
    assert widget.page_key == "page"
    assert widget.sync_ids_key == "sync_ids"


def test__widget_factory__from_container_config() -> None:
    container = BotXContainer()
    container.config.widgets.include_state_in_metadata.from_value(True)
    factory = container.widget_factory()
    widget = factory.single(command="/widget")
    assert widget.include_state_in_metadata is True


def test__widget_state_store__from_container() -> None:
    container = BotXContainer()
    container.config.widgets.state_store.backend.from_value("memory")
    container.config.widgets.state_store.serializer.from_value("json")
    container.config.widgets.state_store.serializer_version.from_value(2)
    store = container.widget_state_store()
    assert isinstance(store, WidgetStateStorePort)


def test__widget_state_store__redis_from_container() -> None:
    class DummyRedis:
        async def get(self, key):
            return None

        async def set(self, key, value, ex=None):
            return True

        async def delete(self, key):
            return 1

    container = BotXContainer()
    container.config.widgets.state_store.backend.from_value("redis")
    container.config.widgets.state_store.redis_prefix.from_value("test:")
    container.config.widgets.state_store.serializer.from_value("json")
    container.config.widgets.state_store.serializer_version.from_value(2)
    container.redis_client.override(providers.Object(DummyRedis()))
    store = container.widget_state_store()
    assert isinstance(store, WidgetStateStorePort)
