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
    APPLICATION_SERVICE_TEST_TEMPLATE,
    SERVICE_MODULE_TEMPLATE,
)

_SERVICE_IMPORTS_START = "# pybotx-scaffold service imports start"
_SERVICE_IMPORTS_END = "# pybotx-scaffold service imports end"
_SERVICE_PROVIDERS_START = "    # pybotx-scaffold service providers start"
_SERVICE_PROVIDERS_END = "    # pybotx-scaffold service providers end"


@dataclass(frozen=True, slots=True)
class CreateServiceOptions:
    service_name: str
    project_dir: Path | str = "."
    response_text: str | None = None


@dataclass(frozen=True, slots=True)
class CreatedServiceArtifacts:
    project_root: Path
    package_name: str
    service_name: str
    created_files: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class _ServiceSpec:
    module_name: str
    response_text: str
    service_class_name: str
    service_provider_name: str
    test_module_name: str


def create_service_in_project(
    options: CreateServiceOptions,
) -> CreatedServiceArtifacts:
    project_root = find_scaffold_project_root(options.project_dir)
    manifest = ScaffoldProjectManifest.load(project_root)
    service_spec = _build_service_spec(
        service_name=options.service_name,
        response_text=options.response_text,
    )

    service_module_path = project_root / manifest.services_dir / (
        f"{service_spec.module_name}.py"
    )
    test_module_path = project_root / manifest.tests_dir / (
        f"{service_spec.test_module_name}.py"
    )

    for path in (service_module_path, test_module_path):
        if path.exists():
            raise FileExistsError(f"`{path}` already exists")

    context = {
        "module_name": service_spec.module_name,
        "response_text_literal": repr(service_spec.response_text),
        "service_class_name": service_spec.service_class_name,
        "services_module_prefix": manifest.services_module_prefix,
    }

    write_template(service_module_path, SERVICE_MODULE_TEMPLATE, context)
    write_template(test_module_path, APPLICATION_SERVICE_TEST_TEMPLATE, context)

    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=_SERVICE_IMPORTS_START,
        end_marker=_SERVICE_IMPORTS_END,
        new_lines=[
            (
                f"from {manifest.services_module_prefix}.{service_spec.module_name} "
                f"import {service_spec.service_class_name}"
            ),
        ],
    )
    append_marked_lines(
        project_root / manifest.container_path,
        start_marker=_SERVICE_PROVIDERS_START,
        end_marker=_SERVICE_PROVIDERS_END,
        new_lines=[
            (
                f"    {service_spec.service_provider_name} = providers.Factory("
                f"{service_spec.service_class_name})"
            ),
        ],
    )

    return CreatedServiceArtifacts(
        project_root=project_root,
        package_name=manifest.package_name,
        service_name=service_spec.module_name,
        created_files=(
            service_module_path,
            test_module_path,
        ),
    )


def _build_service_spec(
    *,
    service_name: str,
    response_text: str | None,
) -> _ServiceSpec:
    normalized_service_name = normalize_scaffold_name(
        service_name,
        kind="Service name",
    )
    module_name = slug_to_module_name(normalized_service_name)

    return _ServiceSpec(
        module_name=module_name,
        response_text=response_text or f"Implement {normalized_service_name} service.",
        service_class_name=f"{module_name_to_pascal_case(module_name)}Service",
        service_provider_name=f"{module_name}_service",
        test_module_name=f"test_{module_name}_service",
    )
