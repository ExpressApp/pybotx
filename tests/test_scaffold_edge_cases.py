from argparse import Namespace
import importlib.metadata
from pathlib import Path
import runpy
from types import SimpleNamespace
from typing import Any

import pytest

from pybotx import cli
from pybotx.scaffold import CreateBotProjectOptions, create_bot_project
from pybotx.scaffold import _shared, fsm_flow, manifest, project, repository, widget
from pybotx.scaffold import widget_flow


@pytest.mark.parametrize(
    ("argv", "factory_name"),
    [
        (["create", "command", "name"], "create_command_in_project"),
        (["create", "port", "name"], "create_port_in_project"),
        (["create", "repository", "name"], "create_repository_in_project"),
        (["create", "service", "name"], "create_service_in_project"),
        (["create", "fsm-flow", "name"], "create_fsm_flow_in_project"),
        (["create", "widget", "name"], "create_widget_in_project"),
        (["create", "widget-flow", "name"], "create_widget_flow_in_project"),
    ],
)
def test__cli_create_handlers__report_scaffold_errors(
    argv: list[str],
    factory_name: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail(_options: object) -> None:
        raise ValueError("invalid scaffold")

    monkeypatch.setattr(cli, factory_name, fail)

    assert cli.main(argv) == 1
    assert "Error: invalid scaffold" in capsys.readouterr().err


def test__cli_main__returns_fallback_when_parser_error_returns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parser = SimpleNamespace(
        parse_args=lambda _argv: Namespace(command=None),
        error=lambda _message: None,
    )
    monkeypatch.setattr(cli, "build_parser", lambda: parser)

    assert cli.main([]) == 2


def test__cli_module__is_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["pybotx", "--help"])

    with pytest.raises(SystemExit, match="0"):
        runpy.run_module("pybotx.cli", run_name="__main__")


@pytest.mark.parametrize("raw_name", ["", "1-name", "class"])
def test__normalize_scaffold_name__rejects_invalid_names(raw_name: str) -> None:
    with pytest.raises(ValueError):
        _shared.normalize_scaffold_name(raw_name, kind="Name")


def test__normalize_scaffold_name__rejects_non_identifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(_shared, "slug_to_module_name", lambda _name: "not-valid")

    with pytest.raises(ValueError, match="Invalid"):
        _shared.normalize_scaffold_name("name", kind="Name")


@pytest.mark.parametrize(
    "content",
    ["plain text", "# end\n# start\n"],
)
def test__append_marked_lines__rejects_invalid_markers(
    tmp_path: Path,
    content: str,
) -> None:
    path = tmp_path / "module.py"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(RuntimeError):
        _shared.append_marked_lines(
            path,
            start_marker="# start",
            end_marker="# end",
            new_lines=["line"],
        )


def test__append_marked_lines__rejects_duplicate(tmp_path: Path) -> None:
    path = tmp_path / "module.py"
    path.write_text("# start\nline\n# end", encoding="utf-8")

    with pytest.raises(FileExistsError):
        _shared.append_marked_lines(
            path,
            start_marker="# start",
            end_marker="# end",
            new_lines=["line"],
        )


def test__flat_manifest__exposes_flat_paths_and_modules() -> None:
    item = manifest.ScaffoldProjectManifest(template="legacy", package_name="sample")

    assert item.commands_dir == Path("src/sample/commands")
    assert item.fsm_dir == Path("src/sample/fsm")
    assert item.widget_support_path == Path("src/sample/widget_support.py")
    assert item.services_dir == Path("src/sample/services")
    assert item.bot_path == Path("src/sample/bot.py")
    assert item.config_path == Path("src/sample/config.py")
    assert item.api_path == Path("src/sample/main.py")
    assert item.fsm_state_repo_path == Path("src/sample/fsm_state_repo.py")
    assert item.root_main_module == "sample.main"
    assert item.uses_clean_architecture is False
    assert item._module_for_file(Path("src/sample/__init__.py")) == "sample"
    assert set(item.layer_paths) == {
        "domain",
        "application",
        "infrastructure",
        "presentation",
    }


def test__manifest_load__rejects_unknown_schema(tmp_path: Path) -> None:
    (tmp_path / manifest.PROJECT_MANIFEST_FILENAME).write_text(
        '{"schema_version": 999, "template": "x", "package_name": "x"}',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="Unsupported scaffold manifest"):
        manifest.ScaffoldProjectManifest.load(tmp_path)


def test__find_scaffold_project_root__supports_file_and_not_found(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    source = project_dir / "source.py"
    source.write_text("", encoding="utf-8")
    (project_dir / manifest.PROJECT_MANIFEST_FILENAME).write_text("{}", encoding="utf-8")

    assert manifest.find_scaffold_project_root(source) == project_dir
    with pytest.raises(FileNotFoundError):
        manifest.find_scaffold_project_root(tmp_path / "missing")


def test__project_validation_edge_cases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match="Unsupported template"):
        project._validate_template("unknown")

    target_file = tmp_path / "target"
    target_file.write_text("", encoding="utf-8")
    with pytest.raises(FileExistsError, match="isn't a directory"):
        project._ensure_target_dir_is_safe(target_file)

    for raw_name in ("", "class"):
        with pytest.raises(ValueError):
            project._normalize_package_name(raw_name)

    class InvalidRegex:
        def sub(self, *_args: Any) -> str:
            return "not-valid"

    monkeypatch.setattr(project, "_NON_ALNUM_RE", InvalidRegex())
    with pytest.raises(ValueError, match="Invalid package"):
        project._normalize_package_name("name")


