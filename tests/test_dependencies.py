import pytest

from botx import Depends, Message
from botx.bots import AsyncBot
from botx.dependencies import solve_dependencies
from botx.models import Dependency


def test_public_function_depends():
    def dep_func():
        pass

    assert Depends(dep_func) == Dependency(call=dep_func)


class TestDependenciesSolving:
    @pytest.mark.asyncio
    async def test_sync_solving_without_deps(self, get_bot, message_data):
        def func_without_deps():
            pass

        assert {} == await solve_dependencies(
            Message(**message_data()), get_bot(), Depends(func_without_deps)
        )

    @pytest.mark.asyncio
    async def test_sync_solving_without_sub_deps(self, get_bot, message_data):
        def dep_func():
            return 1

        def func_with_deps(dep=Depends(dep_func)):
            pass

        assert {"dep": 1} == await solve_dependencies(
            Message(**message_data()), get_bot(), Depends(func_with_deps)
        )

    @pytest.mark.asyncio
    async def test_sync_solving_with_sub_deps(self, get_bot, message_data):
        def inner_dep_func():
            return 1

        def dep_func(dep=Depends(inner_dep_func)):
            return {"dep": dep}

        def func_with_deps(dep=Depends(dep_func)):
            pass

        assert {"dep": {"dep": 1}} == await solve_dependencies(
            Message(**message_data()), get_bot(), Depends(func_with_deps)
        )

    @pytest.mark.asyncio
    async def test_sync_solving_with_many_deps(self, get_bot, message_data):
        def inner_dep_func():
            return 1

        def dep_func(dep1=Depends(inner_dep_func), dep2=Depends(inner_dep_func)):
            return {"dep1": dep1, "dep2": dep2}

        def func_with_deps(dep1=Depends(dep_func), dep2=Depends(dep_func)):
            pass

        assert await solve_dependencies(
            Message(**message_data()), get_bot(), Depends(func_with_deps)
        ) == {"dep1": {"dep1": 1, "dep2": 1}, "dep2": {"dep1": 1, "dep2": 1}}

    @pytest.mark.asyncio
    async def test_solving_with_mixing_sync_and_async_deps(self, get_bot, message_data):
        async def inner_dep_func():
            return 1

        def dep_func(dep1=Depends(inner_dep_func), dep2=Depends(inner_dep_func)):
            return {"dep1": dep1, "dep2": dep2}

        async def func_with_deps(dep1=Depends(dep_func), dep2=Depends(dep_func)):
            pass

        assert await solve_dependencies(
            Message(**message_data()), get_bot(), Depends(func_with_deps)
        ) == {"dep1": {"dep1": 1, "dep2": 1}, "dep2": {"dep1": 1, "dep2": 1}}

    @pytest.mark.asyncio
    async def test_solve_deps_with_passing_message_and_bot_in_deps(
        self, get_bot, message_data
    ):
        msg = Message(**message_data())
        bot = get_bot()

        def dep_func_msg(message: Message):
            return {"message": message}

        def dep_func_bot(bot: AsyncBot):
            return {"bot": bot}

        def dep_func(dep1=Depends(dep_func_bot), dep2=Depends(dep_func_msg)):
            return {"dep1": dep1, "dep2": dep2}

        def func_with_deps(dep=Depends(dep_func)):
            pass

        assert await solve_dependencies(msg, bot, Depends(func_with_deps)) == {
            "dep": {"dep1": {"bot": bot}, "dep2": {"message": msg}}
        }
