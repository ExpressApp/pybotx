from pathlib import Path

import pytest

from pybotx.cli import main
from pybotx.scaffold import (
    CreateBotProjectOptions,
    CreateCommandOptions,
    CreateFSMFlowOptions,
    CreatePortOptions,
    CreateRepositoryOptions,
    CreateServiceOptions,
    CreateWidgetOptions,
    CreateWidgetFlowOptions,
    PROJECT_MANIFEST_FILENAME,
    create_bot_project,
    create_command_in_project,
    create_fsm_flow_in_project,
    create_port_in_project,
    create_repository_in_project,
    create_service_in_project,
    create_widget_in_project,
    create_widget_flow_in_project,
)


def _package_dir(root_dir: Path, package_name: str) -> Path:
    return root_dir / "src" / package_name


def test__create_bot_project__creates_expected_file_tree(tmp_path: Path) -> None:
    target_dir = tmp_path / "my-bot"

    result = create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    assert result.root_dir == target_dir
    assert result.project_name == "my-bot"
    assert result.package_name == "my_bot"
    assert (target_dir / PROJECT_MANIFEST_FILENAME).is_file()
    assert (target_dir / ".env.example").is_file()
    assert (target_dir / ".gitignore").is_file()
    assert (target_dir / "README.md").is_file()
    assert (target_dir / "ARCHITECTURE.md").is_file()
    assert (target_dir / "pyproject.toml").is_file()
    assert (target_dir / "Dockerfile").is_file()
    assert (target_dir / "docker-compose.yml").is_file()
    assert (package_dir / "main.py").is_file()
    assert (package_dir / "container.py").is_file()
    assert (package_dir / "domain" / "__init__.py").is_file()
    assert (package_dir / "domain" / "greeting_profile.py").is_file()
    assert (package_dir / "domain" / "ports" / "__init__.py").is_file()
    assert (
        package_dir / "domain" / "ports" / "greeting_profile_repository.py"
    ).is_file()
    assert (package_dir / "application" / "__init__.py").is_file()
    assert (package_dir / "application" / "ports" / "__init__.py").is_file()
    assert (package_dir / "application" / "services" / "__init__.py").is_file()
    assert (package_dir / "application" / "services" / "greeting.py").is_file()
    assert (package_dir / "infrastructure" / "__init__.py").is_file()
    assert (package_dir / "infrastructure" / "config.py").is_file()
    assert (package_dir / "infrastructure" / "repositories" / "__init__.py").is_file()
    assert (
        package_dir
        / "infrastructure"
        / "repositories"
        / "static_greeting_profile_repository.py"
    ).is_file()
    assert (package_dir / "presentation" / "__init__.py").is_file()
    assert (package_dir / "presentation" / "api.py").is_file()
    assert (package_dir / "presentation" / "bot.py").is_file()
    assert (package_dir / "presentation" / "widget_support.py").is_file()
    assert (package_dir / "presentation" / "commands" / "__init__.py").is_file()
    assert (package_dir / "presentation" / "commands" / "common.py").is_file()
    assert (target_dir / "tests" / "conftest.py").is_file()
    assert (target_dir / "tests" / "test_architecture.py").is_file()
    assert (target_dir / "tests" / "test_start_command.py").is_file()

    pyproject_content = (target_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "my-bot"' in pyproject_content
    assert '"pybotx==' in pyproject_content
    assert '"dependency-injector>=4.48.1,<5"' in pyproject_content
    assert '"opentelemetry-api>=1.38.0,<2"' in pyproject_content

    commands_init_content = (
        package_dir / "presentation" / "commands" / "__init__.py"
    ).read_text(encoding="utf-8")
    assert "# pybotx-scaffold command imports start" in commands_init_content
    assert "# pybotx-scaffold command collectors start" in commands_init_content

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert "StaticGreetingProfileRepository" in container_content
    assert "# pybotx-scaffold repository imports start" in container_content
    assert "# pybotx-scaffold repository providers start" in container_content
    assert "greeting_profile_repository = providers.Singleton(" in container_content
    assert "greeting_profile_repository=greeting_profile_repository" in container_content
    assert "# pybotx-scaffold service imports start" in container_content
    assert "# pybotx-scaffold service providers start" in container_content

    greeting_service_content = (
        package_dir / "application" / "services" / "greeting.py"
    ).read_text(encoding="utf-8")
    assert "GreetingProfileRepository" in greeting_service_content
    assert "self.greeting_profile_repository.get_profile()" in greeting_service_content

    greeting_repository_content = (
        package_dir / "domain" / "ports" / "greeting_profile_repository.py"
    ).read_text(encoding="utf-8")
    assert "class GreetingProfileRepository(Protocol):" in greeting_repository_content

    static_repository_content = (
        package_dir
        / "infrastructure"
        / "repositories"
        / "static_greeting_profile_repository.py"
    ).read_text(encoding="utf-8")
    assert "class StaticGreetingProfileRepository:" in static_repository_content
    assert "return GreetingProfile(" in static_repository_content

    main_content = (package_dir / "main.py").read_text(encoding="utf-8")
    assert "from my_bot.presentation.api import create_app" in main_content

    api_content = (package_dir / "presentation" / "api.py").read_text(
        encoding="utf-8",
    )
    assert "create_fastapi_bot_app" in api_content
    assert "FastAPIBotAppConfig(" in api_content
    assert 'metrics_path="/metrics"' in api_content

    architecture_content = (target_dir / "ARCHITECTURE.md").read_text(
        encoding="utf-8",
    )
    assert "4-layer clean architecture" in architecture_content
    assert "src/my_bot/container.py" in architecture_content
    assert "presentation -> application -> domain" in architecture_content
    assert "GreetingProfileRepository" in architecture_content

    conftest_content = (target_dir / "tests" / "conftest.py").read_text(
        encoding="utf-8",
    )
    assert "from my_bot.presentation.commands import collectors" in conftest_content
    assert "from my_bot.container import ApplicationContainer" in conftest_content
    assert "built_bot.send = AsyncMock" in conftest_content
    assert "built_bot.edit_message = AsyncMock()" in conftest_content


def test__create_bot_project__supports_explicit_names_and_without_docker(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "generated"

    result = create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            project_name="customer-bot",
            package_name="customer_bot",
            display_name="Customer Support Bot",
            description="Customer support bot",
            enable_otel_tracing=True,
            include_docker=False,
        ),
    )

    assert result.project_name == "customer-bot"
    assert result.package_name == "customer_bot"
    assert not (target_dir / "Dockerfile").exists()
    assert not (target_dir / "docker-compose.yml").exists()

    env_content = (target_dir / ".env.example").read_text(encoding="utf-8")
    assert 'BOT_DISPLAY_NAME="Customer Support Bot"' in env_content
    assert 'BOT_ENABLE_OTEL_TRACING="true"' in env_content

    readme_content = (target_dir / "README.md").read_text(encoding="utf-8")
    assert "# customer-bot" in readme_content
    assert "ARCHITECTURE.md" in readme_content
    assert "create port" in readme_content
    assert "create repository" in readme_content
    assert "create fsm-flow" not in readme_content
    assert "create widget" in readme_content


