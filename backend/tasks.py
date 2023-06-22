import io
import os
import pathlib
import sys
import tempfile
from typing import List

import tomllib
from invoke.context import Context
from invoke.tasks import task  # pyright: ignore[reportUnknownVariableType]

deps_options = ("runtime", "test", "qa", "dev")


@task
def install_deps(c: Context, package: str = deps_options[0], no_previous: bool = False):
    """install dependencies for runtime (default) or extra packages

    packages:
        - runtime: default, to run the backend
        - test: to run the test suite
        - qa: to check code quality
        - dev: specific packages for development machine"""
    if package not in deps_options:
        print(
            f"Invalid deps package `{package}`. Choose from: {','.join(deps_options)}"
        )
        sys.exit(1)

    packages: List[str] = []
    with open("pyproject.toml", "rb") as f:
        manifest = tomllib.load(f)
    # include deps from required package and previous ones in list
    if no_previous:
        packages = manifest["dependencies"][package]
    else:
        for option in deps_options[: deps_options.index(package) + 1]:
            packages += manifest["dependencies"][option]

    c.run(
        "pip install -r /dev/stdin",
        in_stream=io.StringIO("\n".join(packages)),
    )

    # if package == "dev":
    #     c.run("pre-commit install", pty=True)


@task
def test(c: Context, args: str = "", path: str = ""):
    """execute pytest with coverage

    args: additional pytest args to pass. ex: -x -v
    path: sub-folder or test file to test to limit scope"""
    custom_db_url = os.getenv("TEST_DATABASE_URL")
    db_path = None
    if not custom_db_url:
        db_path = pathlib.Path(
            tempfile.NamedTemporaryFile(suffix=".db", prefix="test_", delete=False).name
        )
    with c.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        if db_path:
            c.run(
                "alembic upgrade head",
                env={"DATABASE_URL": f"sqlite+pysqlite:////{db_path.resolve()}"},
            )
        try:
            c.run(
                f"{sys.executable} -m pytest --cov=backend "
                f"--cov-report term-missing --cov-report html {args} "
                f"../tests{'/' + path if path else ''}",
                pty=True,
                env={
                    "DATABASE_URL": custom_db_url
                    if not db_path
                    else f"sqlite+pysqlite:////{db_path.resolve()}"
                },
            )
        finally:
            if not custom_db_url and db_path and db_path.exists():
                db_path.unlink()
        c.run("coverage xml", pty=True)


@task
def serve(c: Context, args: str = ""):
    """run devel HTTP server locally. Use --args to specify additional uvicorn args"""
    with c.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        c.run(
            f"{sys.executable} -m uvicorn backend.entrypoint:app --reload {args}",
            pty=True,
        )


@task
def alembic(c: Context, args: str = "", test_db: bool = False):
    with c.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        c.run(
            f"{sys.executable} -m alembic {args}",
            env={
                "DATABASE_URL": os.environ["TEST_DATABASE_URL"]
                if test_db
                else os.environ["DATABASE_URL"]
            },
        )


@task
def db_upgrade(c: Context, rev: str = "head", test_db: bool = False):
    c.run(
        f'invoke alembic --args "upgrade {rev}"',
        env={
            "DATABASE_URL": os.environ["TEST_DATABASE_URL"]
            if test_db
            else os.environ["DATABASE_URL"]
        },
    )


@task
def db_downgrade(c: Context, rev: str = "-1"):
    c.run(f'invoke alembic --args "downgrade {rev}"')


@task
def db_list(c: Context):
    c.run('invoke alembic --args "history -i"')


@task
def db_gen(c: Context):
    with c.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        res = c.run("alembic-autogen-check", env={"PYTHONPATH": "."}, warn=True)
    # only generate revision if we're out of sync with models
    if res and res.exited > 0:
        c.run('invoke alembic --args "revision --autogenerate -m unnamed"')


@task
def db_init_no_migration(c: Context):
    """[dev] create database schema from models, without migration. expects empty DB"""
    with c.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        c.run(
            f"{sys.executable} -c 'import sqlalchemy\n"
            "from backend.models import BaseMeta;\n"
            "engine = sqlalchemy.create_engine(str(BaseMeta.database.url))\n"
            "BaseMeta.metadata.drop_all(engine)\n"
            "BaseMeta.metadata.create_all(engine)\n'"
        )


@task
def report_qa_tools_versions(c: Context):
    print("black:")
    black_res = c.run(f"{sys.executable} -m black --version", warn=True)
    print()
    print("flake8:")
    flake8_res = c.run(f"{sys.executable} -m flake8 --version", warn=True)
    print()
    print("isort:")
    isort_res = c.run(f"{sys.executable} -m isort --version", warn=True)
    print()
    print("pyright:")
    pyright_res = c.run(f"{sys.executable} -m pyright --version", warn=True)
    print()

    if (
        not black_res
        or black_res.exited
        or not flake8_res
        or flake8_res.exited
        or not isort_res
        or isort_res.exited
        or not pyright_res
        or pyright_res.exited
    ):
        sys.exit(1)


@task
def check_qa(c: Context):
    with c.cd("src"):  # pyright: ignore[reportUnknownMemberType]
        print("black:")
        black_res = c.run(f"{sys.executable} -m black --check backend", warn=True)
        print()
        print("flake8:")
        flake8_res = c.run(
            f"{sys.executable} -m flake8 backend --count --max-line-length=88"
            " --statistics",
            warn=True,
        )
        print()
        print("isort:")
        isort_res = c.run(
            f"{sys.executable} -m isort --profile black --check backend", warn=True
        )
        print()
        if (
            not black_res
            or black_res.exited
            or not flake8_res
            or flake8_res.exited
            or not isort_res
            or isort_res.exited
        ):
            sys.exit(1)

    print("pyright:")
    pyright_res = c.run(f"{sys.executable} -m pyright", warn=True)
    print("")  # clearing pyright's output (missing CRLF)

    if not pyright_res or pyright_res.exited:
        sys.exit(1)
