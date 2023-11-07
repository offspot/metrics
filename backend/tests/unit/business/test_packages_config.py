from collections.abc import Callable

import pytest

from offspot_metrics_backend.business.reverse_proxy_config import (
    AppConfig,
    FileConfig,
    IncorrectConfigurationError,
    ReverseProxyConfig,
    ZimConfig,
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
    assert set(config.files) == {
        FileConfig(
            title="Nomad exercices du CP à la 3è",
            host="nomad.renaud.test",
        ),
        FileConfig(
            title="Chasse au trésor Math Mathews",
            host="mathews.renaud.test",
        ),
    }
    assert set(config.zims) == {
        ZimConfig(
            title="Super content",
            host="kiwix.renaud.test",
            zim_name="super.zim_2023-05",
        ),
        ZimConfig(
            title="Ray Charles",
            host="kiwix.renaud.test",
            zim_name="wikipedia_en_ray_charles",
        ),
        ZimConfig(
            title="Wikipedia", host="kiwix.renaud.test", zim_name="wikipedia_en_all"
        ),
    }
    assert set(config.apps) == {
        AppConfig(
            title="Shared files 1",
            host="edupi1.renaud.test",
            ident="edupi.offspot.kiwix.org",
        ),
        AppConfig(
            title="Shared files 2",
            host="edupi2.renaud.test",
            ident="edupi.offspot.kiwix.org",
        ),
        AppConfig(
            title="Wikifundi",
            host="wikifundi.renaud.test",
            ident="wikifundi-en.offspot.kiwix.org",
        ),
    }


def test_parsing_warnings(
    reverse_proxy_config: Callable[[str | None], ReverseProxyConfig]
):
    config = reverse_proxy_config("conf_with_warnings.yaml")
    assert config.warnings == [
        "Package with missing 'url' ignored",
        "Package with missing 'title' ignored",
        "Unsupported URL: tata",
        "Package with missing 'kind' ignored",
        "Unsupported ZIM URL: //kiwix.renaud.test/kkkk#toto",
        "Package with unsupported 'kind' : 'ooo' ignored",
    ]
    assert config.files == []
    assert set(config.zims) == {
        ZimConfig(
            title="Wikipedia", host="kiwix.renaud.test", zim_name="wikipedia_en_all"
        ),
        ZimConfig(title="toto title", host="kaka.renaud.test", zim_name="toto"),
    }
    assert set(config.apps) == {
        AppConfig(
            title="Shared files",
            host="edupi.renaud.test",
            ident="edupi.offspot.kiwix.org",
        ),
        AppConfig(
            title="Shared files 2",
            host="edupi2.renaud.test",
            ident="edupi.offspot.kiwix.org",
        ),
        AppConfig(
            title="Wikifundi",
            host="wikifundi.renaud.test",
            ident="wikifundi-en.offspot.kiwix.org",
        ),
    }
