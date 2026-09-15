from __future__ import annotations

from dataclasses import dataclass
import importlib.metadata
import keyword
from pathlib import Path
import re
from string import Template
from typing import Literal

from pybotx.scaffold.manifest import (
    PROJECT_LAYOUT_CLEAN_ARCHITECTURE,
    ScaffoldProjectManifest,
)
from pybotx.scaffold.templates import (
    APPLICATION_INIT_TEMPLATE,
    APPLICATION_PORTS_INIT_TEMPLATE,
    ARCHITECTURE_TEMPLATE,
    ARCHITECTURE_TEST_TEMPLATE,
    AUTH_SERVICE_TEMPLATE,
    BOT_TEMPLATE,
    BOT_FSM_TEMPLATE,
    COMMANDS_INIT_TEMPLATE,
    COMMANDS_INIT_FSM_TEMPLATE,
    COMMON_COMMANDS_TEMPLATE,
    COMMON_COMMANDS_FSM_TEMPLATE,
    CONFIG_TEMPLATE,
    CONFIG_FSM_TEMPLATE,
    CONTAINER_TEMPLATE,
    CONTAINER_FSM_TEMPLATE,
    DOMAIN_PORTS_INIT_TEMPLATE,
    DOCKER_COMPOSE_TEMPLATE,
    DOCKERFILE_TEMPLATE,
    ENV_EXAMPLE_TEMPLATE,
    ENV_EXAMPLE_FSM_TEMPLATE,
    FSM_INIT_TEMPLATE,
    FSM_LOGIN_TEMPLATE,
    FSM_STATE_REPO_TEMPLATE,
    GREETING_PROFILE_REPOSITORY_TEMPLATE,
    GREETING_PROFILE_TEMPLATE,
    GITIGNORE_TEMPLATE,
    GREETING_SERVICE_TEMPLATE,
    INFRASTRUCTURE_REPOSITORIES_INIT_TEMPLATE,
    MAIN_TEMPLATE,
    MAIN_FSM_TEMPLATE,
    PACKAGE_INIT_TEMPLATE,
    PRESENTATION_API_TEMPLATE,
    PRESENTATION_API_FSM_TEMPLATE,
    PRESENTATION_INIT_TEMPLATE,
    PYPROJECT_TEMPLATE,
    PYPROJECT_FSM_TEMPLATE,
    README_TEMPLATE,
    README_FSM_TEMPLATE,
    SERVICES_INIT_TEMPLATE,
    STATIC_GREETING_PROFILE_REPOSITORY_TEMPLATE,
    TESTS_CONFTEST_TEMPLATE,
    TESTS_CONFTEST_FSM_TEMPLATE,
    TEST_START_COMMAND_TEMPLATE,
    TEST_START_COMMAND_FSM_TEMPLATE,
    DOMAIN_INIT_TEMPLATE,
    INFRASTRUCTURE_INIT_TEMPLATE,
    WIDGET_SUPPORT_TEMPLATE,
)

TemplateName = Literal["production-fastapi", "production-fastapi-fsm"]

_SUPPORTED_TEMPLATES: tuple[TemplateName, ...] = (
    "production-fastapi",
    "production-fastapi-fsm",
)
_NON_ALNUM_RE = re.compile(r"[^0-9a-zA-Z_]+")
_VERSION_RE = re.compile(r'^version = "(?P<version>[^"]+)"$', re.MULTILINE)


@dataclass(frozen=True, slots=True)
class CreateBotProjectOptions:
    target_dir: Path | str
    template: TemplateName = "production-fastapi"
    project_name: str | None = None
    package_name: str | None = None
    display_name: str | None = None
    description: str | None = None
    enable_otel_tracing: bool = False
    include_docker: bool = True


@dataclass(frozen=True, slots=True)
class CreatedBotProject:
    root_dir: Path
    template: TemplateName
    project_name: str
    package_name: str
    created_files: tuple[Path, ...]


