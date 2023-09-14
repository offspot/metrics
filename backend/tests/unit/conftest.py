import pathlib
from collections.abc import Callable, Generator

import pytest

from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig
from offspot_metrics_backend.constants import BackendConf


@pytest.fixture()
def reverse_proxy_config() -> (
    Generator[Callable[[str | None], ReverseProxyConfig], None, None]
):
    previous_location = BackendConf.package_conf_file_location

    def _reverse_proxy_config(location: str | None) -> ReverseProxyConfig:
        if location:
            path = (
                pathlib.Path(__file__)
                .parent.absolute()
                .joinpath("conf_files", location)
            )
            BackendConf.package_conf_file_location = str(path)
        config = ReverseProxyConfig()
        config.parse_configuration()
        return config

    yield _reverse_proxy_config

    BackendConf.package_conf_file_location = previous_location
