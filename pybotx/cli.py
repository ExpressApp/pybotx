from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from pybotx.scaffold import (
    CreateBotProjectOptions,
    CreateCommandOptions,
    CreateFSMFlowOptions,
    CreatePortOptions,
    CreateRepositoryOptions,
    CreateServiceOptions,
    CreateWidgetOptions,
    CreateWidgetFlowOptions,
    create_bot_project,
    create_command_in_project,
    create_fsm_flow_in_project,
    create_port_in_project,
    create_repository_in_project,
    create_service_in_project,
    create_widget_in_project,
    create_widget_flow_in_project,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pybotx",
        description="CLI utilities for pybotx projects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="Create new assets managed by pybotx.",
    )
    create_subparsers = create_parser.add_subparsers(
        dest="create_command",
        required=True,
    )

    create_bot_parser = create_subparsers.add_parser(
        "bot",
        help="Generate a production-ready pybotx bot project.",
    )
    create_bot_parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Directory to generate the bot into. Defaults to the current directory.",
    )
    create_bot_parser.add_argument(
        "--template",
        default="production-fastapi",
        choices=("production-fastapi", "production-fastapi-fsm"),
        help="Scaffold template to use.",
    )
    create_bot_parser.add_argument(
        "--project-name",
        help="Explicit project name. Defaults to the target directory name.",
    )
    create_bot_parser.add_argument(
        "--package-name",
        help="Python package name. Defaults to a normalized project name.",
    )
    create_bot_parser.add_argument(
        "--display-name",
        help="Human-readable bot name used in README and default settings.",
    )
    create_bot_parser.add_argument(
        "--description",
        help="Project description written into pyproject.toml.",
    )
    create_bot_parser.add_argument(
        "--otel-tracing",
        action="store_true",
        help="Enable OpenTelemetry tracing by default in generated settings.",
    )
    create_bot_parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Skip Dockerfile and docker-compose.yml generation.",
    )

    create_command_parser = create_subparsers.add_parser(
        "command",
        help="Generate a command module inside a pybotx scaffold project.",
    )
    create_command_parser.add_argument(
        "command_name",
        help="Command name, for example `ping-users` or `/ping-users`.",
    )
    create_command_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )
    create_command_parser.add_argument(
        "--description",
        help="Command description for Bot status menu.",
    )
    create_command_parser.add_argument(
        "--response-text",
        help="Default response text returned by the generated service.",
    )

    create_service_parser = create_subparsers.add_parser(
        "service",
        help="Generate an application service and register it in the DI container.",
    )
    create_service_parser.add_argument(
        "service_name",
        help="Service name, for example `sync-users`.",
    )
    create_service_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )
    create_service_parser.add_argument(
        "--response-text",
        help="Default response text returned by the generated service.",
    )

    create_port_parser = create_subparsers.add_parser(
        "port",
        help="Generate a domain port contract inside a pybotx scaffold project.",
    )
    create_port_parser.add_argument(
        "port_name",
        help="Port name, for example `billing-gateway`.",
    )
    create_port_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )

    create_repository_parser = create_subparsers.add_parser(
        "repository",
        help="Generate a domain port + infrastructure repository stub and register it in DI.",
    )
    create_repository_parser.add_argument(
        "repository_name",
        help="Repository name, for example `user-profile`.",
    )
    create_repository_parser.add_argument(
        "--port",
        dest="port_name",
        help="Existing domain port name to bind the generated repository to.",
    )
    create_repository_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )

    create_use_case_parser = create_subparsers.add_parser(
        "use-case",
        help="Alias of `create service` for teams that prefer use-case terminology.",
    )
    create_use_case_parser.add_argument(
        "service_name",
        help="Use-case name, for example `sync-users`.",
    )
    create_use_case_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )
    create_use_case_parser.add_argument(
        "--response-text",
        help="Default response text returned by the generated service.",
    )

    create_fsm_flow_parser = create_subparsers.add_parser(
        "fsm-flow",
        help="Generate an FSM flow module inside a pybotx FSM scaffold project.",
    )
    create_fsm_flow_parser.add_argument(
        "flow_name",
        help="FSM flow name, for example `approval` or `order-approval`.",
    )
    create_fsm_flow_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )
    create_fsm_flow_parser.add_argument(
        "--command-name",
        help="Explicit command name used to start the generated flow.",
    )
    create_fsm_flow_parser.add_argument(
        "--description",
        help="Command description for Bot status menu.",
    )
    create_fsm_flow_parser.add_argument(
        "--initial-prompt",
        help="Initial prompt sent when the generated FSM flow starts.",
    )
    create_fsm_flow_parser.add_argument(
        "--completion-text",
        help="Static message sent when the generated FSM flow completes.",
    )

    create_widget_parser = create_subparsers.add_parser(
        "widget",
        help="Generate a widget command inside a pybotx scaffold project.",
    )
    create_widget_parser.add_argument(
        "widget_name",
        help="Widget name, for example `deployment-approval`.",
    )
    create_widget_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )
    create_widget_parser.add_argument(
        "--kind",
        default="confirm",
        choices=(
            "confirm",
            "approval",
            "select",
            "search-select",
            "multi-select",
            "date-range",
        ),
        help="Generated widget kind.",
    )
    create_widget_parser.add_argument(
        "--command-name",
        help="Explicit command name used to start the generated widget.",
    )
    create_widget_parser.add_argument(
        "--description",
        help="Command description for Bot status menu.",
    )

    create_widget_flow_parser = create_subparsers.add_parser(
        "widget-flow",
        help="Generate a command + widget + follow-up service flow inside a pybotx scaffold project.",
    )
    create_widget_flow_parser.add_argument(
        "flow_name",
        help="Widget flow name, for example `deployment-approval`.",
    )
    create_widget_flow_parser.add_argument(
        "--project-dir",
        default=".",
        help="Path inside the target pybotx scaffold project.",
    )
    create_widget_flow_parser.add_argument(
        "--kind",
        default="confirm",
        choices=(
            "confirm",
            "approval",
            "select",
            "search-select",
            "multi-select",
            "date-range",
        ),
        help="Generated widget flow kind.",
    )
    create_widget_flow_parser.add_argument(
        "--command-name",
        help="Explicit command name used to start the generated widget flow.",
    )
    create_widget_flow_parser.add_argument(
        "--description",
        help="Command description for Bot status menu.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "create" and args.create_command == "bot":
        return _handle_create_bot(args)
    if args.command == "create" and args.create_command == "command":
        return _handle_create_command(args)
    if args.command == "create" and args.create_command == "port":
        return _handle_create_port(args)
    if args.command == "create" and args.create_command == "repository":
        return _handle_create_repository(args)
    if args.command == "create" and args.create_command in {"service", "use-case"}:
        return _handle_create_service(args)
    if args.command == "create" and args.create_command == "fsm-flow":
        return _handle_create_fsm_flow(args)
    if args.command == "create" and args.create_command == "widget":
        return _handle_create_widget(args)
    if args.command == "create" and args.create_command == "widget-flow":
        return _handle_create_widget_flow(args)

    parser.error("Unknown command")
    return 2


def _handle_create_bot(args: argparse.Namespace) -> int:
    try:
        result = create_bot_project(
            CreateBotProjectOptions(
                target_dir=Path(args.target_dir),
                template=args.template,
                project_name=args.project_name,
                package_name=args.package_name,
                display_name=args.display_name,
                description=args.description,
                enable_otel_tracing=args.otel_tracing,
                include_docker=not args.no_docker,
            ),
        )
    except (FileExistsError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created pybotx bot project in {result.root_dir}")
    print(f"Template: {result.template}")
    print(f"Package: {result.package_name}")
    print("Next steps:")
    print(f"  cd {result.root_dir}")
    print("  cp .env.example .env")
    print("  uv sync")
    print(f"  uv run uvicorn {result.package_name}.main:app --reload")
    return 0


def _handle_create_command(args: argparse.Namespace) -> int:
    try:
        result = create_command_in_project(
            CreateCommandOptions(
                command_name=args.command_name,
                project_dir=Path(args.project_dir),
                description=args.description,
                response_text=args.response_text,
            ),
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created command {result.command_path} in {result.project_root}")
    print("Created files:")
    for created_file in result.created_files:
        print(f"  {created_file}")
    return 0


def _handle_create_port(args: argparse.Namespace) -> int:
    try:
        result = create_port_in_project(
            CreatePortOptions(
                port_name=args.port_name,
                project_dir=Path(args.project_dir),
            ),
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created port {result.port_name} in {result.project_root}")
    print("Created files:")
    for created_file in result.created_files:
        print(f"  {created_file}")
    return 0


def _handle_create_repository(args: argparse.Namespace) -> int:
    try:
        result = create_repository_in_project(
            CreateRepositoryOptions(
                repository_name=args.repository_name,
                project_dir=Path(args.project_dir),
                port_name=args.port_name,
            ),
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Created repository {result.repository_name} bound to port "
        f"{result.port_name} in {result.project_root}",
    )
    print("Created files:")
    for created_file in result.created_files:
        print(f"  {created_file}")
    return 0


def _handle_create_service(args: argparse.Namespace) -> int:
    try:
        result = create_service_in_project(
            CreateServiceOptions(
                service_name=args.service_name,
                project_dir=Path(args.project_dir),
                response_text=args.response_text,
            ),
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created application service {result.service_name} in {result.project_root}")
    print("Created files:")
    for created_file in result.created_files:
        print(f"  {created_file}")
    return 0


def _handle_create_fsm_flow(args: argparse.Namespace) -> int:
    try:
        result = create_fsm_flow_in_project(
            CreateFSMFlowOptions(
                flow_name=args.flow_name,
                project_dir=Path(args.project_dir),
                command_name=args.command_name,
                description=args.description,
                initial_prompt=args.initial_prompt,
                completion_text=args.completion_text,
            ),
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created FSM flow {result.flow_name} in {result.project_root}")
    print(f"Start command: {result.command_path}")
    print("Created files:")
    for created_file in result.created_files:
        print(f"  {created_file}")
    return 0


def _handle_create_widget(args: argparse.Namespace) -> int:
    try:
        result = create_widget_in_project(
            CreateWidgetOptions(
                widget_name=args.widget_name,
                project_dir=Path(args.project_dir),
                kind=args.kind,
                command_name=args.command_name,
                description=args.description,
            ),
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Created {result.kind} widget {result.widget_name} in {result.project_root}",
    )
    print(f"Start command: {result.command_path}")
    print("Created files:")
    for created_file in result.created_files:
        print(f"  {created_file}")
    return 0


def _handle_create_widget_flow(args: argparse.Namespace) -> int:
    try:
        result = create_widget_flow_in_project(
            CreateWidgetFlowOptions(
                flow_name=args.flow_name,
                project_dir=Path(args.project_dir),
                kind=args.kind,
                command_name=args.command_name,
                description=args.description,
            ),
        )
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created {result.kind} widget flow {result.flow_name} in {result.project_root}")
    print(f"Start command: {result.command_path}")
    print("Created files:")
    for created_file in result.created_files:
        print(f"  {created_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
