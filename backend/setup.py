import pathlib
import tomllib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).resolve().parent
with open(here / "pyproject.toml", "rb") as f:
    manifest = tomllib.load(f)

metadata = dict()
with open(here / "src/backend/__init__.py", "r") as fh:
    exec(fh.read(), metadata)  # pylint: disable=W0122


with open(here / "README.md", "r") as fh:
    long_desc = fh.read()

setup(
    name=metadata["__title__"],
    version=metadata["__version__"],
    url="https://github.com/offspot/metrics",
    description=metadata["__description__"],
    author="openZIM team",
    author_email="dev@kiwix.org",
    maintainer="openZIM team",
    maintainer_email="dev@kiwix.org",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    license="GPL-3.0-or-later",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=manifest["dependencies"]["runtime"],
    tests_require=manifest["dependencies"]["test"],
    extras_require={
        "test": manifest["dependencies"]["test"],
        "dev": manifest["dependencies"]["dev"],
    },
    zip_safe=False,
)
