from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Literal

from pybotx.scaffold._shared import (
    append_marked_lines,
    module_name_to_pascal_case,
    normalize_scaffold_name,
    slug_to_module_name,
    write_template,
)
from pybotx.scaffold.manifest import (
    ScaffoldProjectManifest,
    find_scaffold_project_root,
)
from pybotx.scaffold.templates import (
    WIDGET_APPROVAL_COMMAND_TEMPLATE,
    WIDGET_APPROVAL_SERVICE_TEMPLATE,
    WIDGET_APPROVAL_TEST_TEMPLATE,
    WIDGET_CONFIRM_COMMAND_TEMPLATE,
    WIDGET_CONFIRM_SERVICE_TEMPLATE,
    WIDGET_CONFIRM_TEST_TEMPLATE,
    WIDGET_DATE_RANGE_COMMAND_TEMPLATE,
    WIDGET_DATE_RANGE_SERVICE_TEMPLATE,
    WIDGET_DATE_RANGE_TEST_TEMPLATE,
    WIDGET_MULTI_SELECT_COMMAND_TEMPLATE,
    WIDGET_MULTI_SELECT_SERVICE_TEMPLATE,
    WIDGET_MULTI_SELECT_TEST_TEMPLATE,
    WIDGET_SEARCH_SELECT_COMMAND_TEMPLATE,
    WIDGET_SEARCH_SELECT_TEST_TEMPLATE,
    WIDGET_SELECT_COMMAND_TEMPLATE,
    WIDGET_SELECT_SERVICE_TEMPLATE,
    WIDGET_SELECT_TEST_TEMPLATE,
    WIDGET_SUPPORT_TEMPLATE,
)


WidgetKind = Literal[
    "confirm",
    "approval",
    "select",
    "search-select",
    "multi-select",
    "date-range",
]

_COMMAND_IMPORTS_START = "# pybotx-scaffold command imports start"
_COMMAND_IMPORTS_END = "# pybotx-scaffold command imports end"
_COMMAND_COLLECTORS_START = "    # pybotx-scaffold command collectors start"
_COMMAND_COLLECTORS_END = "    # pybotx-scaffold command collectors end"
_SERVICE_IMPORTS_START = "# pybotx-scaffold service imports start"
_SERVICE_IMPORTS_END = "# pybotx-scaffold service imports end"
_SERVICE_PROVIDERS_START = "    # pybotx-scaffold service providers start"
_SERVICE_PROVIDERS_END = "    # pybotx-scaffold service providers end"
_ANSWER_MESSAGE_MOCK = (
    "    built_bot.answer_message = AsyncMock(return_value=uuid4())  # type: ignore[method-assign]"
)
_SEND_MESSAGE_MOCK = (
    "    built_bot.send = AsyncMock(return_value=uuid4())  # type: ignore[method-assign]"
)
_EDIT_MESSAGE_MOCK = "    built_bot.edit_message = AsyncMock()  # type: ignore[method-assign]"


@dataclass(frozen=True, slots=True)
class CreateWidgetOptions:
    widget_name: str
    project_dir: Path | str = "."
    kind: WidgetKind = "confirm"
    command_name: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class CreatedWidgetArtifacts:
    project_root: Path
    package_name: str
    widget_name: str
    kind: WidgetKind
    command_path: str
    created_files: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class _WidgetSpec:
    kind: WidgetKind
    module_name: str
    widget_name: str
    command_path: str
    description: str
    service_class_name: str
    service_provider_name: str
    collector_alias: str
    handler_name: str
    label: str
    primary_result: str
    secondary_result: str
    tertiary_result: str | None = None


