import logging

import pytest
from loguru import logger


@pytest.fixture()
def _enable_logger():
    logger.enable("botx")


@pytest.fixture()
def loguru_caplog(caplog, _enable_logger):
    class PropogateHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)
