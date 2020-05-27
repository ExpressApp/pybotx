"""Run common tasks using nox."""
import pathlib

import nox
from nox.sessions import Session

_EXAMPLES = ("examples/fsm/bot",)

TARGETS = ("botx", "tests", "docs/src/", *_EXAMPLES, "noxfile.py")


def _process_add_single_comma_path(session: Session, path: pathlib.Path) -> None:
    if path.is_dir():
        for new_path in path.iterdir():
            _process_add_single_comma_path(session, new_path)

        return

    if path.suffix not in {".py", ".pyi"}:
        return

    session.run(
        "add-trailing-comma", "--py36-plus", "--exit-zero-even-if-changed", str(path),
    )


def _process_add_single_comma(session: Session, *paths: str) -> None:
    for target in paths:
        path = pathlib.Path(target)
        _process_add_single_comma_path(session, path)


@nox.session(python=False, name="format")
def run_formatters(session: Session) -> None:
    """Run all project formatters.

    Formatters to run:
    1. isort with autoflake to remove all unused imports.
    2. black for sinle style in all project.
    3. add-trailing-comma to adding or removing comma from line.
    4. isort for properly imports sorting.
    """
    # we need to run isort here, since autoflake is unable to understand unused imports
    # when they are multiline.
    # see https://github.com/myint/autoflake/issues/8
    session.run("isort", "--recursive", "--force-single-line-imports", *TARGETS)
    session.run(
        "autoflake",
        "--recursive",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--in-place",
        *TARGETS,
    )
    session.run("black", *TARGETS)
    _process_add_single_comma(session, *TARGETS)
    session.run("isort", "--recursive", *TARGETS)


@nox.session(python=False)
def lint(session: Session) -> None:
    """Run all project linters.

    Linters to run:
    1. black for code format style.
    2. mypy for type checking.
    3. flake8 for common python code style issues.
    """
    session.run("black", "--check", "--diff", *TARGETS)
    session.run("mypy", *TARGETS)
    session.run("flake8", *TARGETS)


@nox.session(python=False)
def test(session: Session) -> None:
    """Run pytest."""
    session.run("pytest", "--cov-config=setup.cfg")


@nox.session(python=False)
def publish(session: Session) -> None:
    """Publish library on PyPI."""
    session.run("poetry", "publish", "--build")


@nox.session(python=False, name="build-docs")
def build_docs(session: Session) -> None:
    """Build MkDocs pages."""
    session.run("mkdocs", "build")


@nox.session(python=False, name="serve-docs")
def serve_docs(session: Session) -> None:
    """Serve MkDocs pages."""
    session.run("mkdocs", "serve", "--dev-addr", "0.0.0.0:8008")