def create_widget_in_project(options: CreateWidgetOptions) -> CreatedWidgetArtifacts:
    project_root = find_scaffold_project_root(options.project_dir)
    manifest = ScaffoldProjectManifest.load(project_root)
    widget_spec = _build_widget_spec(
        widget_name=options.widget_name,
        kind=options.kind,
        command_name=options.command_name,
        description=options.description,
    )

    command_module_path = project_root / manifest.commands_dir / (
        f"{widget_spec.module_name}.py"
    )
    service_module_path = project_root / manifest.services_dir / (
        f"{widget_spec.module_name}.py"
    )
    test_module_path = project_root / manifest.tests_dir / (
        f"test_{widget_spec.module_name}_widget.py"
    )
    widget_support_path = project_root / manifest.widget_support_path

    for path in (command_module_path, service_module_path, test_module_path):
        if path.exists():
            raise FileExistsError(f"`{path}` already exists")

    created_files: list[Path] = []
    if not widget_support_path.exists():
        write_template(
            widget_support_path,
            WIDGET_SUPPORT_TEMPLATE,
            {"container_module": manifest.container_module},
        )
        created_files.append(widget_support_path)

    _ensure_widget_test_mocks(project_root / manifest.tests_conftest_path)

    command_template, service_template, test_template = _select_widget_templates(
        widget_spec.kind,
    )
    context = {
        "command_literal": repr(widget_spec.command_path),
        "description_literal": repr(widget_spec.description),
        "display_body_literal": repr(
            f"{widget_spec.label}\nНачало: —\nКонец: —",
        ),
        "handler_name": widget_spec.handler_name,
        "label_literal": repr(widget_spec.label),
        "module_name": widget_spec.module_name,
        "package_name": manifest.package_name,
        "primary_result_literal": repr(widget_spec.primary_result),
        "secondary_result_literal": repr(widget_spec.secondary_result),
        "service_class_name": widget_spec.service_class_name,
        "service_provider_name": widget_spec.service_provider_name,
        "tertiary_result_literal": repr(widget_spec.tertiary_result or ""),
        "widget_support_module": manifest.widget_support_module,
    }

    write_template(command_module_path, command_template, context)
    write_template(service_module_path, service_template, context)
    write_template(test_module_path, test_template, context)
    created_files.extend(
        [
            command_module_path,
            service_module_path,
            test_module_path,
        ],
    )

    append_marked_lines(
        project_root / manifest.commands_init_path,
        start_marker=_COMMAND_IMPORTS_START,
        end_marker=_COMMAND_IMPORTS_END,
        new_lines=[
            (
                f"from {manifest.commands_module_prefix}.{widget_spec.module_name} "
                f"import collector as {widget_spec.collector_alias}"
            ),
        ],
    )
    append_marked_lines(
        project_root / manifest.commands_init_path,
        start_marker=_COMMAND_COLLECTORS_START,
        end_marker=_COMMAND_COLLECTORS_END,
        new_lines=[f"    {widget_spec.collector_alias},"],
    )
    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=_SERVICE_IMPORTS_START,
        end_marker=_SERVICE_IMPORTS_END,
        new_lines=[
            (
                f"from {manifest.services_module_prefix}.{widget_spec.module_name} "
                f"import {widget_spec.service_class_name}"
            ),
        ],
    )
    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=_SERVICE_PROVIDERS_START,
        end_marker=_SERVICE_PROVIDERS_END,
        new_lines=[
            (
                f"    {widget_spec.service_provider_name} = providers.Factory("
                f"{widget_spec.service_class_name})"
            ),
        ],
    )

    return CreatedWidgetArtifacts(
        project_root=project_root,
        package_name=manifest.package_name,
        widget_name=widget_spec.widget_name,
        kind=widget_spec.kind,
        command_path=widget_spec.command_path,
        created_files=tuple(created_files),
    )