def create_bot_project(options: CreateBotProjectOptions) -> CreatedBotProject:
    target_dir = Path(options.target_dir).expanduser().resolve()
    _validate_template(options.template)
    _ensure_target_dir_is_safe(target_dir)

    project_name = options.project_name or target_dir.name
    if not project_name:
        raise ValueError("Project name couldn't be derived from target directory")

    package_name = _normalize_package_name(options.package_name or project_name)
    display_name = options.display_name or _build_display_name(project_name)
    description = options.description or f"{display_name} bot built with pybotx"
    manifest = ScaffoldProjectManifest(
        template=options.template,
        package_name=package_name,
        layout=PROJECT_LAYOUT_CLEAN_ARCHITECTURE,
    )
    context = {
        "api_module": manifest.api_module,
        "bot_module": manifest.bot_module,
        "commands_module_prefix": manifest.commands_module_prefix,
        "config_module": manifest.config_module,
        "container_module": manifest.container_module,
        "description": description,
        "display_name": display_name,
        "enable_otel_tracing": str(options.enable_otel_tracing).lower(),
        "enable_otel_tracing_python": "True" if options.enable_otel_tracing else "False",
        "fsm_state_repo_module": manifest.fsm_state_repo_module,
        "fsm_module_prefix": manifest.fsm_module_prefix,
        "greeting_profile_module": f"{package_name}.domain.greeting_profile",
        "greeting_profile_repository_module": (
            f"{package_name}.domain.ports.greeting_profile_repository"
        ),
        "package_name": package_name,
        "project_name": project_name,
        "services_module_prefix": manifest.services_module_prefix,
        "static_greeting_profile_repository_module": (
            f"{package_name}.infrastructure.repositories.static_greeting_profile_repository"
        ),
        "widget_support_module": manifest.widget_support_module,
        "pybotx_version": _resolve_pybotx_version(),
    }

    target_dir.mkdir(parents=True, exist_ok=True)
    created_files: list[Path] = []
    for relative_path, template in _build_project_templates(
        manifest=manifest,
        include_docker=options.include_docker,
    ):
        absolute_path = target_dir / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text(template.safe_substitute(context), encoding="utf-8")
        created_files.append(absolute_path)

    manifest_path = manifest.write(target_dir)
    created_files.append(manifest_path)

    return CreatedBotProject(
        root_dir=target_dir,
        template=options.template,
        project_name=project_name,
        package_name=package_name,
        created_files=tuple(created_files),
    )


def _validate_template(template: str) -> None:
    if template not in _SUPPORTED_TEMPLATES:
        raise ValueError(
            f"Unsupported template `{template}`. "
            f"Supported templates: {', '.join(_SUPPORTED_TEMPLATES)}",
        )


def _ensure_target_dir_is_safe(target_dir: Path) -> None:
    if target_dir.exists():
        if not target_dir.is_dir():
            raise FileExistsError(f"Target path `{target_dir}` already exists and isn't a directory")
        if any(target_dir.iterdir()):
            raise FileExistsError(f"Target directory `{target_dir}` isn't empty")


def _normalize_package_name(raw_name: str) -> str:
    normalized = _NON_ALNUM_RE.sub("_", raw_name.strip().lower()).strip("_")
    if not normalized:
        raise ValueError("Package name can't be empty")
    if normalized[0].isdigit():
        raise ValueError("Package name should not start with a digit")
    if not normalized.isidentifier():
        raise ValueError(f"Invalid package name `{normalized}`")
    if keyword.iskeyword(normalized):
        raise ValueError(f"Package name `{normalized}` is a reserved Python keyword")
    return normalized


def _build_display_name(project_name: str) -> str:
    tokens = [token for token in _NON_ALNUM_RE.split(project_name) if token]
    if not tokens:
        raise ValueError("Display name couldn't be derived from project name")
    return " ".join(token.capitalize() for token in tokens)


def _resolve_pybotx_version() -> str:
    try:
        return importlib.metadata.version("pybotx")
    except importlib.metadata.PackageNotFoundError:
        pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
        pyproject_content = pyproject_path.read_text(encoding="utf-8")
        match = _VERSION_RE.search(pyproject_content)
        if match is None:
            raise RuntimeError("Couldn't resolve current pybotx version from pyproject.toml")
        return match.group("version")


