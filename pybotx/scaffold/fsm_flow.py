from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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
    FSM_FLOW_COMMAND_TEMPLATE,
    FSM_FLOW_MODULE_TEMPLATE,
    FSM_FLOW_TEST_TEMPLATE,
)


_COMMAND_IMPORTS_START = "# pybotx-scaffold command imports start"
_COMMAND_IMPORTS_END = "# pybotx-scaffold command imports end"
_COMMAND_COLLECTORS_START = "    # pybotx-scaffold command collectors start"
_COMMAND_COLLECTORS_END = "    # pybotx-scaffold command collectors end"
_FSM_IMPORTS_START = "# pybotx-scaffold fsm imports start"
_FSM_IMPORTS_END = "# pybotx-scaffold fsm imports end"
_FSM_COLLECTORS_START = "                    # pybotx-scaffold fsm collectors start"
_FSM_COLLECTORS_END = "                    # pybotx-scaffold fsm collectors end"


@dataclass(frozen=True, slots=True)
class CreateFSMFlowOptions:
    flow_name: str
    project_dir: Path | str = "."
    command_name: str | None = None
    description: str | None = None
    initial_prompt: str | None = None
    completion_text: str | None = None


@dataclass(frozen=True, slots=True)
class CreatedFSMFlowArtifacts:
    project_root: Path
    package_name: str
    flow_name: str
    command_path: str
    created_files: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class _FSMFlowSpec:
    module_name: str
    flow_name: str
    command_path: str
    description: str
    initial_prompt: str
    handler_name: str
    start_function_name: str
    states_enum_name: str
    collector_alias: str
    fsm_alias: str
    display_name: str
    display_name_lower: str
    completion_statement: str
    completion_assert_text: str


def create_fsm_flow_in_project(
    options: CreateFSMFlowOptions,
) -> CreatedFSMFlowArtifacts:
    project_root = find_scaffold_project_root(options.project_dir)
    manifest = ScaffoldProjectManifest.load(project_root)
    _ensure_fsm_template_support(project_root, manifest)

    flow_spec = _build_fsm_flow_spec(
        flow_name=options.flow_name,
        command_name=options.command_name,
        description=options.description,
        initial_prompt=options.initial_prompt,
        completion_text=options.completion_text,
    )

    flow_module_path = project_root / manifest.fsm_dir / f"{flow_spec.module_name}.py"
    command_module_path = project_root / manifest.commands_dir / (
        f"{flow_spec.module_name}.py"
    )
    test_module_path = project_root / manifest.tests_dir / (
        f"test_{flow_spec.module_name}_fsm.py"
    )

    for path in (flow_module_path, command_module_path, test_module_path):
        if path.exists():
            raise FileExistsError(f"`{path}` already exists")

    context = {
        "command_literal": repr(flow_spec.command_path),
        "completion_assert_literal": repr(flow_spec.completion_assert_text),
        "completion_statement": flow_spec.completion_statement,
        "description_literal": repr(flow_spec.description),
        "display_name_lower": flow_spec.display_name_lower,
        "fsm_module_prefix": manifest.fsm_module_prefix,
        "handler_name": flow_spec.handler_name,
        "initial_prompt_literal": repr(flow_spec.initial_prompt),
        "module_name": flow_spec.module_name,
        "package_name": manifest.package_name,
        "start_function_name": flow_spec.start_function_name,
        "states_enum_name": flow_spec.states_enum_name,
    }

    write_template(flow_module_path, FSM_FLOW_MODULE_TEMPLATE, context)
    write_template(command_module_path, FSM_FLOW_COMMAND_TEMPLATE, context)
    write_template(test_module_path, FSM_FLOW_TEST_TEMPLATE, context)

    append_marked_lines(
        project_root / manifest.commands_init_path,
        start_marker=_COMMAND_IMPORTS_START,
        end_marker=_COMMAND_IMPORTS_END,
        new_lines=[
            (
                f"from {manifest.commands_module_prefix}.{flow_spec.module_name} "
                f"import collector as {flow_spec.collector_alias}"
            ),
        ],
    )
    append_marked_lines(
        project_root / manifest.commands_init_path,
        start_marker=_COMMAND_COLLECTORS_START,
        end_marker=_COMMAND_COLLECTORS_END,
        new_lines=[f"    {flow_spec.collector_alias},"],
    )

    fsm_import_line = (
        f"from {manifest.fsm_module_prefix}.{flow_spec.module_name} "
        f"import fsm as {flow_spec.fsm_alias}"
    )
    fsm_collector_line = f"                    {flow_spec.fsm_alias},"

    for relative_path in (manifest.bot_path, manifest.tests_conftest_path):
        target_path = project_root / relative_path
        append_marked_lines(
            target_path,
            start_marker=_FSM_IMPORTS_START,
            end_marker=_FSM_IMPORTS_END,
            new_lines=[fsm_import_line],
        )
        append_marked_lines(
            target_path,
            start_marker=_FSM_COLLECTORS_START,
            end_marker=_FSM_COLLECTORS_END,
            new_lines=[fsm_collector_line],
        )

    return CreatedFSMFlowArtifacts(
        project_root=project_root,
        package_name=manifest.package_name,
        flow_name=flow_spec.flow_name,
        command_path=flow_spec.command_path,
        created_files=(
            flow_module_path,
            command_module_path,
            test_module_path,
        ),
    )


