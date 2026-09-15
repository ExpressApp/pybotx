from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from pybotx.bot.bot import Bot
from pybotx.models.message.incoming_message import IncomingMessage
from pybotx.models.message.outgoing_message import OutgoingMessage

from .approval import ApprovalWidget
from .async_job import AsyncJobWidget
from .base import WidgetResultMode
from .calendar import CalendarWidget
from .carousel import CarouselWidget
from .checklist import CheckListWidget
from .checktable import CheckboxContent, ChecktableWidget
from .confirm import ConfirmWidget
from .date_range import DateRangeWidget
from .file_batch import BatchFileItem, FileBatchWidget
from .form_wizard import FormWizardStep, FormWizardWidget
from .markup import MessageMarkup
from .messages_pager import MessagesPagerWidget
from .multi_select import MultiSelectWidget
from .pagination import PaginationWidget
from .range import RangeWidget
from .search_select import SearchSelectWidget
from .select import SelectOption, SelectWidget
from .table import TableWidget


@dataclass(frozen=True, slots=True)
class WidgetContext:
    message: IncomingMessage
    bot: Bot
    command: str
    additional_markup: MessageMarkup | None = None
    result_mode: WidgetResultMode | None = None

    def as_widget_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "message": self.message,
            "bot": self.bot,
            "command": self.command,
        }
        if self.additional_markup is not None:
            kwargs["additional_markup"] = self.additional_markup
        if self.result_mode is not None:
            kwargs["result_mode"] = self.result_mode
        return kwargs


@dataclass(frozen=True, slots=True)
class WidgetDefaults:
    confirm_label: str = "Подтвердить"
    cancel_label: str = "Отмена"
    approve_label: str = "Согласовать"
    reject_label: str = "Отклонить"
    comment_label: str = "Комментарий"
    search_empty_label: str = "Ничего не найдено"
    selected_prefix: str = "• "


