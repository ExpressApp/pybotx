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
    COMMAND_MODULE_TEMPLATE,
    COMMAND_TEST_TEMPLATE,
    SERVICE_MODULE_TEMPLATE,
)

_COMMAND_IMPORTS_START = "# pybotx-scaffold command imports start"
_COMMAND_IMPORTS_END = "# pybotx-scaffold command imports end"
_COMMAND_COLLECTORS_START = "    # pybotx-scaffold command collectors start"
_COMMAND_COLLECTORS_END = "    # pybotx-scaffold command collectors end"
_SERVICE_IMPORTS_START = "# pybotx-scaffold service imports start"
_SERVICE_IMPORTS_END = "# pybotx-scaffold service imports end"
_SERVICE_PROVIDERS_START = "    # pybotx-scaffold service providers start"
_SERVICE_PROVIDERS_END = "    # pybotx-scaffold service providers end"


@dataclass(frozen=True, slots=True)
class CreateCommandOptions:
    command_name: str
    project_dir: Path | str = "."
    description: str | None = None
    response_text: str | None = None


@dataclass(frozen=True, slots=True)
class CreatedCommandArtifacts:
    project_root: Path
    package_name: str
    command_path: str
    created_files: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class _CommandSpec:
    module_name: str
    command_path: str
    description: str
    response_text: str
    service_class_name: str
    service_provider_name: str
    collector_alias: str
    handler_name: str


def create_command_in_project(
    options: CreateCommandOptions,
) -> CreatedCommandArtifacts:
    project_root = find_scaffold_project_root(options.project_dir)
    manifest = ScaffoldProjectManifest.load(project_root)
    command_spec = _build_command_spec(
        command_name=options.command_name,
        description=options.description,
        response_text=options.response_text,
    )

    command_module_path = project_root / manifest.commands_dir / (
        f"{command_spec.module_name}.py"
    )
    service_module_path = project_root / manifest.services_dir / (
        f"{command_spec.module_name}.py"
    )
    test_module_path = project_root / manifest.tests_dir / (
        f"test_{command_spec.module_name}.py"
    )

    for path in (command_module_path, service_module_path, test_module_path):
        if path.exists():
            raise FileExistsError(f"`{path}` already exists")

    context = {
        "command_literal": repr(command_spec.command_path),
        "container_module": manifest.container_module,
        "description_literal": repr(command_spec.description),
        "handler_name": command_spec.handler_name,
        "module_name": command_spec.module_name,
        "package_name": manifest.package_name,
        "response_text_literal": repr(command_spec.response_text),
        "service_class_name": command_spec.service_class_name,
        "service_provider_name": command_spec.service_provider_name,
    }

    write_template(command_module_path, COMMAND_MODULE_TEMPLATE, context)
    write_template(service_module_path, SERVICE_MODULE_TEMPLATE, context)
    write_template(test_module_path, COMMAND_TEST_TEMPLATE, context)

    append_marked_lines(
        project_root / manifest.commands_init_path,
        start_marker=_COMMAND_IMPORTS_START,
        end_marker=_COMMAND_IMPORTS_END,
        new_lines=[
            (
                f"from {manifest.commands_module_prefix}.{command_spec.module_name} "
                f"import collector as {command_spec.collector_alias}"
            ),
        ],
    )
    append_marked_lines(
        project_root / manifest.commands_init_path,
        start_marker=_COMMAND_COLLECTORS_START,
        end_marker=_COMMAND_COLLECTORS_END,
        new_lines=[f"    {command_spec.collector_alias},"],
    )
    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=_SERVICE_IMPORTS_START,
        end_marker=_SERVICE_IMPORTS_END,
        new_lines=[
            (
                f"from {manifest.services_module_prefix}.{command_spec.module_name} "
                f"import {command_spec.service_class_name}"
            ),
        ],
    )
    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=_SERVICE_PROVIDERS_START,
        end_marker=_SERVICE_PROVIDERS_END,
        new_lines=[
            (
                f"    {command_spec.service_provider_name} = providers.Factory("
                f"{command_spec.service_class_name})"
            ),
        ],
    )

    return CreatedCommandArtifacts(
        project_root=project_root,
        package_name=manifest.package_name,
        command_path=command_spec.command_path,
        created_files=(
            command_module_path,
            service_module_path,
            test_module_path,
        ),
    )


def _build_command_spec(
    *,
    command_name: str,
    description: str | None,
    response_text: str | None,
) -> _CommandSpec:
    normalized_command = normalize_scaffold_name(command_name, kind="Command name")
    module_name = slug_to_module_name(normalized_command)
    service_class_name = f"{module_name_to_pascal_case(module_name)}Service"

    return _CommandSpec(
        module_name=module_name,
        command_path=f"/{normalized_command}",
        description=description or f"Handle /{normalized_command} command",
        response_text=response_text or f"Handled /{normalized_command} command.",
        service_class_name=service_class_name,
        service_provider_name=f"{module_name}_service",
        collector_alias=f"{module_name}_collector",
        handler_name=f"{module_name}_handler",
    )
