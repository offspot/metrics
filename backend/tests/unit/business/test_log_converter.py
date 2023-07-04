import pathlib
from typing import List

import pytest

from backend.business.inputs.content_visit import ContentHomeVisit, ContentObjectVisit
from backend.business.inputs.input import Input
from backend.business.log_converter import IncorrectConfiguration, LogConverter


def test_parsing_empty_conf():
    path = pathlib.Path(__file__).parent.absolute().joinpath("conf_empty.yaml")
    converter = LogConverter()

    with pytest.raises(IncorrectConfiguration):
        converter.parse_package_configuration_from_file(str(path))


def test_parsing_missing_packages():
    path = (
        pathlib.Path(__file__).parent.absolute().joinpath("conf_missing_packages.yaml")
    )
    converter = LogConverter()

    with pytest.raises(IncorrectConfiguration):
        converter.parse_package_configuration_from_file(str(path))


def test_parsing_ok():
    path = pathlib.Path(__file__).parent.absolute().joinpath("conf_ok.yaml")
    converter = LogConverter()
    converter.parse_package_configuration_from_file(str(path))
    assert converter.warnings == []
    assert converter.files == {
        "nomad.renaud.test": {"title": "Nomad exercices du CP à la 3è"},
        "mathews.renaud.test": {"title": "Chasse au trésor Math Mathews"},
    }
    assert converter.zims == {
        "wikipedia_en_ray_charles": {"title": "Ray Charles"},
        "wikipedia_en_all": {"title": "Wikipedia"},
    }
    assert converter.zim_host == "kiwix.renaud.test"


def test_parsing_warnings():
    path = pathlib.Path(__file__).parent.absolute().joinpath("conf_with_warnings.yaml")
    converter = LogConverter()
    converter.parse_package_configuration_from_file(str(path))
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
                ContentObjectVisit(
                    content="Wikipedia",
                    object="/questions/149/1-5-million-lines-of-code-0-tests-where",
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
def test_process_ok(log_line: str, expected_inputs: List[Input]):
    path = pathlib.Path(__file__).parent.absolute().joinpath("conf_ok.yaml")
    converter = LogConverter()
    converter.parse_package_configuration_from_file(str(path))
    inputs = converter.process(log_line)
    assert inputs == expected_inputs


def test_process_nok():
    path = pathlib.Path(__file__).parent.absolute().joinpath("processing_conf.yaml")
    converter = LogConverter()
    converter.parse_package_configuration_from_file(str(path))
    path = pathlib.Path(__file__).parent.absolute().joinpath("processing_nok.txt")
    with open(path) as fp:
        for line in fp:
            inputs = converter.process(line)
            assert len(inputs) == 0, (
                "Problem with this message which returned an input instead of none:"
                f" {line}"
            )
