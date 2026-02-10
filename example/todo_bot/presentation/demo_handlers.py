from __future__ import annotations

from collections.abc import Sequence
from io import BytesIO
from pathlib import Path
import tempfile
from uuid import UUID

from pybotx import (
    Bot,
    ChatLinkTypes,
    ChatTypes,
    EditMessageBuilder,
    HandlerCollector,
    IncomingMessage,
    MessageOptions,
    OutgoingMessageBuilder,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
    TextBuilder,
    WidgetSession,
    build_bot_command_link,
)
from pybotx.domain.errors import InvalidWidgetPayloadError
from pybotx.domain.ports.async_buffer import AsyncBufferReadable, AsyncBufferWritable
from pybotx.domain.widgets import MultiMessageWidget, SingleMessageWidget
from pybotx.infrastructure.services.attachment_factory import AttachmentFactory

from example.todo_bot.application.services import TodoService
from example.todo_bot.domain.models import TodoItem


class _MemoryAsyncBuffer(AsyncBufferReadable, AsyncBufferWritable):
    def __init__(self, initial: bytes = b"") -> None:
        self._buf = bytearray(initial)
        self._pos = 0

    async def read(self, bytes_to_read: int | None = None) -> bytes:
        if bytes_to_read is None:
            data = bytes(self._buf[self._pos :])
            self._pos = len(self._buf)
            return data
        data = bytes(self._buf[self._pos : self._pos + bytes_to_read])
        self._pos += len(data)
        return data

    async def write(self, content: bytes) -> int:
        end_pos = self._pos + len(content)
        if end_pos > len(self._buf):
            self._buf.extend(b"\x00" * (end_pos - len(self._buf)))
        self._buf[self._pos : end_pos] = content
        self._pos = end_pos
        return len(content)

    async def seek(self, cursor: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = max(0, cursor)
        elif whence == 1:
            self._pos = max(0, self._pos + cursor)
        elif whence == 2:
            self._pos = max(0, len(self._buf) + cursor)
        else:
            raise ValueError("Invalid whence")
        return self._pos

    async def tell(self) -> int:
        return self._pos


def register_demo_handlers(
    collector: HandlerCollector,
    *,
    todo_service: TodoService,
    attachment_factory: AttachmentFactory,
    single_widget: SingleMessageWidget,
    multi_widget: MultiMessageWidget,
    session_single_widget: SingleMessageWidget,
    session_multi_widget: MultiMessageWidget,
    single_session: WidgetSession,
    multi_session: WidgetSession,
    demo_enabled: bool,
    allow_risky: bool,
) -> None:
    if not demo_enabled:
        @collector.command("/demo_help", description="Show demo commands")
        async def demo_help_disabled_handler(message: IncomingMessage, bot: Bot) -> None:
            await bot.answer_message("Demo commands are disabled by config")

        return

    safe_commands = [
        "/demo_help - show demo commands",
        "/demo_reply - reply to incoming message",
        "/demo_edit - edit source or replied message",
        "/demo_status <sync_id> - get message status",
        "/demo_typing - send typing events",
        "/demo_bot_token - get bot token",
        "/demo_bots_list - list bots",
        "/demo_bot_command_link [command] - build bot command link",
        "/demo_list_chats - list chats",
        "/demo_chat_info [chat_id] - chat info",
        "/demo_personal_chat <huid> - personal chat info",
        "/demo_users_email <email> - search user by email",
        "/demo_users_emails <email1,email2> - search users by emails",
        "/demo_users_huid <huid> - search user by huid",
        "/demo_users_other_id <id> - search user by other id",
        "/demo_users_ad <login> <domain> - search user by AD",
        "/demo_sticker_packs - list sticker packs",
        "/demo_sticker_pack <pack_id> - get sticker pack",
        "/demo_sticker <pack_id> <sticker_id> - get sticker",
        "/demo_widget_single - send single widget",
        "/demo_widget_multi - send multi widget",
        "/demo_widget_session_single - send session single widget",
        "/demo_widget_session_multi - send session multi widget",
    ]
    risky_commands = [
        "/demo_send - send outgoing message",
        "/demo_send_sync - send sync message",
        "/demo_bulk_send - bulk send messages",
        "/demo_openid_refresh - refresh OpenID token",
        "/demo_metrics - collect metric",
        "/demo_users_csv - stream users list",
        "/demo_user_update <public_name> - update user profile",
        "/demo_smartapps_list - list smartapps",
        "/demo_smartapp_event - send smartapp event",
        "/demo_smartapp_notification - send smartapp notification",
        "/demo_smartapp_custom - send smartapp custom notification",
        "/demo_smartapp_unread - send smartapp unread counter",
        "/demo_smartapp_manifest - send smartapp manifest",
        "/demo_upload_static - upload static file",
        "/demo_files_upload - upload file",
        "/demo_files_download <file_id> [chat_id] - download file",
        "/demo_attachment_factory - send attachment built by factory",
        "/demo_attachment_from_path - send attachment from file path",
        "/demo_attachment_from_file - send attachment from file object",
        "/demo_files_download_url <url> - download URL",
        "/demo_ensure_personal_chat <huid> - ensure personal chat",
        "/demo_create_chat [name] - create group chat",
        "/demo_chat_link <chat_id> [type] - create chat invite link",
        "/demo_add_users <chat_id> <huid1,huid2> - add users to chat",
        "/demo_remove_users <chat_id> <huid1,huid2> - remove users from chat",
        "/demo_promote_admins <chat_id> <huid1,huid2> - promote chat admins",
        "/demo_create_thread <sync_id> - create thread",
        "/demo_pin <sync_id> - pin message",
        "/demo_unpin [chat_id] - unpin message",
        "/demo_enable_stealth [chat_id] - enable stealth mode",
        "/demo_disable_stealth [chat_id] - disable stealth mode",
        "/demo_sticker_pack_create <name> - create sticker pack",
        "/demo_sticker_add <pack_id> <emoji> - add sticker",
        "/demo_sticker_delete <pack_id> <sticker_id> - delete sticker",
        "/demo_sticker_pack_delete <pack_id> - delete sticker pack",
        "/demo_sticker_pack_edit <pack_id> <name> <preview_id> <sticker_ids...> - edit pack",
    ]

    @collector.command("/demo_help", description="Show demo commands")
    async def demo_help_handler(message: IncomingMessage, bot: Bot) -> None:
        lines = ["Demo commands:"]
        lines.extend(safe_commands)
        if allow_risky:
            lines.extend(risky_commands)
        else:
            lines.append("Risky demo commands are disabled by config.")
        await bot.answer_message("\n".join(lines))

    async def _risky_disabled(message: IncomingMessage, bot: Bot) -> None:
        await bot.answer_message(
            "Demo risky commands are disabled by config. "
            "Set TODO_DEMO_ALLOW_RISKY=true to enable.",
        )

    def _register_risky(
        command: str,
        description: str,
    ):
        def _decorator(handler):
            if allow_risky:
                return collector.command(command, description=description)(handler)
            collector.command(command, description=f"{description} (disabled)")(
                _risky_disabled,
            )
            return handler

        return _decorator

    @collector.command("/demo_reply", description="Reply to incoming message (events)")
    async def demo_reply_handler(message: IncomingMessage, bot: Bot) -> None:
        text = TextBuilder().append("Reply via reply_to: ").mention_user(
            message.sender.huid,
            message.sender.username,
        )
        await bot.reply_to(
            message,
            body=text.build(),
            options=MessageOptions(silent_response=True),
        )

    @collector.command("/demo_edit", description="Edit source message (events)")
    async def demo_edit_handler(message: IncomingMessage, bot: Bot) -> None:
        builder: EditMessageBuilder | None = None
        try:
            builder = EditMessageBuilder.for_incoming_source_id(message)
        except ValueError:
            builder = None

        if builder is None and message.reply is not None:
            builder = EditMessageBuilder.for_incoming_source(
                message,
                sync_id=message.reply.sync_id,
            )

        if builder is None:
            await bot.answer_message(
                "Cannot edit: source_sync_id is missing. "
                "Reply to a bot message or use a widget action, then call /demo_edit.",
            )
            return

        edit = builder.with_body("Edited by /demo_edit").build()
        await bot.edit(message=edit)

    @collector.command("/demo_status", description="Get message status (events)")
    async def demo_status_handler(message: IncomingMessage, bot: Bot) -> None:
        sync_id = _parse_uuid(message.argument)
        if sync_id is None:
            await bot.answer_message("Usage: /demo_status <sync_id>")
            return
        status = await bot.get_message_status(bot_id=message.bot.id, sync_id=sync_id)
        await bot.answer_message(f"Status: {status.status}")

    @collector.command("/demo_typing", description="Send typing events")
    async def demo_typing_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.start_typing(bot_id=message.bot.id, chat_id=message.chat.id)
        await bot.stop_typing(bot_id=message.bot.id, chat_id=message.chat.id)
        await bot.answer_message("Typing events sent")

    @collector.command("/demo_bot_token", description="Get bot token (bots api)")
    async def demo_bot_token_handler(message: IncomingMessage, bot: Bot) -> None:
        token = await bot.get_token(bot_id=message.bot.id)
        await bot.answer_message(f"Token length: {len(token)}")

    @collector.command("/demo_bots_list", description="Get bots list (bots api)")
    async def demo_bots_list_handler(message: IncomingMessage, bot: Bot) -> None:
        bots, generated_at = await bot.get_bots_list(bot_id=message.bot.id)
        await bot.answer_message(f"Bots: {len(bots)} (generated at {generated_at})")

    @collector.command("/demo_bot_command_link", description="Build bot command link")
    async def demo_bot_command_link_handler(message: IncomingMessage, bot: Bot) -> None:
        command = message.argument.strip() if message.argument else "/start"
        link = build_bot_command_link(
            huid=message.bot.id,
            command=command,
            body=command,
        )
        await bot.answer_message(f"Bot command link: {link}")

    @collector.command("/demo_list_chats", description="List chats (chats)")
    async def demo_list_chats_handler(message: IncomingMessage, bot: Bot) -> None:
        chats = await bot.list_chats(bot_id=message.bot.id)
        await bot.answer_message(f"Chats count: {len(chats)}")

    @collector.command("/demo_chat_info", description="Chat info (chats)")
    async def demo_chat_info_handler(message: IncomingMessage, bot: Bot) -> None:
        chat_id = _parse_uuid(message.argument) or message.chat.id
        info = await bot.chat_info(bot_id=message.bot.id, chat_id=chat_id)
        await bot.answer_message(f"Chat: {info.chat_id} ({info.chat_type})")

    @collector.command("/demo_personal_chat", description="Get personal chat (chats)")
    async def demo_personal_chat_handler(message: IncomingMessage, bot: Bot) -> None:
        huid = _parse_uuid(message.argument)
        if huid is None:
            await bot.answer_message("Usage: /demo_personal_chat <huid>")
            return
        info = await bot.personal_chat(bot_id=message.bot.id, user_huid=huid)
        await bot.answer_message(f"Personal chat: {info.chat_id}")

    @collector.command("/demo_users_email", description="Find user by email (users)")
    async def demo_users_email_handler(message: IncomingMessage, bot: Bot) -> None:
        if not message.argument:
            await bot.answer_message("Usage: /demo_users_email <email>")
            return
        user = await bot.search_user_by_email_post(
            bot_id=message.bot.id,
            email=message.argument,
        )
        await bot.answer_message(f"User: {user.huid} {user.username}")

    @collector.command("/demo_users_emails", description="Find users by emails (users)")
    async def demo_users_emails_handler(message: IncomingMessage, bot: Bot) -> None:
        emails = _parse_list(message.argument)
        if not emails:
            await bot.answer_message("Usage: /demo_users_emails <email1,email2>")
            return
        users = await bot.search_user_by_emails(bot_id=message.bot.id, emails=emails)
        await bot.answer_message(f"Users: {len(users)}")

    @collector.command("/demo_users_huid", description="Find user by huid (users)")
    async def demo_users_huid_handler(message: IncomingMessage, bot: Bot) -> None:
        huid = _parse_uuid(message.argument)
        if huid is None:
            await bot.answer_message("Usage: /demo_users_huid <huid>")
            return
        user = await bot.search_user_by_huid(bot_id=message.bot.id, huid=huid)
        await bot.answer_message(f"User: {user.huid} {user.username}")

    @collector.command("/demo_users_other_id", description="Find user by other id (users)")
    async def demo_users_other_id_handler(message: IncomingMessage, bot: Bot) -> None:
        other_id = message.argument.strip()
        if not other_id:
            await bot.answer_message("Usage: /demo_users_other_id <id>")
            return
        user = await bot.search_user_by_other_id(bot_id=message.bot.id, other_id=other_id)
        await bot.answer_message(f"User: {user.huid} {user.username}")

    @collector.command("/demo_users_ad", description="Find user by AD (users)")
    async def demo_users_ad_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 2:
            await bot.answer_message("Usage: /demo_users_ad <login> <domain>")
            return
        user = await bot.search_user_by_ad(
            bot_id=message.bot.id,
            ad_login=parts[0],
            ad_domain=parts[1],
        )
        await bot.answer_message(f"User: {user.huid} {user.username}")

    @_register_risky("/demo_send", "Send outgoing message (notifications)")
    async def demo_send_handler(message: IncomingMessage, bot: Bot) -> None:
        outgoing = (
            OutgoingMessageBuilder(
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                body="Hello from OutgoingMessageBuilder",
            )
            .silent()
            .auto_adjust_buttons()
            .build()
        )
        await bot.send(message=outgoing)

    @_register_risky("/demo_send_sync", "Send sync message (notifications)")
    async def demo_send_sync_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.send_message_sync(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body="Hello from send_message_sync",
        )

    @_register_risky("/demo_bulk_send", "Bulk send (notifications)")
    async def demo_bulk_send_handler(message: IncomingMessage, bot: Bot) -> None:
        messages = [
            OutgoingMessageBuilder(
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                body="Bulk message 1",
            ).build(),
            OutgoingMessageBuilder(
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                body="Bulk message 2",
            ).build(),
        ]
        result = await bot.bulk_send(messages=messages, max_concurrency=2)
        await bot.answer_message(
            f"Bulk send: {len(result.successes)} ok, {len(result.failures)} failed",
        )

    @_register_risky("/demo_users_csv", "Stream users list (users)")
    async def demo_users_csv_handler(message: IncomingMessage, bot: Bot) -> None:
        total = 0
        async with bot.users_as_csv(bot_id=message.bot.id) as users:
            async for user in users:
                total += 1
                if total >= 5:
                    break
        await bot.answer_message(f"Users sampled: {total}")

    @_register_risky("/demo_user_update", "Update user profile (users)")
    async def demo_user_update_handler(message: IncomingMessage, bot: Bot) -> None:
        public_name = message.argument.strip()
        if not public_name:
            await bot.answer_message("Usage: /demo_user_update <public_name>")
            return
        await bot.update_user_profile(
            bot_id=message.bot.id,
            user_huid=message.sender.huid,
            public_name=public_name,
        )
        await bot.answer_message("Profile updated")

    @_register_risky("/demo_openid_refresh", "Refresh OpenID token")
    async def demo_openid_refresh_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.refresh_access_token(bot_id=message.bot.id, huid=message.sender.huid)
        await bot.answer_message("OpenID refresh sent")

    @_register_risky("/demo_metrics", "Collect metric (metrics)")
    async def demo_metrics_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.collect_metric(
            bot_id=message.bot.id,
            bot_function="demo_metrics",
            huids=[message.sender.huid],
            chat_id=message.chat.id,
        )
        await bot.answer_message("Metric collected")

    @_register_risky("/demo_smartapps_list", "List smartapps")
    async def demo_smartapps_list_handler(message: IncomingMessage, bot: Bot) -> None:
        apps, version = await bot.get_smartapps_list(bot_id=message.bot.id)
        await bot.answer_message(f"SmartApps: {len(apps)} (version {version})")

    @_register_risky("/demo_smartapp_event", "Send smartapp event")
    async def demo_smartapp_event_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.send_smartapp_event(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            data={"type": "ping", "text": "hello"},
            encrypted=False,
        )
        await bot.answer_message("SmartApp event sent")

    @_register_risky("/demo_smartapp_notification", "Send smartapp notification")
    async def demo_smartapp_notification_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.send_smartapp_notification(
            message.bot.id,
            message.chat.id,
            smartapp_counter=1,
            body="SmartApp notification",
        )
        await bot.answer_message("SmartApp notification sent")

    @_register_risky("/demo_smartapp_custom", "Send smartapp custom notification")
    async def demo_smartapp_custom_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.send_smartapp_custom_notification(
            bot_id=message.bot.id,
            group_chat_id=message.chat.id,
            title="SmartApp title",
            body="SmartApp custom notification",
        )
        await bot.answer_message("SmartApp custom notification sent")

    @_register_risky("/demo_smartapp_unread", "Send smartapp unread counter")
    async def demo_smartapp_unread_handler(message: IncomingMessage, bot: Bot) -> None:
        await bot.send_smartapp_unread_counter(
            bot_id=message.bot.id,
            group_chat_id=message.chat.id,
            counter=1,
        )
        await bot.answer_message("SmartApp unread counter sent")

    @_register_risky("/demo_smartapp_manifest", "Send smartapp manifest")
    async def demo_smartapp_manifest_handler(message: IncomingMessage, bot: Bot) -> None:
        manifest = await bot.send_smartapp_manifest(
            bot_id=message.bot.id,
            web_layout=SmartappManifestWebParams(),
            unread_counter=SmartappManifestUnreadCounterParams(
                user_huid=[message.sender.huid],
                group_chat_id=[message.chat.id],
            ),
        )
        await bot.answer_message(
            f"SmartApp manifest set: web={manifest.web.default_layout}",
        )

    @_register_risky("/demo_upload_static", "Upload static file (smartapps)")
    async def demo_upload_static_handler(message: IncomingMessage, bot: Bot) -> None:
        buffer = _MemoryAsyncBuffer(b"hello")
        link = await bot.upload_static_file(
            bot_id=message.bot.id,
            async_buffer=buffer,
            filename="hello.txt",
        )
        await bot.answer_message(f"Static file link: {link}")

    @_register_risky("/demo_files_upload", "Upload file (files)")
    async def demo_files_upload_handler(message: IncomingMessage, bot: Bot) -> None:
        buffer = _MemoryAsyncBuffer(b"demo file")
        file = await bot.upload_file(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            async_buffer=buffer,
            filename="demo.txt",
        )
        await bot.answer_message(f"Uploaded file: {file.filename}, size {file.size}")

    @_register_risky("/demo_files_download", "Download file (files)")
    async def demo_files_download_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if not parts:
            await bot.answer_message("Usage: /demo_files_download <file_id> [chat_id]")
            return
        file_id = _parse_uuid(parts[0])
        if file_id is None:
            await bot.answer_message("Invalid file_id")
            return
        chat_id = _parse_uuid(parts[1]) if len(parts) > 1 else message.chat.id
        if chat_id is None:
            await bot.answer_message("Invalid chat_id")
            return
        buffer = _MemoryAsyncBuffer()
        await bot.download_file(
            bot_id=message.bot.id,
            chat_id=chat_id,
            file_id=file_id,
            async_buffer=buffer,
        )
        await buffer.seek(0)
        content = await buffer.read()
        await bot.answer_message(f"Downloaded file bytes: {len(content)}")

    @_register_risky("/demo_attachment_factory", "Send attachment via factory")
    async def demo_attachment_factory_handler(message: IncomingMessage, bot: Bot) -> None:
        attachment = await attachment_factory.from_bytes(
            b"hello from attachment factory",
            filename="hello.txt",
        )
        outgoing = (
            OutgoingMessageBuilder(
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                body="Attachment from factory",
            )
            .with_file(attachment)
            .build()
        )
        await bot.send(message=outgoing)

    @_register_risky("/demo_attachment_from_path", "Send attachment from path")
    async def demo_attachment_from_path_handler(message: IncomingMessage, bot: Bot) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "demo_from_path.txt"
            file_path.write_bytes(b"hello from attachment factory path")
            attachment = await attachment_factory.from_path(file_path)
        outgoing = (
            OutgoingMessageBuilder(
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                body="Attachment from path",
            )
            .with_file(attachment)
            .build()
        )
        await bot.send(message=outgoing)

    @_register_risky("/demo_attachment_from_file", "Send attachment from file object")
    async def demo_attachment_from_file_handler(message: IncomingMessage, bot: Bot) -> None:
        buffer = BytesIO(b"hello from attachment factory file")
        attachment = await attachment_factory.from_file(buffer, filename="demo_from_file.txt")
        outgoing = (
            OutgoingMessageBuilder(
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                body="Attachment from file object",
            )
            .with_file(attachment)
            .build()
        )
        await bot.send(message=outgoing)

    @_register_risky("/demo_files_download_url", "Download URL (files)")
    async def demo_files_download_url_handler(message: IncomingMessage, bot: Bot) -> None:
        if not message.argument:
            await bot.answer_message("Usage: /demo_files_download_url <url>")
            return
        buffer = _MemoryAsyncBuffer()
        await bot.download_url(url=message.argument, async_buffer=buffer)
        await buffer.seek(0)
        content = await buffer.read()
        await bot.answer_message(f"Downloaded {len(content)} bytes")

    @collector.command("/demo_sticker_packs", description="List sticker packs")
    async def demo_sticker_packs_handler(message: IncomingMessage, bot: Bot) -> None:
        packs = []
        async for pack in bot.iterate_by_sticker_packs(
            bot_id=message.bot.id,
            user_huid=message.sender.huid,
        ):
            packs.append(pack)
            if len(packs) >= 3:
                break
        await bot.answer_message(f"Sticker packs: {len(packs)}")

    @collector.command("/demo_sticker_pack", description="Get sticker pack")
    async def demo_sticker_pack_handler(message: IncomingMessage, bot: Bot) -> None:
        pack_id = _parse_uuid(message.argument)
        if pack_id is None:
            await bot.answer_message("Usage: /demo_sticker_pack <pack_id>")
            return
        pack = await bot.get_sticker_pack(bot_id=message.bot.id, sticker_pack_id=pack_id)
        await bot.answer_message(f"Sticker pack: {pack.id} ({pack.name})")

    @collector.command("/demo_sticker", description="Get sticker")
    async def demo_sticker_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 2:
            await bot.answer_message("Usage: /demo_sticker <pack_id> <sticker_id>")
            return
        pack_id = _parse_uuid(parts[0])
        sticker_id = _parse_uuid(parts[1])
        if pack_id is None or sticker_id is None:
            await bot.answer_message("Invalid pack_id or sticker_id")
            return
        sticker = await bot.get_sticker(
            bot_id=message.bot.id,
            sticker_pack_id=pack_id,
            sticker_id=sticker_id,
        )
        await bot.answer_message(f"Sticker: {sticker.id} ({sticker.emoji})")

    @_register_risky("/demo_sticker_pack_create", "Create sticker pack")
    async def demo_sticker_pack_create_handler(message: IncomingMessage, bot: Bot) -> None:
        name = message.argument.strip() if message.argument else ""
        if not name:
            await bot.answer_message("Usage: /demo_sticker_pack_create <name>")
            return
        pack = await bot.create_sticker_pack(
            bot_id=message.bot.id,
            name=name,
            huid=message.sender.huid,
        )
        await bot.answer_message(f"Sticker pack created: {pack.id}")

    @_register_risky("/demo_sticker_add", "Add sticker to pack")
    async def demo_sticker_add_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 2:
            await bot.answer_message("Usage: /demo_sticker_add <pack_id> <emoji>")
            return
        pack_id = _parse_uuid(parts[0])
        if pack_id is None:
            await bot.answer_message("Invalid pack_id")
            return
        buffer = _MemoryAsyncBuffer(_small_png_bytes())
        sticker = await bot.add_sticker(
            bot_id=message.bot.id,
            sticker_pack_id=pack_id,
            emoji=parts[1],
            async_buffer=buffer,
        )
        await bot.answer_message(f"Sticker added: {sticker.id}")

    @_register_risky("/demo_sticker_delete", "Delete sticker from pack")
    async def demo_sticker_delete_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 2:
            await bot.answer_message("Usage: /demo_sticker_delete <pack_id> <sticker_id>")
            return
        pack_id = _parse_uuid(parts[0])
        sticker_id = _parse_uuid(parts[1])
        if pack_id is None or sticker_id is None:
            await bot.answer_message("Invalid pack_id or sticker_id")
            return
        await bot.delete_sticker(
            bot_id=message.bot.id,
            sticker_pack_id=pack_id,
            sticker_id=sticker_id,
        )
        await bot.answer_message("Sticker deleted")

    @_register_risky("/demo_sticker_pack_delete", "Delete sticker pack")
    async def demo_sticker_pack_delete_handler(message: IncomingMessage, bot: Bot) -> None:
        pack_id = _parse_uuid(message.argument)
        if pack_id is None:
            await bot.answer_message("Usage: /demo_sticker_pack_delete <pack_id>")
            return
        await bot.delete_sticker_pack(bot_id=message.bot.id, sticker_pack_id=pack_id)
        await bot.answer_message("Sticker pack deleted")

    @_register_risky("/demo_sticker_pack_edit", "Edit sticker pack")
    async def demo_sticker_pack_edit_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 4:
            await bot.answer_message(
                "Usage: /demo_sticker_pack_edit <pack_id> <name> <preview_id> <sticker_ids...>",
            )
            return
        pack_id = _parse_uuid(parts[0])
        preview_id = _parse_uuid(parts[2])
        if pack_id is None or preview_id is None:
            await bot.answer_message("Invalid pack_id or preview_id")
            return
        stickers = _parse_uuid_list(parts[3:])
        if not stickers:
            await bot.answer_message("Invalid sticker ids")
            return
        pack = await bot.edit_sticker_pack(
            bot_id=message.bot.id,
            sticker_pack_id=pack_id,
            name=parts[1],
            preview=preview_id,
            stickers_order=stickers,
        )
        await bot.answer_message(f"Sticker pack updated: {pack.id}")

    @collector.command("/demo_widget_single", description="Send single widget")
    async def demo_widget_single_handler(message: IncomingMessage, bot: Bot) -> None:
        items = _todo_texts(await todo_service.list(chat_id=message.chat.id))
        if not items:
            items = ["Empty list"]
        await bot.send_single_widget(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            widget=single_widget,
            elems=items,
        )

    @collector.command("/demo_widget_multi", description="Send multi widget")
    async def demo_widget_multi_handler(message: IncomingMessage, bot: Bot) -> None:
        items = _todo_texts(await todo_service.list(chat_id=message.chat.id))
        if not items:
            items = ["Empty list"]
        await bot.send_multi_widget(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            widget=multi_widget,
            elems=items,
        )

    @collector.command("/demo_widget_session_single", description="Send session widget")
    async def demo_widget_session_single_handler(message: IncomingMessage, bot: Bot) -> None:
        items = _todo_texts(await todo_service.list(chat_id=message.chat.id))
        if not items:
            items = ["Empty list"]
        session = bot.widget_session(widget=session_single_widget, ttl_seconds=3600)
        await session.send_single(
            bot=bot,
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            elems=items,
        )

    @collector.command("/demo_widget_session_multi", description="Send session multi widget")
    async def demo_widget_session_multi_handler(message: IncomingMessage, bot: Bot) -> None:
        items = _todo_texts(await todo_service.list(chat_id=message.chat.id))
        if not items:
            items = ["Empty list"]
        session = bot.widget_session(widget=session_multi_widget, ttl_seconds=3600)
        await session.send_multi(
            bot=bot,
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            elems=items,
        )

    @_register_risky("/demo_ensure_personal_chat", "Ensure personal chat (chats)")
    async def demo_ensure_personal_chat_handler(message: IncomingMessage, bot: Bot) -> None:
        huid = _parse_uuid(message.argument)
        if huid is None:
            await bot.answer_message("Usage: /demo_ensure_personal_chat <huid>")
            return
        info = await bot.ensure_personal_chat(bot_id=message.bot.id, user_huid=huid)
        await bot.answer_message(f"Personal chat: {info.chat_id}")

    @_register_risky("/demo_create_chat", "Create group chat (chats)")
    async def demo_create_chat_handler(message: IncomingMessage, bot: Bot) -> None:
        name = message.argument.strip() if message.argument else "Demo chat"
        chat_id = await bot.create_chat(
            bot_id=message.bot.id,
            name=name,
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[message.sender.huid],
        )
        await bot.answer_message(f"Chat created: {chat_id}")

    @_register_risky("/demo_chat_link", "Create chat link (chats)")
    async def demo_chat_link_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if not parts:
            await bot.answer_message("Usage: /demo_chat_link <chat_id> [type]")
            return
        chat_id = _parse_uuid(parts[0])
        if chat_id is None:
            await bot.answer_message("Invalid chat_id")
            return
        link_type = ChatLinkTypes.PUBLIC
        if len(parts) > 1:
            try:
                link_type = ChatLinkTypes(parts[1])
            except ValueError:
                await bot.answer_message("Invalid link type. Use public/trusts/corporate/server")
                return
        link = await bot.create_chat_link(
            bot_id=message.bot.id,
            chat_id=chat_id,
            link_type=link_type,
        )
        await bot.answer_message(f"Chat link: {link.link}")

    @_register_risky("/demo_add_users", "Add users to chat (chats)")
    async def demo_add_users_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 2:
            await bot.answer_message("Usage: /demo_add_users <chat_id> <huid1,huid2>")
            return
        chat_id = _parse_uuid(parts[0])
        huids = _parse_uuid_list(parts[1:])
        if chat_id is None or not huids:
            await bot.answer_message("Invalid chat_id or huids")
            return
        await bot.add_users_to_chat(bot_id=message.bot.id, chat_id=chat_id, huids=huids)
        await bot.answer_message(f"Added {len(huids)} users")

    @_register_risky("/demo_remove_users", "Remove users from chat (chats)")
    async def demo_remove_users_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 2:
            await bot.answer_message("Usage: /demo_remove_users <chat_id> <huid1,huid2>")
            return
        chat_id = _parse_uuid(parts[0])
        huids = _parse_uuid_list(parts[1:])
        if chat_id is None or not huids:
            await bot.answer_message("Invalid chat_id or huids")
            return
        await bot.remove_users_from_chat(
            bot_id=message.bot.id,
            chat_id=chat_id,
            huids=huids,
        )
        await bot.answer_message(f"Removed {len(huids)} users")

    @_register_risky("/demo_promote_admins", "Promote admins (chats)")
    async def demo_promote_admins_handler(message: IncomingMessage, bot: Bot) -> None:
        parts = _parse_list(message.argument)
        if len(parts) < 2:
            await bot.answer_message("Usage: /demo_promote_admins <chat_id> <huid1,huid2>")
            return
        chat_id = _parse_uuid(parts[0])
        huids = _parse_uuid_list(parts[1:])
        if chat_id is None or not huids:
            await bot.answer_message("Invalid chat_id or huids")
            return
        await bot.promote_to_chat_admins(
            bot_id=message.bot.id,
            chat_id=chat_id,
            huids=huids,
        )
        await bot.answer_message(f"Promoted {len(huids)} users")

    @_register_risky("/demo_create_thread", "Create thread (chats)")
    async def demo_create_thread_handler(message: IncomingMessage, bot: Bot) -> None:
        sync_id = _parse_uuid(message.argument)
        if sync_id is None:
            await bot.answer_message("Usage: /demo_create_thread <sync_id>")
            return
        thread_id = await bot.create_thread(bot_id=message.bot.id, sync_id=sync_id)
        await bot.answer_message(f"Thread created: {thread_id}")

    @_register_risky("/demo_pin", "Pin message (chats)")
    async def demo_pin_handler(message: IncomingMessage, bot: Bot) -> None:
        sync_id = _parse_uuid(message.argument)
        if sync_id is None:
            await bot.answer_message("Usage: /demo_pin <sync_id>")
            return
        await bot.pin_message(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            sync_id=sync_id,
        )
        await bot.answer_message("Message pinned")

    @_register_risky("/demo_unpin", "Unpin message (chats)")
    async def demo_unpin_handler(message: IncomingMessage, bot: Bot) -> None:
        chat_id = _parse_uuid(message.argument) if message.argument else message.chat.id
        if chat_id is None:
            await bot.answer_message("Usage: /demo_unpin [chat_id]")
            return
        await bot.unpin_message(bot_id=message.bot.id, chat_id=chat_id)
        await bot.answer_message("Message unpinned")

    @_register_risky("/demo_enable_stealth", "Enable stealth mode (chats)")
    async def demo_enable_stealth_handler(message: IncomingMessage, bot: Bot) -> None:
        chat_id = _parse_uuid(message.argument) if message.argument else message.chat.id
        if chat_id is None:
            await bot.answer_message("Usage: /demo_enable_stealth [chat_id]")
            return
        await bot.enable_stealth(bot_id=message.bot.id, chat_id=chat_id)
        await bot.answer_message("Stealth enabled")

    @_register_risky("/demo_disable_stealth", "Disable stealth mode (chats)")
    async def demo_disable_stealth_handler(message: IncomingMessage, bot: Bot) -> None:
        chat_id = _parse_uuid(message.argument) if message.argument else message.chat.id
        if chat_id is None:
            await bot.answer_message("Usage: /demo_disable_stealth [chat_id]")
            return
        await bot.disable_stealth(bot_id=message.bot.id, chat_id=chat_id)
        await bot.answer_message("Stealth disabled")

    @collector.command("/todo_widget_session_single", description="Update session widget")
    async def todo_widget_session_single_handler(message: IncomingMessage, bot: Bot) -> None:
        try:
            await single_session.update(bot=bot, message=message, diff=True)
        except InvalidWidgetPayloadError as exc:
            await bot.answer_message(str(exc))

    @collector.command("/todo_widget_session_multi", description="Update session multi widget")
    async def todo_widget_session_multi_handler(message: IncomingMessage, bot: Bot) -> None:
        try:
            await multi_session.update(bot=bot, message=message, diff=True, max_concurrency=3)
        except InvalidWidgetPayloadError as exc:
            await bot.answer_message(str(exc))


def _parse_uuid(raw: str) -> UUID | None:
    cleaned = raw.strip()
    if not cleaned:
        return None
    try:
        return UUID(cleaned)
    except ValueError:
        return None


def _parse_list(raw: str) -> list[str]:
    if not raw:
        return []
    return [part for part in raw.replace(",", " ").split() if part]


def _parse_uuid_list(parts: Sequence[str]) -> list[UUID]:
    result: list[UUID] = []
    for part in parts:
        try:
            result.append(UUID(part))
        except ValueError:
            return []
    return result


def _small_png_bytes() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00"
        b"\x18\xdd\x8d\x18\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def _todo_texts(items: Sequence[TodoItem]) -> list[str]:
    return [f"{item.id}. {'[x]' if item.is_done else '[ ]'} {item.text}" for item in items]
