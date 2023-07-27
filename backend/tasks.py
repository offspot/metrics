# pyright: strict, reportUntypedFunctionDecorator=false
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from invoke.context import Context
from invoke.tasks import task  # pyright: ignore [reportUnknownVariableType]

use_pty = not os.getenv("CI", "")


def setup_db_and_test(ctx: Context, cmd: str, args: str, path: str):
    """Setup the test DB and run the tests

    This function takes care of:
    - using the TEST_DATABASE_URL environment variable if present
    - creating a test DB with appropriate schema if TEST_DATABASE_URL environment
    is variable not present and deleting it afterwards
    - running the tests with the `cmd` passed, for the `path` requested and with
    additional `args` supplied
    """
    environment_db_url = os.getenv("TEST_DATABASE_URL")
    one_shot_db_path = (
        Path(NamedTemporaryFile(suffix=".db", prefix="test_", delete=False).name)
        if not environment_db_url
        else None
    )
    with ctx.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        if one_shot_db_path:
            ctx.run(
                "alembic upgrade head",
                pty=use_pty,
                env={
                    "DATABASE_URL": f"sqlite+pysqlite:////{one_shot_db_path.resolve()}"
                },
            )
        try:
            ctx.run(
                f"{cmd} {args} ../tests{'/' + path if path else ''}",
                pty=use_pty,
                env={
                    "DATABASE_URL": environment_db_url
                    if not one_shot_db_path
                    else f"sqlite+pysqlite:////{one_shot_db_path.resolve()}"
                },
            )
        finally:
            if one_shot_db_path and one_shot_db_path.exists():
                one_shot_db_path.unlink()


@task(
    optional=["args", "path"],
    help={
        "args": "pytest additional arguments",
        "path": "path to test, relative to 'tests' parent folder",
    },
)
def test(ctx: Context, args: str = "", path: str = ""):
    """run tests (without coverage)"""
    setup_db_and_test(ctx=ctx, cmd="pytest", args=args, path=path)


@task(
    optional=["args", "path"],
    help={
        "args": "pytest additional arguments",
        "path": "path to test, relative to 'tests' parent folder",
    },
)
def test_cov(ctx: Context, args: str = "", path: str = ""):
    """run test vith coverage"""
    setup_db_and_test(
        ctx=ctx, cmd="pytest --cov=offspot_metrics_backend", args=args, path=path
    )


@task(
    optional=["test-db"],
    help={
        "cmd": "alembic command to run, including options if necessary",
        "test-db": "flag to run command on test database",
    },
)
def alembic(ctx: Context, cmd: str, *, test_db: bool = False):
    """Run alembic command passed with `cmd`

    Database is identified by the DATABASE_URL environement variable or
    TEST_DATABASE_URL if `--test-db` flag is set.
    """
    with ctx.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        ctx.run(
            f"alembic {cmd}",
            pty=use_pty,
            env={
                "DATABASE_URL": os.getenv("TEST_DATABASE_URL")
                if test_db
                else os.getenv("DATABASE_URL")
            },
        )


@task(
    optional=["rev", "test-db"],
    help={
        "rev": "alembic revision, default to head",
        "test-db": "process test database",
    },
)
def db_upgrade(ctx: Context, rev: str = "head", *, test_db: bool = False):
    """Upgrade database schema with alembic

    Database is identified by the DATABASE_URL environement variable or
    TEST_DATABASE_URL if `--test-db` flag is set.
    """
    ctx.run(
        f"invoke alembic --cmd 'upgrade {rev}' {'--test-db' if test_db else ''}",
        pty=use_pty,
    )


@task(
    optional=["rev", "test-db"],
    help={
        "rev": "alembic revision, default to head",
        "test-db": "process test database",
    },
)
def db_downgrade(ctx: Context, rev: str = "-1", *, test_db: bool = False):
    """Downgrade database schema with alembic

    Database is identified by the DATABASE_URL environement variable or
    TEST_DATABASE_URL if `--test-db` flag is set.
    """
    ctx.run(
        f"invoke alembic --cmd 'downgrade {rev}' {'--test-db' if test_db else ''}",
        pty=use_pty,
    )


