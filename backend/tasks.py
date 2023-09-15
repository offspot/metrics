# pyright: strict, reportUntypedFunctionDecorator=false, reportUnknownMemberType=false
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from invoke.context import Context
from invoke.tasks import task  # pyright: ignore [reportUnknownVariableType]

use_pty = not os.getenv("CI", "")


def setup_db_and_test(ctx: Context, cmd: str, args: str):
    """Setup the test DB and run the tests

    This function takes care of:
    - using the TEST_DATABASE_URL environment variable if present
    - creating a test DB with appropriate schema if TEST_DATABASE_URL environment
    is variable not present and deleting it afterwards
    - running the tests with the `cmd` passed, for the `path` requested and with
    additional `args` supplied
    """
    temp_db_path = None
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        temp_db_path = Path(
            NamedTemporaryFile(suffix=".db", prefix="test_", delete=False).name
        ).resolve()
        test_db_url = f"sqlite+pysqlite:////{temp_db_path}"
    try:
        ctx.run(
            f"{cmd} {args}",
            pty=use_pty,
            env={"DATABASE_URL": test_db_url},
        )
    finally:
        if temp_db_path:
            temp_db_path.unlink(missing_ok=True)


@task(optional=["args"], help={"args": "pytest additional arguments"})
def test(ctx: Context, args: str = ""):
    """run tests (without coverage)"""
    setup_db_and_test(ctx=ctx, cmd="pytest", args=args)


@task(optional=["args"], help={"args": "pytest additional arguments"})
def test_cov(ctx: Context, args: str = ""):
    """run test vith coverage"""
    setup_db_and_test(ctx=ctx, cmd="coverage run -m pytest", args=args)


def call_alembic(ctx: Context, cmd: str, *, test_db: bool = False):
    """Helper function shared by multiple tasks to call alembic"""

    # this won't be needed once https://github.com/pyinvoke/invoke/issues/170 will be
    # implemented and we will be able to call alembic task from other related tasks

    with ctx.cd("src/offspot_metrics_backend"):
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

    call_alembic(ctx=ctx, cmd=cmd, test_db=test_db)


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
    call_alembic(ctx=ctx, cmd=f"upgrade {rev}", test_db=test_db)


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
    call_alembic(ctx=ctx, cmd=f"downgrade {rev}", test_db=test_db)


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
    call_alembic(ctx=ctx, cmd="history -i", test_db=test_db)


@task(optional=["html"], help={"html": "flag to export html report"})
def report_cov(ctx: Context, *, html: bool = False):
    """report test coverage"""
    ctx.run("coverage combine", warn=True, pty=use_pty)
    ctx.run("coverage report --show-missing", pty=use_pty)
    ctx.run("coverage xml", pty=use_pty)
    if html:
        ctx.run("coverage html", pty=use_pty)


@task(
    optional=["args", "html"],
    help={
        "args": "pytest additional arguments",
        "html": "flag to export html report",
    },
)
def coverage(ctx: Context, args: str = "", *, html: bool = False):
    """run tests and report coverage"""
    test_cov(ctx, args=args)
    report_cov(ctx, html=html)


@task(optional=["args"], help={"args": "black additional arguments"})
def lint_black(ctx: Context, args: str = "."):
    args = args or "."  # needed for hatch script
    ctx.run("black --version", pty=use_pty)
    ctx.run(f"black --check --diff {args}", pty=use_pty)


@task(optional=["args"], help={"args": "ruff additional arguments"})
def lint_ruff(ctx: Context, args: str = "."):
    args = args or "."  # needed for hatch script
    ctx.run("ruff --version", pty=use_pty)
    ctx.run(f"ruff check {args}", pty=use_pty)


@task(
    optional=["args"],
    help={
        "args": "linting tools (black, ruff) additional arguments, typically a path",
    },
)
def lintall(ctx: Context, args: str = "."):
    """Check linting"""
    args = args or "."  # needed for hatch script
    lint_black(ctx, args)
    lint_ruff(ctx, args)


@task(optional=["args"], help={"args": "check tools (pyright) additional arguments"})
def check_pyright(ctx: Context, args: str = ""):
    """check static types with pyright"""
    ctx.run("pyright --version")
    ctx.run(f"pyright {args}", pty=use_pty)


@task(optional=["args"], help={"args": "check tools (pyright) additional arguments"})
def checkall(ctx: Context, args: str = ""):
    """check static types"""
    check_pyright(ctx, args)


@task(optional=["args"], help={"args": "black additional arguments"})
def fix_black(ctx: Context, args: str = "."):
    """fix black formatting"""
    args = args or "."  # needed for hatch script
    ctx.run(f"black {args}", pty=use_pty)


@task(optional=["args"], help={"args": "ruff additional arguments"})
def fix_ruff(ctx: Context, args: str = "."):
    """fix all ruff rules"""
    args = args or "."  # needed for hatch script
    ctx.run(f"ruff --fix {args}", pty=use_pty)


@task(
    optional=["args"],
    help={
        "args": "linting tools (black, ruff) additional arguments, typically a path",
    },
)
def fixall(ctx: Context, args: str = "."):
    """Fix everything automatically"""
    args = args or "."  # needed for hatch script
    fix_black(ctx, args)
    fix_ruff(ctx, args)
    lintall(ctx, args)
