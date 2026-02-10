from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from uuid import UUID

import aiofiles
from aiocsv.readers import AsyncDictReader
from aiofiles.tempfile import NamedTemporaryFile, TemporaryDirectory

from pybotx.domain.models.users import UserFromCSV
from pybotx.infrastructure.botx_api.method_factory import BotXApiMethodFactory
from pybotx.infrastructure.client.users_api.user_from_csv import BotXAPIUserFromCSVResult
from pybotx.infrastructure.client.users_api.users_as_csv import (
    BotXAPIUsersAsCSVRequestPayload,
    UsersAsCSVMethod,
)


class UsersCsvService:
    def __init__(self, *, method_factory: BotXApiMethodFactory) -> None:
        self._method_factory = method_factory

    @asynccontextmanager
    async def stream_users(
        self,
        *,
        bot_id: UUID,
        cts_user: bool = True,
        unregistered: bool = True,
        botx: bool = False,
    ) -> AsyncIterator[AsyncIterator[UserFromCSV]]:
        method = self._method_factory.build(UsersAsCSVMethod, bot_id=bot_id)
        payload = BotXAPIUsersAsCSVRequestPayload.from_domain(
            cts_user=cts_user,
            unregistered=unregistered,
            botx=botx,
        )

        async with AsyncExitStack() as stack:
            tmp_dir = await stack.enter_async_context(TemporaryDirectory())
            tmp_file = await stack.enter_async_context(
                NamedTemporaryFile(dir=tmp_dir, mode="w+b"),
            )

            await method.execute(payload, tmp_file)
            await tmp_file.seek(0)

            text_file = await stack.enter_async_context(
                aiofiles.open(tmp_file.name, mode="r"),
            )
            reader = AsyncDictReader(text_file)

            async def iterator() -> AsyncIterator[UserFromCSV]:
                async for row in reader:
                    yield BotXAPIUserFromCSVResult.model_validate(row).to_domain()

            yield iterator()


__all__ = ("UsersCsvService",)
