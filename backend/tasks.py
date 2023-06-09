import io
import os
import pathlib
import sys
import tempfile

import tomllib
from invoke import task

deps_options = ("runtime", "test", "qa", "dev")


@task
def install_deps(c, package=deps_options[0], no_previous=False):
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

    packages = []
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
def test(c, args="", path=""):
    """execute pytest with coverage

    args: additional pytest args to pass. ex: -x -v
    path: sub-folder or test file to test to limit scope"""
    custom_db_url = os.getenv("TEST_DATABASE_URL")
    if not custom_db_url:
        db_path = pathlib.Path(
            tempfile.NamedTemporaryFile(suffix=".db", prefix="test_", delete=False).name
        )
    with c.cd("src"):
        if not custom_db_url:
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
                    if custom_db_url
                    else f"sqlite+pysqlite:////{db_path.resolve()}"
                },
            )
        finally:
            if not custom_db_url and db_path.exists():
                db_path.unlink()
        c.run("coverage xml", pty=True)


@task
def serve(c, args=""):
    """run devel HTTP server locally. Use --args to specify additional uvicorn args"""
    with c.cd("src"):
        c.run(
            f"{sys.executable} -m uvicorn backend.entrypoint:app --reload {args}",
            pty=True,
        )


@task
def alembic(c, args="", test_db=False):
    with c.cd("src"):
        c.run(
            f"{sys.executable} -m alembic {args}",
            env={
                "DATABASE_URL": os.environ["TEST_DATABASE_URL"]
                if test_db
                else os.environ["DATABASE_URL"]
            },
        )


@task
def db_upgrade(c, rev="head", test_db=False):
    c.run(
        f'invoke alembic --args "upgrade {rev}"',
        env={
            "DATABASE_URL": os.environ["TEST_DATABASE_URL"]
            if test_db
            else os.environ["DATABASE_URL"]
        },
    )


@task
def db_downgrade(c, rev="-1"):
    c.run(f'invoke alembic --args "downgrade {rev}"')


@task
def db_list(c):
    c.run('invoke alembic --args "history -i"')


@task
def db_gen(c):
    with c.cd("src"):
        res = c.run("alembic-autogen-check", env={"PYTHONPATH": "."}, warn=True)
    # only generate revision if we're out of sync with models
    if res.exited > 0:
        c.run('invoke alembic --args "revision --autogenerate -m unnamed"')


@task
def db_init_no_migration(c):
    """[dev] create database schema from models, without migration. expects empty DB"""
    with c.cd("src"):
        c.run(
            f"{sys.executable} -c 'import sqlalchemy\n"
            "from backend.models import BaseMeta;\n"
            "engine = sqlalchemy.create_engine(str(BaseMeta.database.url))\n"
            "BaseMeta.metadata.drop_all(engine)\n"
            "BaseMeta.metadata.create_all(engine)\n'"
        )


@task
def report_qa_tools_versions(c):
    print("black:")
    black_res = c.run(f"{sys.executable} -m black --version", warn=True)
    print()
    print("flake8:")
    flake8_res = c.run(f"{sys.executable} -m flake8 --version", warn=True)
    print()
    print("isort:")
    isort_res = c.run(f"{sys.executable} -m isort --version", warn=True)
    print()
    print("mypy:")
    mypy_res = c.run(f"{sys.executable} -m mypy --version", warn=True)
    print()

    if black_res.exited or flake8_res.exited or isort_res.exited or mypy_res.exited:
        sys.exit(1)


@task
def check_qa(c):
    with c.cd("src"):
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
        if black_res.exited or flake8_res.exited or isort_res.exited:
            sys.exit(1)

    print("mypy:")
    mypy_res = c.run(f"{sys.executable} -m mypy --strict src tests", warn=True)
    print("")  # clearing mypy's output (missing CRLF)

    if mypy_res.exited:
        sys.exit(1)
