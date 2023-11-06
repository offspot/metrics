from collections.abc import Callable

import pytest

from offspot_metrics_backend.business.reverse_proxy_config import (
    IncorrectConfigurationError,
    ReverseProxyConfig,
)


def test_parsing_missing_file_provided(
    reverse_proxy_config: Callable[[str | None], ReverseProxyConfig]
):
    with pytest.raises(FileNotFoundError, match="/conf/packages.yml"):
        reverse_proxy_config(None)


def test_parsing_empty_conf(
    reverse_proxy_config: Callable[[str | None], ReverseProxyConfig]
):
    with pytest.raises(IncorrectConfigurationError):
        reverse_proxy_config("conf_empty.yaml")


def test_parsing_missing_packages(
    reverse_proxy_config: Callable[[str | None], ReverseProxyConfig]
):
    with pytest.raises(IncorrectConfigurationError):
        reverse_proxy_config("conf_missing_packages.yaml")


def test_parsing_ok(reverse_proxy_config: Callable[[str | None], ReverseProxyConfig]):
    config = reverse_proxy_config("conf_ok.yaml")
    assert config.warnings == []
    assert config.files == {
        "nomad.renaud.test": {"title": "Nomad exercices du CP à la 3è"},
        "mathews.renaud.test": {"title": "Chasse au trésor Math Mathews"},
    }
    assert config.zims == {
        "super.zim_2023-05": {"title": "Super content"},
        "wikipedia_en_ray_charles": {"title": "Ray Charles"},
        "wikipedia_en_all": {"title": "Wikipedia"},
    }
    assert config.zim_host == "kiwix.renaud.test"
    assert config.edupi_hosts == ["edupi1.renaud.test", "edupi2.renaud.test"]


def test_parsing_warnings(
    reverse_proxy_config: Callable[[str | None], ReverseProxyConfig]
):
    config = reverse_proxy_config("conf_with_warnings.yaml")
    assert config.warnings == [
        "Package with missing 'url' ignored",
        "Package with missing 'title' ignored",
        "Unsupported URL: tata",
        "Package with missing 'kind' ignored",
        "Ignoring second zim host 'kaka.renaud.test', only one host supported",
        "Unsupported ZIM URL: //kiwix.renaud.test/kkkk#toto",
        "Package with unsupported 'kind' : 'ooo' ignored",
        "Ignoring unknown app ident 'wikifundi-en.offspot.kiwix.org'",
    ]
    assert config.files == {}
    assert config.zims == {
        "wikipedia_en_all": {"title": "Wikipedia"},
    }
    assert config.zim_host == "kiwix.renaud.test"
    assert config.edupi_hosts == ["edupi.renaud.test", "edupi2.renaud.test"]