def test__create_bot_project__creates_fsm_template(tmp_path: Path) -> None:
    target_dir = tmp_path / "fsm-bot"

    result = create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            template="production-fastapi-fsm",
        ),
    )
    package_dir = _package_dir(target_dir, "fsm_bot")

    assert result.template == "production-fastapi-fsm"
    assert (target_dir / "ARCHITECTURE.md").is_file()
    assert (package_dir / "presentation" / "fsm" / "__init__.py").is_file()
    assert (package_dir / "presentation" / "fsm" / "login.py").is_file()
    assert (package_dir / "infrastructure" / "fsm_state_repo.py").is_file()
    assert (
        package_dir / "infrastructure" / "repositories" / "static_greeting_profile_repository.py"
    ).is_file()
    assert (
        package_dir / "domain" / "ports" / "greeting_profile_repository.py"
    ).is_file()
    assert (package_dir / "application" / "services" / "auth.py").is_file()
    assert (package_dir / "presentation" / "widget_support.py").is_file()

    pyproject_content = (target_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert '"pybotx-fsm>=0.6.1,<0.7"' in pyproject_content
    assert '"redis>=5.0.0,<6"' in pyproject_content

    env_content = (target_dir / ".env.example").read_text(encoding="utf-8")
    assert 'BOT_FSM_REDIS_URL="redis://localhost:6379/0"' in env_content

    bot_content = (package_dir / "presentation" / "bot.py").read_text(encoding="utf-8")
    assert "FSMMiddleware" in bot_content
    assert 'state_repo_key="fsm_state_repo"' in bot_content
    assert "# pybotx-scaffold fsm imports start" in bot_content
    assert "# pybotx-scaffold fsm collectors start" in bot_content

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert "StaticGreetingProfileRepository" in container_content
    assert "# pybotx-scaffold repository imports start" in container_content
    assert "# pybotx-scaffold repository providers start" in container_content
    assert "greeting_profile_repository = providers.Singleton(" in container_content

    api_content = (package_dir / "presentation" / "api.py").read_text(
        encoding="utf-8",
    )
    assert "fsm_redis" in api_content
    assert "ReadinessCheck(" in api_content

    conftest_content = (target_dir / "tests" / "conftest.py").read_text(
        encoding="utf-8",
    )
    assert "from fsm_bot.presentation.commands import collectors" in conftest_content
    assert "from fsm_bot.presentation.fsm.login import fsm as login_fsm" in (
        conftest_content
    )
    assert "# pybotx-scaffold fsm imports start" in conftest_content
    assert "# pybotx-scaffold fsm collectors start" in conftest_content
    assert "built_bot.send = AsyncMock" in conftest_content
    assert "built_bot.edit_message = AsyncMock()" in conftest_content

    readme_content = (target_dir / "README.md").read_text(encoding="utf-8")
    assert "create port" in readme_content
    assert "create repository" in readme_content
    assert "create widget" in readme_content
    assert "create fsm-flow" in readme_content


def test__create_command_in_project__creates_expected_artifacts(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_command_in_project(
        CreateCommandOptions(
            command_name="ping-users",
            project_dir=target_dir,
        ),
    )

    assert result.command_path == "/ping-users"
    assert (package_dir / "presentation" / "commands" / "ping_users.py").is_file()
    assert (package_dir / "application" / "services" / "ping_users.py").is_file()
    assert (target_dir / "tests" / "test_ping_users.py").is_file()

    commands_init_content = (
        package_dir / "presentation" / "commands" / "__init__.py"
    ).read_text(encoding="utf-8")
    assert (
        "from my_bot.presentation.commands.ping_users import collector as ping_users_collector"
        in commands_init_content
    )
    assert "ping_users_collector," in commands_init_content

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert (
        "from my_bot.application.services.ping_users import PingUsersService"
        in container_content
    )
    assert "ping_users_service = providers.Factory(PingUsersService)" in container_content

    command_content = (
        package_dir / "presentation" / "commands" / "ping_users.py"
    ).read_text(encoding="utf-8")
    assert "@collector.command(" in command_content
    assert "/ping-users" in command_content
    assert "ping_users_service()" in command_content
    assert "from my_bot.container import ApplicationContainer" in command_content


def test__create_command_in_project__works_for_fsm_template(tmp_path: Path) -> None:
    target_dir = tmp_path / "fsm-bot"
    create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            template="production-fastapi-fsm",
        ),
    )
    package_dir = _package_dir(target_dir, "fsm_bot")

    result = create_command_in_project(
        CreateCommandOptions(command_name="/ping-users", project_dir=target_dir),
    )

    assert result.command_path == "/ping-users"

    commands_init_content = (
        package_dir / "presentation" / "commands" / "__init__.py"
    ).read_text(encoding="utf-8")
    assert "login_fsm" in commands_init_content
    assert "ping_users_collector" in commands_init_content


