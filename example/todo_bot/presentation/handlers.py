from __future__ import annotations

from collections.abc import Callable, Sequence
from uuid import UUID

from pybotx import (
    Bot,
    HandlerCollector,
    IncomingMessage,
    MultiMessageWidget,
    SingleMessageWidget,
    WidgetFactory,
    WidgetSession,
)
from pybotx.domain.errors import InvalidWidgetPayloadError
from pybotx.infrastructure.services.attachment_factory import AttachmentFactory

from example.todo_bot.application.services import TodoService
from example.todo_bot.domain.errors import TodoNotFoundError, TodoValidationError
from example.todo_bot.domain.models import TodoItem
from example.todo_bot.presentation.demo_handlers import register_demo_handlers


def build_collector(
    todo_service: TodoService,
    attachment_factory: AttachmentFactory,
    widget_factory: WidgetFactory,
    widget_session_factory: Callable[..., WidgetSession],
    demo_enabled: bool = True,
    demo_allow_risky: bool = False,
) -> HandlerCollector:
    collector = HandlerCollector()
    single_widget = widget_factory.single(command="/todo_widget_single")
    multi_widget = widget_factory.multi(command="/todo_widget_multi", page_size=3)
    session_single_widget = widget_factory.single(command="/todo_widget_session_single")
    session_multi_widget = widget_factory.multi(command="/todo_widget_session_multi", page_size=3)
    single_session = widget_session_factory(widget=session_single_widget, ttl_seconds=3600)
    multi_session = widget_session_factory(widget=session_multi_widget, ttl_seconds=3600)

    @collector.command("/todo_add", description="Add a todo item")
    async def todo_add_handler(message: IncomingMessage, bot: Bot) -> None:
        if not message.argument:
            await bot.answer_message("Usage: /todo_add <text>")
            return

        try:
            item = await todo_service.add(
                chat_id=_chat_id(message),
                text=message.argument,
            )
        except TodoValidationError as exc:
            await bot.answer_message(str(exc))
            return

        await bot.answer_message(f"Added: {item.id}. {item.text}")

    @collector.command("/todo_list", description="Show todo list")
    async def todo_list_handler(message: IncomingMessage, bot: Bot) -> None:
        items = await todo_service.list(chat_id=_chat_id(message))
        await bot.answer_message(_format_list(items))

    @collector.command("/todo_done", description="Mark todo as done")
    async def todo_done_handler(message: IncomingMessage, bot: Bot) -> None:
        todo_id = _parse_id(message.argument)
        if todo_id is None:
            await bot.answer_message("Usage: /todo_done <id>")
            return

        try:
            item = await todo_service.mark_done(
                chat_id=_chat_id(message),
                todo_id=todo_id,
            )
        except TodoNotFoundError as exc:
            await bot.answer_message(str(exc))
            return

        await bot.answer_message(f"Done: {item.id}. {item.text}")

    @collector.command("/todo_delete", description="Delete todo item")
    async def todo_delete_handler(message: IncomingMessage, bot: Bot) -> None:
        todo_id = _parse_id(message.argument)
        if todo_id is None:
            await bot.answer_message("Usage: /todo_delete <id>")
            return

        try:
            await todo_service.delete(
                chat_id=_chat_id(message),
                todo_id=todo_id,
            )
        except TodoNotFoundError as exc:
            await bot.answer_message(str(exc))
            return

        await bot.answer_message(f"Deleted: {todo_id}")

    @collector.command("/todo_clear", description="Clear todo list")
    async def todo_clear_handler(message: IncomingMessage, bot: Bot) -> None:
        count = await todo_service.clear(chat_id=_chat_id(message))
        await bot.answer_message(f"Cleared {count} items.")

    @collector.command("/todo_help", description="Show help")
    async def todo_help_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.answer_message(_help_text())

    @collector.command("/todo_widget_single", description="Update single widget")
    async def todo_widget_single_handler(message: IncomingMessage, bot: Bot) -> None:
        try:
            await bot.update_widget(widget=single_widget, message=message)
        except InvalidWidgetPayloadError as exc:
            await bot.answer_message(str(exc))

    @collector.command("/todo_widget_multi", description="Update multi widget")
    async def todo_widget_multi_handler(message: IncomingMessage, bot: Bot) -> None:
        try:
            await bot.update_widget(widget=multi_widget, message=message, max_concurrency=3)
        except InvalidWidgetPayloadError as exc:
            await bot.answer_message(str(exc))

    register_demo_handlers(
        collector,
        todo_service=todo_service,
        attachment_factory=attachment_factory,
        single_widget=single_widget,
        multi_widget=multi_widget,
        session_single_widget=session_single_widget,
        session_multi_widget=session_multi_widget,
        single_session=single_session,
        multi_session=multi_session,
        demo_enabled=demo_enabled,
        allow_risky=demo_allow_risky,
    )

    return collector


def _chat_id(message: IncomingMessage) -> UUID:
    return message.chat.id


def _parse_id(raw: str) -> int | None:
    cleaned = raw.strip()
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _format_list(items: Sequence[TodoItem]) -> str:
    if not items:
        return "Todo list is empty. Use /todo_add <text>."

    lines = ["Todo list:"]
    for item in items:
        status = "[x]" if item.is_done else "[ ]"
        lines.append(f"{item.id}. {status} {item.text}")
    return "\n".join(lines)


def _help_text() -> str:
    return "\n".join(
        [
            "Todo bot commands:",
            "/todo_add <text> - add a task",
            "/todo_list - show tasks",
            "/todo_done <id> - mark task as done",
            "/todo_delete <id> - delete task",
            "/todo_clear - clear tasks",
            "/todo_help - show help",
        ],
    )