def test__project_name_and_display_name_cannot_be_derived(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(project, "_ensure_target_dir_is_safe", lambda _path: None)
    with pytest.raises(ValueError, match="Project name"):
        create_bot_project(CreateBotProjectOptions(target_dir=Path("/")))

    with pytest.raises(ValueError, match="Display name"):
        project._build_display_name("---")


def test__resolve_pybotx_version__falls_back_to_pyproject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing(_name: str) -> str:
        raise importlib.metadata.PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", missing)
    assert project._resolve_pybotx_version()

    monkeypatch.setattr(project, "_VERSION_RE", SimpleNamespace(search=lambda _text: None))
    with pytest.raises(RuntimeError, match="current pybotx version"):
        project._resolve_pybotx_version()


def test__fsm_flow_edge_cases(tmp_path: Path) -> None:
    spec = fsm_flow._build_fsm_flow_spec(
        flow_name="approval",
        command_name=None,
        description=None,
        initial_prompt=None,
        completion_text="Done",
    )
    assert spec.completion_statement == "await bot.answer_message('Done')"

    current_import = "from pkg.presentation.fsm.login import fsm as login_fsm"
    legacy_import = "from pkg.fsm.login import fsm as login_fsm"
    middleware = '        middlewares=[FSMMiddleware([login_fsm], state_repo_key="fsm_state_repo")],'
    for import_line in (legacy_import,):
        path = tmp_path / "legacy.py"
        path.write_text(f"{import_line}\n{middleware}\n", encoding="utf-8")
        fsm_flow._ensure_fsm_markers(
            path,
            fsm_module_prefix="pkg.presentation.fsm",
            package_name="pkg",
        )
        assert fsm_flow._FSM_IMPORTS_START in path.read_text(encoding="utf-8")

    broken = tmp_path / "broken.py"
    broken.write_text(current_import, encoding="utf-8")
    with pytest.raises(RuntimeError, match="Couldn't enable FSM"):
        fsm_flow._ensure_fsm_markers(
            broken,
            fsm_module_prefix="pkg.presentation.fsm",
            package_name="pkg",
        )


def test__create_fsm_flow__rejects_duplicate_artifact(tmp_path: Path) -> None:
    target_dir = tmp_path / "fsm-bot"
    create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            template="production-fastapi-fsm",
        ),
    )
    options = fsm_flow.CreateFSMFlowOptions(flow_name="approval", project_dir=target_dir)
    fsm_flow.create_fsm_flow_in_project(options)

    with pytest.raises(FileExistsError):
        fsm_flow.create_fsm_flow_in_project(options)


def test__fsm_marker_upgrade_rejects_missing_import(tmp_path: Path) -> None:
    path = tmp_path / "broken.py"
    path.write_text(
        '        middlewares=[FSMMiddleware([login_fsm], state_repo_key="fsm_state_repo")],',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="Couldn't enable FSM"):
        fsm_flow._ensure_fsm_markers(
            path,
            fsm_module_prefix="pkg.presentation.fsm",
            package_name="pkg",
        )


def test__widget_flow_variants_and_mock_upgrade(tmp_path: Path) -> None:
    for kind in ("approval", "search-select", "select"):
        spec = widget_flow._build_widget_flow_spec(
            flow_name="release",
            kind=kind,
            command_name=None,
            description=None,
        )
        assert spec.kind == kind
        assert len(widget_flow._select_widget_flow_templates(kind)) == 4

    conftest = tmp_path / "conftest.py"
    conftest.write_text(widget_flow._ANSWER_MESSAGE_MOCK, encoding="utf-8")
    widget_flow._ensure_widget_test_mocks(conftest)
    assert widget_flow._SEND_MESSAGE_MOCK in conftest.read_text(encoding="utf-8")

    broken = tmp_path / "broken.py"
    broken.write_text("", encoding="utf-8")
    with pytest.raises(RuntimeError, match="widget test support"):
        widget_flow._ensure_widget_test_mocks(broken)
    with pytest.raises(RuntimeError, match="widget test support"):
        widget._ensure_widget_test_mocks(broken)


def test__widget_flow__creates_missing_widget_support(tmp_path: Path) -> None:
    target_dir = tmp_path / "bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    support_path = target_dir / "src" / "bot" / "presentation" / "widget_support.py"
    support_path.unlink()

    result = widget_flow.create_widget_flow_in_project(
        widget_flow.CreateWidgetFlowOptions(
            flow_name="approval",
            project_dir=target_dir,
        ),
    )

    assert support_path in result.created_files


def test__repository_marker_resolution__supports_fallback_and_errors(
    tmp_path: Path,
) -> None:
    path = tmp_path / "container.py"
    path.write_text("fallback-start\nfallback-end\n", encoding="utf-8")
    assert repository._resolve_container_markers(
        path,
        preferred_start="preferred-start",
        preferred_end="preferred-end",
        fallback_start="fallback-start",
        fallback_end="fallback-end",
    ) == ("fallback-start", "fallback-end")

    path.write_text("", encoding="utf-8")
    with pytest.raises(RuntimeError, match="scaffold markers"):
        repository._resolve_container_markers(
            path,
            preferred_start="preferred-start",
            preferred_end="preferred-end",
            fallback_start="fallback-start",
            fallback_end="fallback-end",
        )

    spec = repository._build_repository_spec(
        repository_name="sql-users",
        port_name="users-repository",
    )
    assert spec.port_class_name == "UsersRepository"
