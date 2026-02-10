from pathlib import Path
import ast

import pytest
from pytestarch import LayerRule, LayeredArchitecture, get_evaluable_architecture

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "pybotx"


def _base_package_name(evaluable) -> str:
    candidates = [
        SRC.name,
        f"{ROOT.name}.{SRC.name}",
    ]
    for candidate in candidates:
        if f"{candidate}.domain" in evaluable.modules:
            return candidate
    return SRC.name


def _build_architecture(base_module: str) -> LayeredArchitecture:
    contracts_pattern = (
        rf"{base_module}\.(presentation|infrastructure)\.contracts(\.|$)"
    )
    non_contracts_infra = rf"{base_module}\.infrastructure(?!\.contracts)(\.|$)"
    non_contracts_presentation = rf"{base_module}\.presentation(?!\.contracts)(\.|$)"
    return (
        LayeredArchitecture()
        .layer("contracts")
        .have_modules_with_names_matching(contracts_pattern)
        .layer("domain")
        .containing_modules(f"{base_module}.domain")
        .layer("application")
        .containing_modules(f"{base_module}.application")
        .layer("infrastructure")
        .have_modules_with_names_matching(non_contracts_infra)
        .layer("presentation")
        .have_modules_with_names_matching(non_contracts_presentation)
    )


@pytest.fixture(scope="session")
def evaluable_architecture():
    return get_evaluable_architecture(str(ROOT), str(SRC))


def _assert_no_access(evaluable, source_layer: str, forbidden_layers: list[str]) -> None:
    base_module = _base_package_name(evaluable)
    arch = _build_architecture(base_module)
    rule = (
        LayerRule()
        .based_on(arch)
        .layers_that()
        .are_named(source_layer)
        .should_not()
        .access_layers_that()
        .are_named(forbidden_layers)
    )
    rule.assert_applies(evaluable)


def test__domain_does_not_depend_on_other_layers(evaluable_architecture) -> None:
    _assert_no_access(
        evaluable_architecture,
        "domain",
        ["application", "contracts", "infrastructure", "presentation"],
    )


def test__application_does_not_depend_on_infrastructure_or_presentation(
    evaluable_architecture,
) -> None:
    _assert_no_access(
        evaluable_architecture,
        "application",
        ["contracts", "infrastructure", "presentation"],
    )


def test__infrastructure_does_not_depend_on_application_or_presentation(
    evaluable_architecture,
) -> None:
    _assert_no_access(
        evaluable_architecture,
        "infrastructure",
        ["application", "presentation"],
    )


def test__presentation_does_not_depend_on_infrastructure(
    evaluable_architecture,
) -> None:
    _assert_no_access(evaluable_architecture, "presentation", ["infrastructure"])


def test__contracts_do_not_depend_on_higher_layers(
    evaluable_architecture,
) -> None:
    _assert_no_access(
        evaluable_architecture,
        "contracts",
        ["application", "infrastructure", "presentation"],
    )


def _iter_python_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*.py") if path.is_file()]


def _collect_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            imports.add(node.module.split(".")[0])
    return imports


def test__domain_and_application_have_no_framework_imports() -> None:
    forbidden = {
        "aiohttp",
        "django",
        "fastapi",
        "httpx",
        "ninja",
        "starlette",
        "uvicorn",
    }
    offenders: list[tuple[Path, str]] = []
    for layer in ("domain", "application"):
        for path in _iter_python_files(SRC / layer):
            imports = _collect_imports(path)
            for module in sorted(imports & forbidden):
                offenders.append((path, module))
    assert offenders == []


def test__dependency_injector_only_in_container() -> None:
    offenders: list[Path] = []
    for path in _iter_python_files(SRC):
        if path.name == "container.py":
            continue
        imports = _collect_imports(path)
        if "dependency_injector" in imports:
            offenders.append(path)
    assert offenders == []