def test__create_command_in_project__rejects_duplicate_command(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    create_command_in_project(
        CreateCommandOptions(command_name="ping-users", project_dir=target_dir),
    )

    with pytest.raises(FileExistsError):
        create_command_in_project(
            CreateCommandOptions(command_name="ping-users", project_dir=target_dir),
        )


def test__create_service_in_project__creates_expected_artifacts(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_service_in_project(
        CreateServiceOptions(
            service_name="sync-users",
            project_dir=target_dir,
        ),
    )

    assert result.service_name == "sync_users"
    assert (package_dir / "application" / "services" / "sync_users.py").is_file()
    assert (target_dir / "tests" / "test_sync_users_service.py").is_file()

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert (
        "from my_bot.application.services.sync_users import SyncUsersService"
        in container_content
    )
    assert "sync_users_service = providers.Factory(SyncUsersService)" in container_content

    service_content = (
        package_dir / "application" / "services" / "sync_users.py"
    ).read_text(encoding="utf-8")
    assert "class SyncUsersService:" in service_content
    assert "return 'Implement sync-users service.'" in service_content

    test_content = (target_dir / "tests" / "test_sync_users_service.py").read_text(
        encoding="utf-8",
    )
    assert "from my_bot.application.services.sync_users import SyncUsersService" in test_content
    assert "assert service.handle() == 'Implement sync-users service.'" in test_content


def test__create_service_in_project__rejects_duplicate_service(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    create_service_in_project(
        CreateServiceOptions(service_name="sync-users", project_dir=target_dir),
    )

    with pytest.raises(FileExistsError):
        create_service_in_project(
            CreateServiceOptions(service_name="sync-users", project_dir=target_dir),
        )


def test__create_port_in_project__creates_expected_artifacts(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_port_in_project(
        CreatePortOptions(
            port_name="billing-gateway",
            project_dir=target_dir,
        ),
    )

    assert result.port_name == "billing_gateway"
    assert (package_dir / "domain" / "ports" / "billing_gateway.py").is_file()

    port_content = (
        package_dir / "domain" / "ports" / "billing_gateway.py"
    ).read_text(encoding="utf-8")
    assert "class BillingGatewayPort(Protocol):" in port_content
    assert "Domain port for `billing-gateway`." in port_content


def test__create_port_in_project__rejects_duplicate_port(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    create_port_in_project(
        CreatePortOptions(port_name="billing-gateway", project_dir=target_dir),
    )

    with pytest.raises(FileExistsError):
        create_port_in_project(
            CreatePortOptions(port_name="billing-gateway", project_dir=target_dir),
        )


def test__create_repository_in_project__creates_expected_artifacts(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_repository_in_project(
        CreateRepositoryOptions(
            repository_name="user-profile",
            project_dir=target_dir,
        ),
    )

    assert result.repository_name == "user_profile_repository"
    assert result.port_name == "user_profile_repository"
    assert (
        package_dir / "domain" / "ports" / "user_profile_repository.py"
    ).is_file()
    assert (
        package_dir
        / "infrastructure"
        / "repositories"
        / "stub_user_profile_repository.py"
    ).is_file()
    assert (target_dir / "tests" / "test_user_profile_repository.py").is_file()

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert (
        "from my_bot.infrastructure.repositories.stub_user_profile_repository "
        "import StubUserProfileRepository"
    ) in container_content
    assert (
        "user_profile_repository = providers.Singleton(StubUserProfileRepository)"
        in container_content
    )

    port_content = (
        package_dir / "domain" / "ports" / "user_profile_repository.py"
    ).read_text(encoding="utf-8")
    assert "class UserProfileRepository(Protocol):" in port_content

    repository_content = (
        package_dir
        / "infrastructure"
        / "repositories"
        / "stub_user_profile_repository.py"
    ).read_text(encoding="utf-8")
    assert "class StubUserProfileRepository:" in repository_content

    test_content = (target_dir / "tests" / "test_user_profile_repository.py").read_text(
        encoding="utf-8",
    )
    assert "container.user_profile_repository()" in test_content
    assert "isinstance(repository, StubUserProfileRepository)" in test_content


def test__create_repository_in_project__binds_to_existing_port(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")
    create_port_in_project(
        CreatePortOptions(
            port_name="billing-gateway",
            project_dir=target_dir,
        ),
    )

    result = create_repository_in_project(
        CreateRepositoryOptions(
            repository_name="stripe-billing-gateway",
            port_name="billing-gateway",
            project_dir=target_dir,
        ),
    )

    assert result.repository_name == "stripe_billing_gateway_repository"
    assert result.port_name == "billing_gateway"
    assert (
        package_dir
        / "infrastructure"
        / "repositories"
        / "stub_stripe_billing_gateway_repository.py"
    ).is_file()
    assert not (
        package_dir / "domain" / "ports" / "stripe_billing_gateway_repository.py"
    ).exists()
    assert (target_dir / "tests" / "test_stripe_billing_gateway_repository.py").is_file()

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert (
        "from my_bot.infrastructure.repositories.stub_stripe_billing_gateway_repository "
        "import StubStripeBillingGatewayRepository"
    ) in container_content
    assert (
        "billing_gateway = providers.Singleton(StubStripeBillingGatewayRepository)"
        in container_content
    )

    repository_content = (
        package_dir
        / "infrastructure"
        / "repositories"
        / "stub_stripe_billing_gateway_repository.py"
    ).read_text(encoding="utf-8")
    assert "the `BillingGatewayPort` port" in repository_content


def test__create_repository_in_project__rejects_missing_port(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    with pytest.raises(FileNotFoundError):
        create_repository_in_project(
            CreateRepositoryOptions(
                repository_name="stripe-billing-gateway",
                port_name="billing-gateway",
                project_dir=target_dir,
            ),
        )


def test__create_repository_in_project__rejects_duplicate_repository(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    create_repository_in_project(
        CreateRepositoryOptions(repository_name="user-profile", project_dir=target_dir),
    )

    with pytest.raises(FileExistsError):
        create_repository_in_project(
            CreateRepositoryOptions(repository_name="user-profile", project_dir=target_dir),
        )


def test__create_fsm_flow_in_project__creates_expected_artifacts(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "fsm-bot"
    create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            template="production-fastapi-fsm",
        ),
    )
    package_dir = _package_dir(target_dir, "fsm_bot")

    result = create_fsm_flow_in_project(
        CreateFSMFlowOptions(flow_name="approval-step", project_dir=target_dir),
    )

    assert result.flow_name == "approval-step"
    assert result.command_path == "/approval-step"
    assert (package_dir / "presentation" / "fsm" / "approval_step.py").is_file()
    assert (package_dir / "presentation" / "commands" / "approval_step.py").is_file()
    assert (target_dir / "tests" / "test_approval_step_fsm.py").is_file()

    flow_content = (
        package_dir / "presentation" / "fsm" / "approval_step.py"
    ).read_text(encoding="utf-8")
    assert "class ApprovalStepStates(Enum):" in flow_content
    assert "start_approval_step_flow" in flow_content

    command_content = (
        package_dir / "presentation" / "commands" / "approval_step.py"
    ).read_text(encoding="utf-8")
    assert (
        "from fsm_bot.presentation.fsm.approval_step import start_approval_step_flow"
        in command_content
    )
    assert "/approval-step" in command_content

    commands_init_content = (
        package_dir / "presentation" / "commands" / "__init__.py"
    ).read_text(encoding="utf-8")
    assert (
        "from fsm_bot.presentation.commands.approval_step import collector as approval_step_collector"
        in commands_init_content
    )
    assert "approval_step_collector," in commands_init_content

    bot_content = (package_dir / "presentation" / "bot.py").read_text(encoding="utf-8")
    assert (
        "from fsm_bot.presentation.fsm.approval_step import fsm as approval_step_fsm"
        in bot_content
    )
    assert "approval_step_fsm," in bot_content

    conftest_content = (target_dir / "tests" / "conftest.py").read_text(
        encoding="utf-8",
    )
    assert (
        "from fsm_bot.presentation.fsm.approval_step import fsm as approval_step_fsm"
        in conftest_content
    )
    assert "approval_step_fsm," in conftest_content


def test__create_fsm_flow_in_project__upgrades_legacy_fsm_scaffold(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "fsm-bot"
    create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            template="production-fastapi-fsm",
        ),
    )

    bot_path = target_dir / "src" / "fsm_bot" / "presentation" / "bot.py"
    bot_path.write_text(
        bot_path.read_text(encoding="utf-8")
        .replace(
            "\n# pybotx-scaffold fsm imports start\n# pybotx-scaffold fsm imports end",
            "",
        )
        .replace(
            "\n".join(
                [
                    "        middlewares=[",
                    "            FSMMiddleware(",
                    "                [",
                    "                    login_fsm,",
                    "                    # pybotx-scaffold fsm collectors start",
                    "                    # pybotx-scaffold fsm collectors end",
                    "                ],",
                    '                state_repo_key="fsm_state_repo",',
                    "            ),",
                    "        ],",
                ],
            ),
            '        middlewares=[FSMMiddleware([login_fsm], state_repo_key="fsm_state_repo")],',
        ),
        encoding="utf-8",
    )

    conftest_path = target_dir / "tests" / "conftest.py"
    conftest_path.write_text(
        conftest_path.read_text(encoding="utf-8")
        .replace(
            "\n# pybotx-scaffold fsm imports start\n# pybotx-scaffold fsm imports end",
            "",
        )
        .replace(
            "\n".join(
                [
                    "        middlewares=[",
                    "            FSMMiddleware(",
                    "                [",
                    "                    login_fsm,",
                    "                    # pybotx-scaffold fsm collectors start",
                    "                    # pybotx-scaffold fsm collectors end",
                    "                ],",
                    '                state_repo_key="fsm_state_repo",',
                    "            ),",
                    "        ],",
                ],
            ),
            '        middlewares=[FSMMiddleware([login_fsm], state_repo_key="fsm_state_repo")],',
        ),
        encoding="utf-8",
    )

    create_fsm_flow_in_project(
        CreateFSMFlowOptions(flow_name="legacy-flow", project_dir=target_dir),
    )

    upgraded_bot_content = bot_path.read_text(encoding="utf-8")
    assert "# pybotx-scaffold fsm imports start" in upgraded_bot_content
    assert "legacy_flow_fsm," in upgraded_bot_content

    upgraded_conftest_content = conftest_path.read_text(encoding="utf-8")
    assert "# pybotx-scaffold fsm collectors start" in upgraded_conftest_content
    assert "legacy_flow_fsm," in upgraded_conftest_content


def test__create_fsm_flow_in_project__rejects_non_fsm_template(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    with pytest.raises(ValueError, match="production-fastapi-fsm"):
        create_fsm_flow_in_project(
            CreateFSMFlowOptions(flow_name="approval", project_dir=target_dir),
        )


def test__create_widget_in_project__creates_confirm_widget_artifacts(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_widget_in_project(
        CreateWidgetOptions(
            widget_name="deployment-approval",
            project_dir=target_dir,
            kind="confirm",
        ),
    )

    assert result.widget_name == "deployment-approval"
    assert result.kind == "confirm"
    assert result.command_path == "/deployment-approval"
    assert (package_dir / "presentation" / "commands" / "deployment_approval.py").is_file()
    assert (package_dir / "application" / "services" / "deployment_approval.py").is_file()
    assert (target_dir / "tests" / "test_deployment_approval_widget.py").is_file()

    command_content = (
        package_dir / "presentation" / "commands" / "deployment_approval.py"
    ).read_text(encoding="utf-8")
    assert "build_widget_factory" in command_content
    assert "build_widget_runner_config" in command_content
    assert "return widgets.confirm(" in command_content
    assert "from my_bot.presentation.widget_support import (" in command_content

    service_content = (
        package_dir / "application" / "services" / "deployment_approval.py"
    ).read_text(encoding="utf-8")
    assert "class DeploymentApprovalWidgetService:" in service_content
    assert "Confirm deployment approval?" in service_content

    commands_init_content = (
        package_dir / "presentation" / "commands" / "__init__.py"
    ).read_text(encoding="utf-8")
    assert (
        "from my_bot.presentation.commands.deployment_approval import collector as deployment_approval_collector"
        in commands_init_content
    )
    assert "deployment_approval_collector," in commands_init_content

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert (
        "from my_bot.application.services.deployment_approval import DeploymentApprovalWidgetService"
        in container_content
    )
    assert (
        "deployment_approval_widget_service = providers.Factory(DeploymentApprovalWidgetService)"
        in container_content
    )


def test__create_widget_in_project__supports_select_widget_for_fsm_template(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "fsm-bot"
    create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            template="production-fastapi-fsm",
        ),
    )
    package_dir = _package_dir(target_dir, "fsm_bot")

    result = create_widget_in_project(
        CreateWidgetOptions(
            widget_name="environment-picker",
            project_dir=target_dir,
            kind="select",
        ),
    )

    assert result.kind == "select"
    command_content = (
        package_dir / "presentation" / "commands" / "environment_picker.py"
    ).read_text(encoding="utf-8")
    assert "return widgets.select(" in command_content
    assert "SELECT_VALUE_KEY" in command_content

    test_content = (target_dir / "tests" / "test_environment_picker_widget.py").read_text(
        encoding="utf-8",
    )
    assert 'message.data = {SELECT_VALUE_KEY: "prod"}' in test_content


def test__create_widget_in_project__supports_search_select_widget(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_widget_in_project(
        CreateWidgetOptions(
            widget_name="service-picker",
            project_dir=target_dir,
            kind="search-select",
        ),
    )

    assert result.kind == "search-select"
    command_content = (
        package_dir / "presentation" / "commands" / "service_picker.py"
    ).read_text(encoding="utf-8")
    assert "SearchSelectWidget" in command_content
    assert "return widgets.search_select(" in command_content

    test_content = (target_dir / "tests" / "test_service_picker_widget.py").read_text(
        encoding="utf-8",
    )
    assert 'message.data = {SELECT_VALUE_KEY: "prod"}' in test_content


def test__create_widget_in_project__supports_multi_select_widget(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_widget_in_project(
        CreateWidgetOptions(
            widget_name="environment-batch",
            project_dir=target_dir,
            kind="multi-select",
        ),
    )

    assert result.kind == "multi-select"
    command_content = (
        package_dir / "presentation" / "commands" / "environment_batch.py"
    ).read_text(encoding="utf-8")
    assert "MultiSelectWidget" in command_content
    assert "RunnerHookResult" in command_content
    assert "return widgets.multi_select(" in command_content

    service_content = (
        package_dir / "application" / "services" / "environment_batch.py"
    ).read_text(encoding="utf-8")
    assert "def max_selected(self) -> int:" in service_content
    assert "def is_selection_complete(self, values: list[str]) -> bool:" in (
        service_content
    )

    test_content = (target_dir / "tests" / "test_environment_batch_widget.py").read_text(
        encoding="utf-8",
    )
    assert "MULTI_SELECTED_VALUES_KEY" in test_content
    assert 'message.data = {MULTI_SELECT_VALUE_KEY: "prod"}' in test_content


def test__create_widget_in_project__supports_date_range_widget(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_widget_in_project(
        CreateWidgetOptions(
            widget_name="deployment-window",
            project_dir=target_dir,
            kind="date-range",
        ),
    )

    assert result.kind == "date-range"
    command_content = (
        package_dir / "presentation" / "commands" / "deployment_window.py"
    ).read_text(encoding="utf-8")
    assert "DateRangeWidget" in command_content
    assert "DATE_RANGE_SELECTED_DATE_KEY" in command_content
    assert "return widgets.date_range(" in command_content

    service_content = (
        package_dir / "application" / "services" / "deployment_window.py"
    ).read_text(encoding="utf-8")
    assert "from datetime import date" in service_content
    assert "def build_selection_result(self, start_date: date, end_date: date) -> str:" in (
        service_content
    )

    test_content = (target_dir / "tests" / "test_deployment_window_widget.py").read_text(
        encoding="utf-8",
    )
    assert "DATE_RANGE_START_KEY" in test_content
    assert 'message.data = {DATE_RANGE_SELECTED_DATE_KEY: "2026-03-08"}' in test_content


def test__create_widget_in_project__creates_widget_support_for_legacy_scaffold(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    widget_support_path = (
        target_dir / "src" / "my_bot" / "presentation" / "widget_support.py"
    )
    widget_support_path.unlink()

    conftest_path = target_dir / "tests" / "conftest.py"
    conftest_path.write_text(
        conftest_path.read_text(encoding="utf-8")
        .replace(
            '    built_bot.send = AsyncMock(return_value=uuid4())  # type: ignore[method-assign]\n',
            "",
        )
        .replace(
            "    built_bot.edit_message = AsyncMock()  # type: ignore[method-assign]\n",
            "",
        ),
        encoding="utf-8",
    )

    result = create_widget_in_project(
        CreateWidgetOptions(
            widget_name="legacy-widget",
            project_dir=target_dir,
            kind="approval",
        ),
    )

    assert widget_support_path in result.created_files
    assert widget_support_path.is_file()

    upgraded_conftest_content = conftest_path.read_text(encoding="utf-8")
    assert "built_bot.send = AsyncMock" in upgraded_conftest_content
    assert "built_bot.edit_message = AsyncMock()" in upgraded_conftest_content


def test__create_widget_flow_in_project__creates_confirm_flow_artifacts(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_widget_flow_in_project(
        CreateWidgetFlowOptions(
            flow_name="deployment-approval",
            project_dir=target_dir,
            kind="confirm",
        ),
    )

    assert result.flow_name == "deployment-approval"
    assert result.kind == "confirm"
    assert result.command_path == "/deployment-approval"
    assert (package_dir / "presentation" / "commands" / "deployment_approval.py").is_file()
    assert (
        package_dir / "application" / "services" / "deployment_approval_widget.py"
    ).is_file()
    assert (
        package_dir / "application" / "services" / "deployment_approval_result.py"
    ).is_file()
    assert (target_dir / "tests" / "test_deployment_approval_widget_flow.py").is_file()

    command_content = (
        package_dir / "presentation" / "commands" / "deployment_approval.py"
    ).read_text(encoding="utf-8")
    assert "deployment_approval_widget_service()" in command_content
    assert "deployment_approval_result_service()" in command_content
    assert "return widgets.confirm(" in command_content

    container_content = (package_dir / "container.py").read_text(encoding="utf-8")
    assert (
        "from my_bot.application.services.deployment_approval_widget import DeploymentApprovalWidgetService"
        in container_content
    )
    assert (
        "from my_bot.application.services.deployment_approval_result import DeploymentApprovalResultService"
        in container_content
    )
    assert (
        "deployment_approval_widget_service = providers.Factory(DeploymentApprovalWidgetService)"
        in container_content
    )
    assert (
        "deployment_approval_result_service = providers.Factory(DeploymentApprovalResultService)"
        in container_content
    )


def test__create_widget_flow_in_project__supports_multi_select_flow(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_widget_flow_in_project(
        CreateWidgetFlowOptions(
            flow_name="environment-batch",
            project_dir=target_dir,
            kind="multi-select",
        ),
    )

    assert result.kind == "multi-select"
    command_content = (
        package_dir / "presentation" / "commands" / "environment_batch.py"
    ).read_text(encoding="utf-8")
    assert "RunnerHookResult" in command_content
    assert "container.environment_batch_result_service().handle_selection" in command_content
    assert "return widgets.multi_select(" in command_content

    widget_service_content = (
        package_dir / "application" / "services" / "environment_batch_widget.py"
    ).read_text(encoding="utf-8")
    assert "def max_selected(self) -> int:" in widget_service_content

    result_service_content = (
        package_dir / "application" / "services" / "environment_batch_result.py"
    ).read_text(encoding="utf-8")
    assert "def handle_selection(self, values: list[str]) -> str:" in (
        result_service_content
    )


def test__create_widget_flow_in_project__supports_date_range_flow(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    package_dir = _package_dir(target_dir, "my_bot")

    result = create_widget_flow_in_project(
        CreateWidgetFlowOptions(
            flow_name="deployment-window",
            project_dir=target_dir,
            kind="date-range",
        ),
    )

    assert result.kind == "date-range"
    command_content = (
        package_dir / "presentation" / "commands" / "deployment_window.py"
    ).read_text(encoding="utf-8")
    assert "DateRangeWidget" in command_content
    assert "DATE_RANGE_SELECTED_DATE_KEY" in command_content
    assert ".handle_selection(widget.start, widget.end)" in command_content

    result_service_content = (
        package_dir / "application" / "services" / "deployment_window_result.py"
    ).read_text(encoding="utf-8")
    assert "from datetime import date" in result_service_content
    assert "def handle_selection(self, start_date: date, end_date: date) -> str:" in (
        result_service_content
    )


def test__create_widget_in_project__rejects_duplicate_widget(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    create_widget_in_project(
        CreateWidgetOptions(
            widget_name="deployment-approval",
            project_dir=target_dir,
        ),
    )

    with pytest.raises(FileExistsError):
        create_widget_in_project(
            CreateWidgetOptions(
                widget_name="deployment-approval",
                project_dir=target_dir,
            ),
        )


def test__create_widget_flow_in_project__rejects_duplicate_flow(
    tmp_path: Path,
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    create_widget_flow_in_project(
        CreateWidgetFlowOptions(
            flow_name="deployment-approval",
            project_dir=target_dir,
        ),
    )

    with pytest.raises(FileExistsError):
        create_widget_flow_in_project(
            CreateWidgetFlowOptions(
                flow_name="deployment-approval",
                project_dir=target_dir,
            ),
        )


def test__create_bot_project__rejects_non_empty_dir(tmp_path: Path) -> None:
    target_dir = tmp_path / "busy"
    target_dir.mkdir()
    (target_dir / "already.txt").write_text("occupied", encoding="utf-8")

    with pytest.raises(FileExistsError):
        create_bot_project(CreateBotProjectOptions(target_dir=target_dir))


def test__create_bot_project__rejects_invalid_package_name(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="should not start with a digit"):
        create_bot_project(
            CreateBotProjectOptions(
                target_dir=tmp_path / "bot",
                package_name="123bot",
            ),
        )


def test__cli_main__creates_project_in_current_directory_by_default(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = main(["create", "bot"])

    assert exit_code == 0
    assert (tmp_path / "pyproject.toml").is_file()
    assert (tmp_path / "README.md").is_file()
    generated_packages = [path for path in (tmp_path / "src").iterdir() if path.is_dir()]
    assert len(generated_packages) == 1

    stdout = capsys.readouterr().out
    assert "Created pybotx bot project" in stdout


def test__cli_main__creates_command_in_generated_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    exit_code = main(
        [
            "create",
            "command",
            "ping-users",
            "--project-dir",
            str(target_dir),
        ],
    )

    assert exit_code == 0
    assert (
        target_dir / "src" / "my_bot" / "presentation" / "commands" / "ping_users.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created command /ping-users" in stdout


def test__cli_main__creates_port_in_generated_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    exit_code = main(
        [
            "create",
            "port",
            "billing-gateway",
            "--project-dir",
            str(target_dir),
        ],
    )

    assert exit_code == 0
    assert (
        target_dir / "src" / "my_bot" / "domain" / "ports" / "billing_gateway.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created port billing_gateway" in stdout


def test__cli_main__creates_repository_in_generated_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    exit_code = main(
        [
            "create",
            "repository",
            "user-profile",
            "--project-dir",
            str(target_dir),
        ],
    )

    assert exit_code == 0
    assert (
        target_dir / "src" / "my_bot" / "domain" / "ports" / "user_profile_repository.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created repository user_profile_repository bound to port user_profile_repository" in stdout


def test__cli_main__creates_repository_bound_to_existing_port(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))
    create_port_in_project(
        CreatePortOptions(
            port_name="billing-gateway",
            project_dir=target_dir,
        ),
    )

    exit_code = main(
        [
            "create",
            "repository",
            "stripe-billing-gateway",
            "--port",
            "billing-gateway",
            "--project-dir",
            str(target_dir),
        ],
    )

    assert exit_code == 0
    assert (
        target_dir
        / "src"
        / "my_bot"
        / "infrastructure"
        / "repositories"
        / "stub_stripe_billing_gateway_repository.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert (
        "Created repository stripe_billing_gateway_repository bound to port billing_gateway"
        in stdout
    )


def test__cli_main__creates_service_in_generated_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    exit_code = main(
        [
            "create",
            "service",
            "sync-users",
            "--project-dir",
            str(target_dir),
        ],
    )

    assert exit_code == 0
    assert (
        target_dir / "src" / "my_bot" / "application" / "services" / "sync_users.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created application service sync_users" in stdout


def test__cli_main__creates_service_via_use_case_alias(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    exit_code = main(
        [
            "create",
            "use-case",
            "sync-users",
            "--project-dir",
            str(target_dir),
        ],
    )

    assert exit_code == 0
    assert (
        target_dir / "src" / "my_bot" / "application" / "services" / "sync_users.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created application service sync_users" in stdout


def test__cli_main__creates_fsm_flow_in_generated_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "fsm-bot"
    create_bot_project(
        CreateBotProjectOptions(
            target_dir=target_dir,
            template="production-fastapi-fsm",
        ),
    )

    exit_code = main(
        [
            "create",
            "fsm-flow",
            "approval",
            "--project-dir",
            str(target_dir),
        ],
    )

    assert exit_code == 0
    assert (
        target_dir / "src" / "fsm_bot" / "presentation" / "fsm" / "approval.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created FSM flow approval" in stdout


def test__cli_main__creates_widget_in_generated_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    exit_code = main(
        [
            "create",
            "widget",
            "deployment-approval",
            "--project-dir",
            str(target_dir),
            "--kind",
            "confirm",
        ],
    )

    assert exit_code == 0
    assert (
        target_dir
        / "src"
        / "my_bot"
        / "presentation"
        / "commands"
        / "deployment_approval.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created confirm widget deployment-approval" in stdout


def test__cli_main__creates_widget_flow_in_generated_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target_dir = tmp_path / "my-bot"
    create_bot_project(CreateBotProjectOptions(target_dir=target_dir))

    exit_code = main(
        [
            "create",
            "widget-flow",
            "deployment-approval",
            "--project-dir",
            str(target_dir),
            "--kind",
            "confirm",
        ],
    )

    assert exit_code == 0
    assert (
        target_dir
        / "src"
        / "my_bot"
        / "application"
        / "services"
        / "deployment_approval_result.py"
    ).is_file()
    stdout = capsys.readouterr().out
    assert "Created confirm widget flow deployment-approval" in stdout


def test__cli_main__returns_error_for_non_empty_current_directory(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "existing.txt").write_text("busy", encoding="utf-8")

    exit_code = main(["create", "bot"])

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "isn't empty" in stderr