class WidgetFactory:
    def __init__(
        self,
        *,
        context: WidgetContext,
        defaults: WidgetDefaults | None = None,
    ) -> None:
        self._context = context
        self._defaults = defaults or WidgetDefaults()

    def confirm(
        self,
        *,
        label: str,
        confirm_label: str | None = None,
        cancel_label: str | None = None,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> ConfirmWidget:
        return ConfirmWidget(
            label=label,
            confirm_label=confirm_label or self._defaults.confirm_label,
            cancel_label=cancel_label or self._defaults.cancel_label,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def approval(
        self,
        *,
        label: str,
        approve_label: str | None = None,
        reject_label: str | None = None,
        comment_label: str | None = None,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> ApprovalWidget:
        return ApprovalWidget(
            label=label,
            approve_label=approve_label or self._defaults.approve_label,
            reject_label=reject_label or self._defaults.reject_label,
            comment_label=comment_label or self._defaults.comment_label,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def select(
        self,
        *,
        options: Sequence[str | SelectOption],
        label: str,
        selected_prefix: str | None = None,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> SelectWidget:
        return SelectWidget(
            options=list(options),
            label=label,
            selected_prefix=selected_prefix or self._defaults.selected_prefix,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def search_select(
        self,
        *,
        options: Sequence[str | SelectOption],
        label: str,
        page_size: int = 5,
        empty_label: str | None = None,
        selected_prefix: str | None = None,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> SearchSelectWidget:
        return SearchSelectWidget(
            options=list(options),
            label=label,
            page_size=page_size,
            empty_label=empty_label or self._defaults.search_empty_label,
            selected_prefix=selected_prefix or self._defaults.selected_prefix,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def multi_select(
        self,
        *,
        options: Sequence[str | SelectOption],
        label: str,
        max_selected: int | None = None,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> MultiSelectWidget:
        return MultiSelectWidget(
            options=list(options),
            label=label,
            max_selected=max_selected,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def form_wizard(
        self,
        *,
        steps: Sequence[FormWizardStep],
        label: str,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> FormWizardWidget:
        return FormWizardWidget(
            steps=list(steps),
            label=label,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def table(
        self,
        *,
        rows: Sequence[dict[str, Any]],
        columns: Sequence[str],
        label: str = "Таблица",
        page_size: int = 5,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> TableWidget:
        return TableWidget(
            rows=list(rows),
            columns=list(columns),
            label=label,
            page_size=page_size,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def calendar(
        self,
        *,
        start_date: date | None = None,
        end_date: date = date.max,
        include_past: bool = False,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> CalendarWidget:
        return CalendarWidget(
            start_date=start_date,
            end_date=end_date,
            include_past=include_past,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def range(
        self,
        *,
        elements: Sequence[str] | None = None,
        label_template: str = "Current element: {element}",
        forward_label: str = "Вперед",
        backward_label: str = "Назад",
        empty_body: str = "Список пуст",
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> RangeWidget:
        return RangeWidget(
            elements=elements,
            label_template=label_template,
            forward_label=forward_label,
            backward_label=backward_label,
            empty_body=empty_body,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def carousel(
        self,
        *,
        widget_content: Sequence[Any],
        label: str,
        start_from: int = 0,
        displayed_content_count: int = 3,
        control_labels: tuple[str, str] | None = None,
        inline: bool = True,
        loop: bool = True,
        show_numbers: bool = False,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> CarouselWidget:
        return CarouselWidget(
            widget_content=widget_content,
            label=label,
            start_from=start_from,
            displayed_content_count=displayed_content_count,
            control_labels=control_labels,
            inline=inline,
            loop=loop,
            show_numbers=show_numbers,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def pagination(
        self,
        *,
        widget_content: Sequence[OutgoingMessage | str],
        paginate_by: int,
        delay_between_messages: float = 0.5,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> PaginationWidget:
        return PaginationWidget(
            widget_content=list(widget_content),
            paginate_by=paginate_by,
            delay_between_messages=delay_between_messages,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def messages_pager(
        self,
        *,
        elements: Sequence[str],
        page_size: int,
        item_template: str = "Element: {element}",
        delay_between_messages: float = 0.5,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> MessagesPagerWidget:
        return MessagesPagerWidget(
            elements=elements,
            page_size=page_size,
            item_template=item_template,
            delay_between_messages=delay_between_messages,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def date_range(
        self,
        *,
        label: str = "Выбор периода",
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> DateRangeWidget:
        return DateRangeWidget(
            label=label,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def async_job(
        self,
        *,
        job_id: str,
        status: str,
        details: str = "",
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> AsyncJobWidget:
        return AsyncJobWidget(
            job_id=job_id,
            status=status,
            details=details,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def file_batch(
        self,
        *,
        files: Sequence[BatchFileItem | dict[str, Any] | str] | None,
        label: str = "Пакет файлов",
        page_size: int = 5,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> FileBatchWidget:
        normalized_files = None if files is None else list(files)
        return FileBatchWidget(
            files=normalized_files,
            label=label,
            page_size=page_size,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def checklist(
        self,
        *,
        widget_content: Sequence[Any],
        label: str,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> CheckListWidget:
        return CheckListWidget(
            widget_content=widget_content,
            label=label,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def checktable(
        self,
        *,
        checkboxes: Sequence[CheckboxContent[Any]],
        label: str,
        uncheck_command: str,
        command: str | None = None,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> ChecktableWidget:
        return ChecktableWidget(
            checkboxes=list(checkboxes),
            label=label,
            uncheck_command=uncheck_command,
            message=self._context.message,
            bot=self._context.bot,
            command=self._resolve_command(command),
            additional_markup=self._resolve_additional_markup(additional_markup),
            result_mode=self._resolve_result_mode(result_mode),
        )

    def _resolve_command(self, command: str | None) -> str:
        return command or self._context.command

    def _resolve_additional_markup(
        self,
        additional_markup: MessageMarkup | None,
    ) -> MessageMarkup | None:
        if additional_markup is not None:
            return additional_markup
        return self._context.additional_markup

    def _resolve_result_mode(
        self,
        result_mode: WidgetResultMode | None,
    ) -> WidgetResultMode | None:
        if result_mode is not None:
            return result_mode
        return self._context.result_mode