def _build_fsm_flow_spec(
    *,
    flow_name: str,
    command_name: str | None,
    description: str | None,
    initial_prompt: str | None,
    completion_text: str | None,
) -> _FSMFlowSpec:
    normalized_flow_name = normalize_scaffold_name(flow_name, kind="Flow name")
    normalized_command_name = normalize_scaffold_name(
        command_name or flow_name,
        kind="Command name",
    )
    module_name = slug_to_module_name(normalized_flow_name)
    display_name_lower = normalized_flow_name.replace("-", " ")
    display_name = display_name_lower.title()
    states_enum_name = f"{module_name_to_pascal_case(module_name)}States"

    if completion_text is None:
        completion_statement = (
            f'await bot.answer_message(f"{display_name} flow completed with value: {{value}}.")'
        )
        completion_assert_text = f"{display_name} flow completed with value: sample-value."
    else:
        completion_statement = f"await bot.answer_message({completion_text!r})"
        completion_assert_text = completion_text

    return _FSMFlowSpec(
        module_name=module_name,
        flow_name=normalized_flow_name,
        command_path=f"/{normalized_command_name}",
        description=description or f"Start {display_name_lower} flow",
        initial_prompt=initial_prompt or f"Enter {display_name_lower} value.",
        handler_name=f"{module_name}_handler",
        start_function_name=f"start_{module_name}_flow",
        states_enum_name=states_enum_name,
        collector_alias=f"{module_name}_collector",
        fsm_alias=f"{module_name}_fsm",
        display_name=display_name,
        display_name_lower=display_name_lower,
        completion_statement=completion_statement,
        completion_assert_text=completion_assert_text,
    )


def _ensure_fsm_template_support(
    project_root: Path,
    manifest: ScaffoldProjectManifest,
) -> None:
    if manifest.template != "production-fastapi-fsm":
        raise ValueError(
            "`pybotx create fsm-flow` is supported only for "
            "`production-fastapi-fsm` projects",
        )

    for relative_path in (manifest.bot_path, manifest.tests_conftest_path):
        _ensure_fsm_markers(
            project_root / relative_path,
            fsm_module_prefix=manifest.fsm_module_prefix,
            package_name=manifest.package_name,
        )


def _ensure_fsm_markers(
    path: Path,
    *,
    fsm_module_prefix: str,
    package_name: str,
) -> None:
    content = path.read_text(encoding="utf-8")
    if _FSM_IMPORTS_START in content and _FSM_COLLECTORS_START in content:
        return

    import_line = f"from {fsm_module_prefix}.login import fsm as login_fsm"
    legacy_import_line = f"from {package_name}.fsm.login import fsm as login_fsm"
    middlewares_line = (
        '        middlewares=[FSMMiddleware([login_fsm], state_repo_key="fsm_state_repo")],'
    )

    if import_line in content:
        current_import_line = import_line
    elif legacy_import_line in content:
        current_import_line = legacy_import_line
    else:
        current_import_line = None

    if current_import_line is None or middlewares_line not in content:
        raise RuntimeError(
            "Couldn't enable FSM flow generation automatically for "
            f"`{path}`. Regenerate the project or add scaffold markers manually.",
        )

    updated_content = content.replace(
        current_import_line,
        "\n".join(
            [
                current_import_line,
                _FSM_IMPORTS_START,
                _FSM_IMPORTS_END,
            ],
        ),
        1,
    ).replace(
        middlewares_line,
        "\n".join(
            [
                "        middlewares=[",
                "            FSMMiddleware(",
                "                [",
                "                    login_fsm,",
                _FSM_COLLECTORS_START,
                _FSM_COLLECTORS_END,
                "                ],",
                '                state_repo_key="fsm_state_repo",',
                "            ),",
                "        ],",
            ],
        ),
        1,
    )
    path.write_text(updated_content, encoding="utf-8")
