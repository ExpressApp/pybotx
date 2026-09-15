from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pybotx.scaffold._shared import (
    module_name_to_pascal_case,
    normalize_scaffold_name,
    slug_to_module_name,
    write_template,
)
from pybotx.scaffold.manifest import (
    ScaffoldProjectManifest,
    find_scaffold_project_root,
)
from pybotx.scaffold.templates import PORT_TEMPLATE


@dataclass(frozen=True, slots=True)
class CreatePortOptions:
    port_name: str
    project_dir: Path | str = "."


@dataclass(frozen=True, slots=True)
class CreatedPortArtifacts:
    project_root: Path
    package_name: str
    port_name: str
    created_files: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class _PortSpec:
    normalized_name: str
    module_name: str
    port_class_name: str


def create_port_in_project(options: CreatePortOptions) -> CreatedPortArtifacts:
    project_root = find_scaffold_project_root(options.project_dir)
    manifest = ScaffoldProjectManifest.load(project_root)
    port_spec = _build_port_spec(options.port_name)

    port_module_path = project_root / manifest.domain_ports_dir / (
        f"{port_spec.module_name}.py"
    )
    if port_module_path.exists():
        raise FileExistsError(f"`{port_module_path}` already exists")

    context = {
        "port_class_name": port_spec.port_class_name,
        "port_slug": port_spec.normalized_name,
    }
    write_template(port_module_path, PORT_TEMPLATE, context)

    return CreatedPortArtifacts(
        project_root=project_root,
        package_name=manifest.package_name,
        port_name=port_spec.module_name,
        created_files=(port_module_path,),
    )


def _build_port_spec(port_name: str) -> _PortSpec:
    normalized_port_name = normalize_scaffold_name(
        port_name,
        kind="Port name",
    )
    module_name = slug_to_module_name(normalized_port_name)

    return _PortSpec(
        normalized_name=normalized_port_name,
        module_name=module_name,
        port_class_name=f"{module_name_to_pascal_case(module_name)}Port",
    )