@task(
    optional=["test-db"],
    help={
        "test-db": "process test database",
    },
)
def db_list(ctx: Context, *, test_db: bool = False):
    """List database schema migrations with alembic

    Database is identified by the DATABASE_URL environement variable or
    TEST_DATABASE_URL if `--test-db` flag is set.
    """
    ctx.run(
        f"invoke alembic --cmd 'history -i' {'--test-db' if test_db else ''}",
        pty=use_pty,
    )


@task(optional=["no-html"], help={"no-html": "flag to not export html report"})
def report_cov(ctx: Context, *, no_html: bool = False):
    """report test coverage"""
    with ctx.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        ctx.run("coverage combine", warn=True, pty=use_pty)
        ctx.run("coverage report --show-missing", pty=use_pty)
        if not no_html:
            ctx.run("coverage html", pty=use_pty)


@task(
    optional=["args", "no-html"],
    help={
        "args": "pytest additional arguments",
        "no-html": "flag to not export html report",
    },
)
def coverage(ctx: Context, args: str = "", *, no_html: bool = False):
    """run tests and report coverage"""
    test_cov(ctx, args)
    report_cov(ctx, no_html=no_html)


@task(
    optional=["args"], help={"args": "linting tools (black, ruff) additional arguments"}
)
def lint_black(ctx: Context, args: str = "."):
    ctx.run("black --version", pty=use_pty)
    ctx.run(f"black --check --diff {args}", pty=use_pty)


@task(
    optional=["args"], help={"args": "linting tools (black, ruff) additional arguments"}
)
def lint_ruff(ctx: Context, args: str = "."):
    ctx.run("ruff --version", pty=use_pty)
    ctx.run(f"ruff check {args}", pty=use_pty)


@task(
    optional=["black_args", "ruff_args"],
    help={
        "black_args": "linting (fix mode) black arguments",
        "ruff_args": "linting (fix mode) ruff arguments",
    },
)
def lintall(ctx: Context, black_args: str = ".", ruff_args: str = "."):
    """Check linting"""
    lint_black(ctx, black_args)
    lint_ruff(ctx, ruff_args)


@task(optional=["args"], help={"args": "check tools (pyright) additional arguments"})
def check_pyright(ctx: Context, args: str = ""):
    """Check static types with pyright"""
    ctx.run("pyright --version")
    ctx.run(f"pyright {args}", pty=use_pty)


@task(optional=["args"], help={"args": "check tools (pyright) additional arguments"})
def checkall(ctx: Context, args: str = ""):
    """Check static types"""
    check_pyright(ctx, args)


@task(optional=["args"], help={"args": "black arguments"})
def fix_black(ctx: Context, args: str = "."):
    """Fix black formatting"""
    ctx.run(f"black {args}", pty=use_pty)


@task(optional=["args"], help={"args": "ruff arguments"})
def fix_ruff(ctx: Context, args: str = "."):
    """Fix ruff rules"""
    ctx.run(f"ruff --fix {args}", pty=use_pty)


@task(
    optional=["black_args", "ruff_args"],
    help={
        "black_args": "linting (fix mode) black arguments",
        "ruff_args": "linting (fix mode) ruff arguments",
    },
)
def fixall(ctx: Context, black_args: str = ".", ruff_args: str = "."):
    """Fix everything automatically"""
    fix_black(ctx, black_args)
    fix_ruff(ctx, ruff_args)
    lintall(ctx, black_args=black_args, ruff_args=ruff_args)


@task(
    optional=["args"],
    help={"args": "optional uvicorn additional arguments"},
)
def serve(c: Context, args: str = ""):
    """Run development HTTP server locally with uvicorn.

    Use --args to specify additional uvicorn args"""
    with c.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        c.run(
            f"uvicorn offspot_metrics_backend.entrypoint:app --reload {args}",
            pty=True,
        )
