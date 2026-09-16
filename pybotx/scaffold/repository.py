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
    REPOSITORY_IMPLEMENTATION_TEMPLATE,
    REPOSITORY_PORT_TEMPLATE,
    REPOSITORY_TEST_TEMPLATE,
)

_REPOSITORY_IMPORTS_START = "# pybotx-scaffold repository imports start"
_REPOSITORY_IMPORTS_END = "# pybotx-scaffold repository imports end"
_REPOSITORY_PROVIDERS_START = "    # pybotx-scaffold repository providers start"
_REPOSITORY_PROVIDERS_END = "    # pybotx-scaffold repository providers end"

_FALLBACK_IMPORTS_START = "# pybotx-scaffold service imports start"
_FALLBACK_IMPORTS_END = "# pybotx-scaffold service imports end"
_FALLBACK_PROVIDERS_START = "    # pybotx-scaffold service providers start"
_FALLBACK_PROVIDERS_END = "    # pybotx-scaffold service providers end"


@dataclass(frozen=True, slots=True)
class CreateRepositoryOptions:
    repository_name: str
    project_dir: Path | str = "."
    port_name: str | None = None


@dataclass(frozen=True, slots=True)
class CreatedRepositoryArtifacts:
    project_root: Path
    package_name: str
    repository_name: str
    port_name: str
    created_files: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class _RepositorySpec:
    repository_slug: str
    repository_module_name: str
    implementation_module_name: str
    port_slug: str
    port_module_name: str
    port_class_name: str
    implementation_class_name: str
    repository_provider_name: str
    test_module_name: str
    should_create_port: bool


def create_repository_in_project(
    options: CreateRepositoryOptions,
) -> CreatedRepositoryArtifacts:
    project_root = find_scaffold_project_root(options.project_dir)
    manifest = ScaffoldProjectManifest.load(project_root)
    repository_spec = _build_repository_spec(
        repository_name=options.repository_name,
        port_name=options.port_name,
    )

    port_module_path = project_root / manifest.domain_ports_dir / (
        f"{repository_spec.port_module_name}.py"
    )
    repository_module_path = project_root / manifest.infrastructure_repositories_dir / (
        f"{repository_spec.implementation_module_name}.py"
    )
    test_module_path = project_root / manifest.tests_dir / (
        f"{repository_spec.test_module_name}.py"
    )

    paths_to_check = [repository_module_path, test_module_path]
    if repository_spec.should_create_port:
        paths_to_check.append(port_module_path)
    else:
        if not port_module_path.exists():
            raise FileNotFoundError(
                f"Port `{repository_spec.port_module_name}` not found at `{port_module_path}`",
            )

    for path in paths_to_check:
        if path.exists():
            raise FileExistsError(f"`{path}` already exists")

    context = {
        "container_module": manifest.container_module,
        "implementation_class_name": repository_spec.implementation_class_name,
        "module_name": repository_spec.repository_module_name,
        "port_class_name": repository_spec.port_class_name,
        "repository_module": (
            f"{manifest.package_name}.infrastructure.repositories."
            f"{repository_spec.implementation_module_name}"
        ),
        "repository_provider_name": repository_spec.repository_provider_name,
        "repository_slug": repository_spec.repository_slug,
    }

    if repository_spec.should_create_port:
        write_template(port_module_path, REPOSITORY_PORT_TEMPLATE, context)
    write_template(
        repository_module_path,
        REPOSITORY_IMPLEMENTATION_TEMPLATE,
        context,
    )
    write_template(test_module_path, REPOSITORY_TEST_TEMPLATE, context)

    imports_start, imports_end = _resolve_container_markers(
        project_root / manifest.container_path,
        preferred_start=_REPOSITORY_IMPORTS_START,
        preferred_end=_REPOSITORY_IMPORTS_END,
        fallback_start=_FALLBACK_IMPORTS_START,
        fallback_end=_FALLBACK_IMPORTS_END,
    )
    providers_start, providers_end = _resolve_container_markers(
        project_root / manifest.container_path,
        preferred_start=_REPOSITORY_PROVIDERS_START,
        preferred_end=_REPOSITORY_PROVIDERS_END,
        fallback_start=_FALLBACK_PROVIDERS_START,
        fallback_end=_FALLBACK_PROVIDERS_END,
    )

    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=imports_start,
        end_marker=imports_end,
        new_lines=[
            (
                "from "
                f"{manifest.package_name}.infrastructure.repositories."
                f"{repository_spec.implementation_module_name} "
                f"import {repository_spec.implementation_class_name}"
            ),
        ],
    )
    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=providers_start,
        end_marker=providers_end,
        new_lines=[
            (
                f"    {repository_spec.repository_provider_name} = providers.Singleton("
                f"{repository_spec.implementation_class_name})"
            ),
        ],
    )

    return CreatedRepositoryArtifacts(
        project_root=project_root,
        package_name=manifest.package_name,
        repository_name=repository_spec.repository_module_name,
        port_name=repository_spec.port_module_name,
        created_files=tuple(paths_to_check),
    )


def _build_repository_spec(
    *,
    repository_name: str,
    port_name: str | None,
) -> _RepositorySpec:
    normalized_repository_name = normalize_scaffold_name(
        repository_name,
        kind="Repository name",
    )
    repository_module_base = slug_to_module_name(normalized_repository_name)

    if port_name is None:
        port_slug = normalized_repository_name
        port_module_name = f"{repository_module_base}_repository"
        port_class_name = f"{module_name_to_pascal_case(repository_module_base)}Repository"
        repository_module_name = port_module_name
        implementation_module_name = f"stub_{repository_module_name}"
        implementation_class_name = f"Stub{port_class_name}"
        repository_provider_name = port_module_name
        test_module_name = f"test_{repository_module_name}"
        should_create_port = True
    else:
        normalized_port_name = normalize_scaffold_name(
            port_name,
            kind="Port name",
        )
        port_module_name = slug_to_module_name(normalized_port_name)
        port_class_name = module_name_to_pascal_case(port_module_name)
        if not port_module_name.endswith("_repository"):
            port_class_name = f"{port_class_name}Port"
        repository_module_name = f"{repository_module_base}_repository"
        implementation_module_name = f"stub_{repository_module_name}"
        implementation_class_name = (
            f"Stub{module_name_to_pascal_case(repository_module_base)}Repository"
        )
        repository_provider_name = port_module_name
        test_module_name = f"test_{repository_module_name}"
        port_slug = normalized_port_name
        should_create_port = False

    return _RepositorySpec(
        repository_slug=normalized_repository_name,
        repository_module_name=repository_module_name,
        implementation_module_name=implementation_module_name,
        port_slug=port_slug,
        port_module_name=port_module_name,
        port_class_name=port_class_name,
        implementation_class_name=implementation_class_name,
        repository_provider_name=repository_provider_name,
        test_module_name=test_module_name,
        should_create_port=should_create_port,
    )


def _resolve_container_markers(
    path: Path,
    *,
    preferred_start: str,
    preferred_end: str,
    fallback_start: str,
    fallback_end: str,
) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    if preferred_start in content and preferred_end in content:
        return preferred_start, preferred_end
    if fallback_start in content and fallback_end in content:
        return fallback_start, fallback_end
    raise RuntimeError(f"Couldn't find scaffold markers in `{path}`")