def _build_widget_spec(
    *,
    widget_name: str,
    kind: WidgetKind,
    command_name: str | None,
    description: str | None,
) -> _WidgetSpec:
    normalized_widget_name = normalize_scaffold_name(widget_name, kind="Widget name")
    normalized_command_name = normalize_scaffold_name(
        command_name or widget_name,
        kind="Command name",
    )
    module_name = slug_to_module_name(normalized_widget_name)
    display_name = normalized_widget_name.replace("-", " ")
    pascal_name = module_name_to_pascal_case(module_name)

    if kind == "confirm":
        return _WidgetSpec(
            kind=kind,
            module_name=module_name,
            widget_name=normalized_widget_name,
            command_path=f"/{normalized_command_name}",
            description=description or f"Show {display_name} confirmation widget",
            service_class_name=f"{pascal_name}WidgetService",
            service_provider_name=f"{module_name}_widget_service",
            collector_alias=f"{module_name}_collector",
            handler_name=f"{module_name}_handler",
            label=f"Confirm {display_name}?",
            primary_result=f"{display_name.title()} confirmed.",
            secondary_result=f"{display_name.title()} cancelled.",
        )

    if kind == "approval":
        return _WidgetSpec(
            kind=kind,
            module_name=module_name,
            widget_name=normalized_widget_name,
            command_path=f"/{normalized_command_name}",
            description=description or f"Show {display_name} approval widget",
            service_class_name=f"{pascal_name}WidgetService",
            service_provider_name=f"{module_name}_widget_service",
            collector_alias=f"{module_name}_collector",
            handler_name=f"{module_name}_handler",
            label=f"Review {display_name}",
            primary_result=f"{display_name.title()} approved.",
            secondary_result=f"{display_name.title()} rejected.",
            tertiary_result=f"Left a comment for {display_name}.",
        )

    if kind == "search-select":
        return _WidgetSpec(
            kind=kind,
            module_name=module_name,
            widget_name=normalized_widget_name,
            command_path=f"/{normalized_command_name}",
            description=description or f"Show {display_name} search select widget",
            service_class_name=f"{pascal_name}WidgetService",
            service_provider_name=f"{module_name}_widget_service",
            collector_alias=f"{module_name}_collector",
            handler_name=f"{module_name}_handler",
            label=f"Choose {display_name}",
            primary_result="Selected value: prod",
            secondary_result="",
        )

    if kind == "multi-select":
        return _WidgetSpec(
            kind=kind,
            module_name=module_name,
            widget_name=normalized_widget_name,
            command_path=f"/{normalized_command_name}",
            description=description or f"Show {display_name} multi select widget",
            service_class_name=f"{pascal_name}WidgetService",
            service_provider_name=f"{module_name}_widget_service",
            collector_alias=f"{module_name}_collector",
            handler_name=f"{module_name}_handler",
            label=f"Choose {display_name}",
            primary_result="Selected values: dev, prod",
            secondary_result="",
        )

    if kind == "date-range":
        return _WidgetSpec(
            kind=kind,
            module_name=module_name,
            widget_name=normalized_widget_name,
            command_path=f"/{normalized_command_name}",
            description=description or f"Show {display_name} date range widget",
            service_class_name=f"{pascal_name}WidgetService",
            service_provider_name=f"{module_name}_widget_service",
            collector_alias=f"{module_name}_collector",
            handler_name=f"{module_name}_handler",
            label=f"Choose {display_name} period",
            primary_result="Selected period: 2026-03-01 - 2026-03-08",
            secondary_result="",
        )

    return _WidgetSpec(
        kind=kind,
        module_name=module_name,
        widget_name=normalized_widget_name,
        command_path=f"/{normalized_command_name}",
        description=description or f"Show {display_name} select widget",
        service_class_name=f"{pascal_name}WidgetService",
        service_provider_name=f"{module_name}_widget_service",
        collector_alias=f"{module_name}_collector",
        handler_name=f"{module_name}_handler",
        label=f"Choose {display_name}",
        primary_result="Selected value: prod",
        secondary_result="",
    )


def _select_widget_templates(
    kind: WidgetKind,
) -> tuple[Template, Template, Template]:
    if kind == "confirm":
        return (
            WIDGET_CONFIRM_COMMAND_TEMPLATE,
            WIDGET_CONFIRM_SERVICE_TEMPLATE,
            WIDGET_CONFIRM_TEST_TEMPLATE,
        )
    if kind == "approval":
        return (
            WIDGET_APPROVAL_COMMAND_TEMPLATE,
            WIDGET_APPROVAL_SERVICE_TEMPLATE,
            WIDGET_APPROVAL_TEST_TEMPLATE,
        )
    if kind == "search-select":
        return (
            WIDGET_SEARCH_SELECT_COMMAND_TEMPLATE,
            WIDGET_SELECT_SERVICE_TEMPLATE,
            WIDGET_SEARCH_SELECT_TEST_TEMPLATE,
        )
    if kind == "multi-select":
        return (
            WIDGET_MULTI_SELECT_COMMAND_TEMPLATE,
            WIDGET_MULTI_SELECT_SERVICE_TEMPLATE,
            WIDGET_MULTI_SELECT_TEST_TEMPLATE,
        )
    if kind == "date-range":
        return (
            WIDGET_DATE_RANGE_COMMAND_TEMPLATE,
            WIDGET_DATE_RANGE_SERVICE_TEMPLATE,
            WIDGET_DATE_RANGE_TEST_TEMPLATE,
        )
    return (
        WIDGET_SELECT_COMMAND_TEMPLATE,
        WIDGET_SELECT_SERVICE_TEMPLATE,
        WIDGET_SELECT_TEST_TEMPLATE,
    )


def _ensure_widget_test_mocks(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if _SEND_MESSAGE_MOCK in content and _EDIT_MESSAGE_MOCK in content:
        return

    if _ANSWER_MESSAGE_MOCK not in content:
        raise RuntimeError(
            "Couldn't enable widget test support automatically for "
            f"`{path}`. Regenerate the project or add send/edit mocks manually.",
        )

    replacement_lines = [
        _ANSWER_MESSAGE_MOCK,
        _SEND_MESSAGE_MOCK,
        _EDIT_MESSAGE_MOCK,
    ]
    updated_content = content.replace(
        _ANSWER_MESSAGE_MOCK,
        "\n".join(replacement_lines),
        1,
    )
    path.write_text(updated_content, encoding="utf-8")
