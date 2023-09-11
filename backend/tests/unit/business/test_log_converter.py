import pathlib

import pytest

from offspot_metrics_backend.business.caddy_log_converter import (
    CaddyLogConverter,
    IncorrectConfigurationError,
)
from offspot_metrics_backend.business.inputs.content_visit import (
    ContentHomeVisit,
    ContentItemVisit,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.constants import BackendConf


def test_parsing_missing_file_provided():
    with pytest.raises(FileNotFoundError, match="/conf/packages.yml"):
        CaddyLogConverter()


def _set_package_conf_file_location(location: str):
    path = pathlib.Path(__file__).parent.absolute().joinpath(location)
    BackendConf.package_conf_file_location = str(path)


def test_parsing_empty_conf():
    _set_package_conf_file_location("conf_empty.yaml")
    with pytest.raises(IncorrectConfigurationError):
        CaddyLogConverter()


def test_parsing_missing_packages():
    _set_package_conf_file_location("conf_missing_packages.yaml")
    with pytest.raises(IncorrectConfigurationError):
        CaddyLogConverter()


def test_parsing_ok():
    _set_package_conf_file_location("conf_ok.yaml")
    converter = CaddyLogConverter()
    assert converter.warnings == []
    assert converter.files == {
        "nomad.renaud.test": {"title": "Nomad exercices du CP à la 3è"},
        "mathews.renaud.test": {"title": "Chasse au trésor Math Mathews"},
    }
    assert converter.zims == {
        "super.zim_2023-05": {"title": "Super content"},
        "wikipedia_en_ray_charles": {"title": "Ray Charles"},
        "wikipedia_en_all": {"title": "Wikipedia"},
    }
    assert converter.zim_host == "kiwix.renaud.test"


def test_parsing_warnings():
    _set_package_conf_file_location("conf_with_warnings.yaml")
    converter = CaddyLogConverter()
    assert converter.warnings == [
        "Package with missing 'url' ignored",
        "Package with missing 'title' ignored",
        "Unsupported URL: tata",
        "Package with missing 'kind' ignored",
        "Ignoring second zim host 'kiwix.renaud.test', only one host supported",
        "Unsupported ZIM URL: //kiwix.renaud.test/kkkk#toto",
        "Package with unsupported 'kind' : 'ooo' ignored",
    ]
    assert converter.files == {}
    assert converter.zims == {
        "wikipedia_en_all": {"title": "Wikipedia"},
    }
    assert converter.zim_host == "kiwix.renaud.test"


@pytest.mark.parametrize(
    "log_line, expected_inputs",
    [
        (
            r"""{"message":"{\"level\":\"info\",\"msg\":\"handled request\","""
            r"""\"request\":{\"host\":\"nomad.renaud.test\",\"uri\":\"/\"}}"}""",
            [ContentHomeVisit(content="Nomad exercices du CP à la 3è")],
        ),
        (
            r"""{"message":"{\"level\":\"info\",\"msg\":\"handled request\","""
            r"""\"request\":{\"host\":\"kiwix.renaud.test\","""
            r"""\"uri\":\"/content/wikipedia_en_all/questions/149/"""
            r"""1-5-million-lines-of-code-0-tests-where\"},"""
            r"""\"resp_headers\":{\"Content-Type\":[\"text/html; charset=utf\"]}}"}""",
            [
                ContentItemVisit(
                    content="Wikipedia",
                    item="/questions/149/1-5-million-lines-of-code-0-tests-where",
                )
            ],
        ),
        (
            r"""{"message":"{\"level\":\"info\",\"msg\":\"handled request\","""
            r"""\"request\":{\"host\":\"kiwix.renaud.test\","""
            r"""\"uri\":\"/content/wikipedia_en_all/\"}}"}""",
            [ContentHomeVisit(content="Wikipedia")],
        ),
    ],
)
def test_process_ok(log_line: str, expected_inputs: list[Input]):
    _set_package_conf_file_location("conf_ok.yaml")
    converter = CaddyLogConverter()
    inputs = converter.process(log_line)
    assert inputs == expected_inputs


def test_process_nok():
    _set_package_conf_file_location("processing_conf.yaml")
    converter = CaddyLogConverter()
    path = pathlib.Path(__file__).parent.absolute().joinpath("processing_nok.txt")
    with open(path) as fp:
        for line in fp:
            inputs = converter.process(line)
            assert len(inputs) == 0, (
                "Problem with this message which returned an input instead of none:"
                f" {line}"
            )
