from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


PROJECT_MANIFEST_FILENAME = ".pybotx-project.json"
PROJECT_MANIFEST_SCHEMA_VERSION = 1
PROJECT_LAYOUT_FLAT = "flat-v1"
PROJECT_LAYOUT_CLEAN_ARCHITECTURE = "clean-architecture-v1"


@dataclass(frozen=True, slots=True)
class ScaffoldProjectManifest:
    template: str
    package_name: str
    layout: str = PROJECT_LAYOUT_FLAT
    schema_version: int = PROJECT_MANIFEST_SCHEMA_VERSION

    def write(self, root_dir: Path) -> Path:
        manifest_path = root_dir / PROJECT_MANIFEST_FILENAME
        manifest_path.write_text(
            json.dumps(asdict(self), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest_path

    @classmethod
    def load(cls, root_dir: Path) -> "ScaffoldProjectManifest":
        manifest_path = root_dir / PROJECT_MANIFEST_FILENAME
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != PROJECT_MANIFEST_SCHEMA_VERSION:
            raise RuntimeError(
                "Unsupported scaffold manifest schema version "
                f"`{payload.get('schema_version')}`",
            )
        return cls(**payload)

    @property
    def src_package_dir(self) -> Path:
        return Path("src") / self.package_name

    @property
    def commands_dir(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "presentation" / "commands"
        return self.src_package_dir / "commands"

    @property
    def commands_init_path(self) -> Path:
        return self.commands_dir / "__init__.py"

    @property
    def fsm_dir(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "presentation" / "fsm"
        return self.src_package_dir / "fsm"

    @property
    def widget_support_path(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "presentation" / "widget_support.py"
        return self.src_package_dir / "widget_support.py"

    @property
    def services_dir(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "application" / "services"
        return self.src_package_dir / "services"

    @property
    def bot_path(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "presentation" / "bot.py"
        return self.src_package_dir / "bot.py"

    @property
    def container_path(self) -> Path:
        return self.src_package_dir / "container.py"

    @property
    def config_path(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "infrastructure" / "config.py"
        return self.src_package_dir / "config.py"

    @property
    def api_path(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "presentation" / "api.py"
        return self.src_package_dir / "main.py"

    @property
    def fsm_state_repo_path(self) -> Path:
        if self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE:
            return self.src_package_dir / "infrastructure" / "fsm_state_repo.py"
        return self.src_package_dir / "fsm_state_repo.py"

    @property
    def architecture_doc_path(self) -> Path:
        return Path("ARCHITECTURE.md")

    @property
    def root_main_path(self) -> Path:
        return self.src_package_dir / "main.py"

    @property
    def domain_dir(self) -> Path:
        return self.src_package_dir / "domain"

    @property
    def application_dir(self) -> Path:
        return self.src_package_dir / "application"

    @property
    def application_ports_dir(self) -> Path:
        return self.application_dir / "ports"

    @property
    def infrastructure_dir(self) -> Path:
        return self.src_package_dir / "infrastructure"

    @property
    def infrastructure_repositories_dir(self) -> Path:
        return self.infrastructure_dir / "repositories"

    @property
    def presentation_dir(self) -> Path:
        return self.src_package_dir / "presentation"

    @property
    def domain_ports_dir(self) -> Path:
        return self.domain_dir / "ports"

    @property
    def commands_module_prefix(self) -> str:
        return self._module_for_dir(self.commands_dir)

    @property
    def services_module_prefix(self) -> str:
        return self._module_for_dir(self.services_dir)

    @property
    def fsm_module_prefix(self) -> str:
        return self._module_for_dir(self.fsm_dir)

    @property
    def container_module(self) -> str:
        return self._module_for_file(self.container_path)

    @property
    def widget_support_module(self) -> str:
        return self._module_for_file(self.widget_support_path)

    @property
    def bot_module(self) -> str:
        return self._module_for_file(self.bot_path)

    @property
    def config_module(self) -> str:
        return self._module_for_file(self.config_path)

    @property
    def api_module(self) -> str:
        return self._module_for_file(self.api_path)

    @property
    def fsm_state_repo_module(self) -> str:
        return self._module_for_file(self.fsm_state_repo_path)

    @property
    def root_main_module(self) -> str:
        return self._module_for_file(self.root_main_path)

    @property
    def uses_clean_architecture(self) -> bool:
        return self.layout == PROJECT_LAYOUT_CLEAN_ARCHITECTURE

    def _module_for_dir(self, path: Path) -> str:
        return ".".join(path.parts[1:])

    def _module_for_file(self, path: Path) -> str:
        suffixless_path = path.with_suffix("")
        if suffixless_path.name == "__init__":
            return ".".join(suffixless_path.parts[1:-1])
        return ".".join(suffixless_path.parts[1:])

    @property
    def architecture_test_path(self) -> Path:
        return self.tests_dir / "test_architecture.py"

    @property
    def layer_paths(self) -> dict[str, Path]:
        return {
            "domain": self.domain_dir,
            "application": self.application_dir,
            "infrastructure": self.infrastructure_dir,
            "presentation": self.presentation_dir,
        }

    @property
    def tests_conftest_path(self) -> Path:
        return self.tests_dir / "conftest.py"

    @property
    def tests_dir(self) -> Path:
        return Path("tests")


def find_scaffold_project_root(start_dir: Path | str) -> Path:
    current_path = Path(start_dir).expanduser().resolve()
    if current_path.is_file():
        current_path = current_path.parent

    for candidate in (current_path, *current_path.parents):
        if (candidate / PROJECT_MANIFEST_FILENAME).is_file():
            return candidate

    raise FileNotFoundError(
        "Couldn't find `.pybotx-project.json`. "
        "Run the command inside a project generated by `pybotx create bot`.",
    )
