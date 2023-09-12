from collections.abc import Callable

import pytest

from offspot_metrics_backend.business.reverse_proxy_config import (
    IncorrectConfigurationError,
    ReverseProxyConfig,
)


def test_parsing_missing_file_provided():
    with pytest.raises(FileNotFoundError, match="/conf/packages.yml"):
        ReverseProxyConfig()


def test_parsing_empty_conf(set_package_conf_file_location: Callable[[str], None]):
    set_package_conf_file_location("conf_empty.yaml")
    with pytest.raises(IncorrectConfigurationError):
        ReverseProxyConfig()


def test_parsing_missing_packages(
    set_package_conf_file_location: Callable[[str], None]
):
    set_package_conf_file_location("conf_missing_packages.yaml")
    with pytest.raises(IncorrectConfigurationError):
        ReverseProxyConfig()


def test_parsing_ok(set_package_conf_file_location: Callable[[str], None]):
    set_package_conf_file_location("conf_ok.yaml")
    config = ReverseProxyConfig()
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


def test_parsing_warnings(set_package_conf_file_location: Callable[[str], None]):
    set_package_conf_file_location("conf_with_warnings.yaml")
    config = ReverseProxyConfig()
    assert config.warnings == [
        "Package with missing 'url' ignored",
        "Package with missing 'title' ignored",
        "Unsupported URL: tata",
        "Package with missing 'kind' ignored",
        "Ignoring second zim host 'kiwix.renaud.test', only one host supported",
        "Unsupported ZIM URL: //kiwix.renaud.test/kkkk#toto",
        "Package with unsupported 'kind' : 'ooo' ignored",
    ]
    assert config.files == {}
    assert config.zims == {
        "wikipedia_en_all": {"title": "Wikipedia"},
    }
    assert config.zim_host == "kiwix.renaud.test"
