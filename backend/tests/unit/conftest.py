import pathlib
from collections.abc import Callable, Generator

import pytest

from offspot_metrics_backend.constants import BackendConf


@pytest.fixture()
def set_package_conf_file_location() -> Generator[Callable[[str], None], None, None]:
    previous_location = BackendConf.package_conf_file_location

    def _set_package_conf_file_location(location: str):
        path = pathlib.Path(__file__).parent.absolute().joinpath("conf_files", location)
        BackendConf.package_conf_file_location = str(path)

    yield _set_package_conf_file_location

    BackendConf.package_conf_file_location = previous_location