def _build_project_templates(
    *,
    manifest: ScaffoldProjectManifest,
    include_docker: bool,
) -> tuple[tuple[Path, Template], ...]:
    src_root = manifest.src_package_dir
    if manifest.template == "production-fastapi":
        template_items: list[tuple[Path, Template]] = [
            (Path(".env.example"), ENV_EXAMPLE_TEMPLATE),
            (Path(".gitignore"), GITIGNORE_TEMPLATE),
            (manifest.architecture_doc_path, ARCHITECTURE_TEMPLATE),
            (Path("README.md"), README_TEMPLATE),
            (Path("pyproject.toml"), PYPROJECT_TEMPLATE),
            (src_root / "__init__.py", PACKAGE_INIT_TEMPLATE),
            (manifest.root_main_path, MAIN_TEMPLATE),
            (manifest.domain_dir / "__init__.py", DOMAIN_INIT_TEMPLATE),
            (manifest.domain_ports_dir / "__init__.py", DOMAIN_PORTS_INIT_TEMPLATE),
            (
                manifest.domain_dir / "greeting_profile.py",
                GREETING_PROFILE_TEMPLATE,
            ),
            (
                manifest.domain_ports_dir / "greeting_profile_repository.py",
                GREETING_PROFILE_REPOSITORY_TEMPLATE,
            ),
            (manifest.application_dir / "__init__.py", APPLICATION_INIT_TEMPLATE),
            (
                manifest.application_ports_dir / "__init__.py",
                APPLICATION_PORTS_INIT_TEMPLATE,
            ),
            (manifest.services_dir / "__init__.py", SERVICES_INIT_TEMPLATE),
            (manifest.services_dir / "greeting.py", GREETING_SERVICE_TEMPLATE),
            (manifest.infrastructure_dir / "__init__.py", INFRASTRUCTURE_INIT_TEMPLATE),
            (
                manifest.infrastructure_repositories_dir / "__init__.py",
                INFRASTRUCTURE_REPOSITORIES_INIT_TEMPLATE,
            ),
            (
                manifest.infrastructure_repositories_dir
                / "static_greeting_profile_repository.py",
                STATIC_GREETING_PROFILE_REPOSITORY_TEMPLATE,
            ),
            (manifest.config_path, CONFIG_TEMPLATE),
            (manifest.container_path, CONTAINER_TEMPLATE),
            (manifest.presentation_dir / "__init__.py", PRESENTATION_INIT_TEMPLATE),
            (manifest.api_path, PRESENTATION_API_TEMPLATE),
            (manifest.bot_path, BOT_TEMPLATE),
            (manifest.widget_support_path, WIDGET_SUPPORT_TEMPLATE),
            (manifest.commands_init_path, COMMANDS_INIT_TEMPLATE),
            (manifest.commands_dir / "common.py", COMMON_COMMANDS_TEMPLATE),
            (manifest.tests_conftest_path, TESTS_CONFTEST_TEMPLATE),
            (manifest.architecture_test_path, ARCHITECTURE_TEST_TEMPLATE),
            (manifest.tests_dir / "test_start_command.py", TEST_START_COMMAND_TEMPLATE),
        ]
    else:
        template_items = [
            (Path(".env.example"), ENV_EXAMPLE_FSM_TEMPLATE),
            (Path(".gitignore"), GITIGNORE_TEMPLATE),
            (manifest.architecture_doc_path, ARCHITECTURE_TEMPLATE),
            (Path("README.md"), README_FSM_TEMPLATE),
            (Path("pyproject.toml"), PYPROJECT_FSM_TEMPLATE),
            (src_root / "__init__.py", PACKAGE_INIT_TEMPLATE),
            (manifest.root_main_path, MAIN_FSM_TEMPLATE),
            (manifest.domain_dir / "__init__.py", DOMAIN_INIT_TEMPLATE),
            (manifest.domain_ports_dir / "__init__.py", DOMAIN_PORTS_INIT_TEMPLATE),
            (
                manifest.domain_dir / "greeting_profile.py",
                GREETING_PROFILE_TEMPLATE,
            ),
            (
                manifest.domain_ports_dir / "greeting_profile_repository.py",
                GREETING_PROFILE_REPOSITORY_TEMPLATE,
            ),
            (manifest.application_dir / "__init__.py", APPLICATION_INIT_TEMPLATE),
            (
                manifest.application_ports_dir / "__init__.py",
                APPLICATION_PORTS_INIT_TEMPLATE,
            ),
            (manifest.services_dir / "__init__.py", SERVICES_INIT_TEMPLATE),
            (manifest.services_dir / "auth.py", AUTH_SERVICE_TEMPLATE),
            (manifest.services_dir / "greeting.py", GREETING_SERVICE_TEMPLATE),
            (manifest.infrastructure_dir / "__init__.py", INFRASTRUCTURE_INIT_TEMPLATE),
            (
                manifest.infrastructure_repositories_dir / "__init__.py",
                INFRASTRUCTURE_REPOSITORIES_INIT_TEMPLATE,
            ),
            (
                manifest.infrastructure_repositories_dir
                / "static_greeting_profile_repository.py",
                STATIC_GREETING_PROFILE_REPOSITORY_TEMPLATE,
            ),
            (manifest.config_path, CONFIG_FSM_TEMPLATE),
            (manifest.container_path, CONTAINER_FSM_TEMPLATE),
            (manifest.fsm_state_repo_path, FSM_STATE_REPO_TEMPLATE),
            (manifest.presentation_dir / "__init__.py", PRESENTATION_INIT_TEMPLATE),
            (manifest.api_path, PRESENTATION_API_FSM_TEMPLATE),
            (manifest.bot_path, BOT_FSM_TEMPLATE),
            (manifest.widget_support_path, WIDGET_SUPPORT_TEMPLATE),
            (manifest.commands_init_path, COMMANDS_INIT_FSM_TEMPLATE),
            (manifest.commands_dir / "common.py", COMMON_COMMANDS_FSM_TEMPLATE),
            (manifest.fsm_dir / "__init__.py", FSM_INIT_TEMPLATE),
            (manifest.fsm_dir / "login.py", FSM_LOGIN_TEMPLATE),
            (manifest.tests_conftest_path, TESTS_CONFTEST_FSM_TEMPLATE),
            (manifest.architecture_test_path, ARCHITECTURE_TEST_TEMPLATE),
            (manifest.tests_dir / "test_start_command.py", TEST_START_COMMAND_FSM_TEMPLATE),
        ]
    if include_docker:
        template_items.extend(
            [
                (Path("Dockerfile"), DOCKERFILE_TEMPLATE),
                (Path("docker-compose.yml"), DOCKER_COMPOSE_TEMPLATE),
            ],
        )
    return tuple(template_items)
