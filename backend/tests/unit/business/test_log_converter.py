import pathlib
from collections.abc import Callable

import pytest

from offspot_metrics_backend.business.caddy_log_converter import (
    CaddyLogConverter,
)
from offspot_metrics_backend.business.inputs.content_visit import (
    ContentHomeVisit,
    ContentItemVisit,
)
from offspot_metrics_backend.business.inputs.input import Input


@pytest.mark.parametrize(
    "log_line, expected_inputs",
    [
        (
            r"""{"level":"info","msg":"handled request","""
            r""""request":{"host":"nomad.renaud.test","uri":"/"}}""",
            [ContentHomeVisit(content="Nomad exercices du CP à la 3è")],
        ),
        (
            r"""{"level":"info","msg":"handled request","""
            r""""request":{"host":"kiwix.renaud.test","""
            r""""uri":"/content/wikipedia_en_all/questions/149/"""
            r"""1-5-million-lines-of-code-0-tests-where"},"""
            r""""resp_headers":{"Content-Type":["text/html; charset=utf"]}}""",
            [
                ContentItemVisit(
                    content="Wikipedia",
                    item="/questions/149/1-5-million-lines-of-code-0-tests-where",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","""
            r""""request":{"host":"kiwix.renaud.test","""
            r""""uri":"/content/wikipedia_en_all/"}}""",
            [ContentHomeVisit(content="Wikipedia")],
        ),
    ],
)
def test_process_ok(
    log_line: str,
    expected_inputs: list[Input],
    set_package_conf_file_location: Callable[[str], None],
):
    set_package_conf_file_location("conf_ok.yaml")
    converter = CaddyLogConverter()
    inputs = converter.process(log_line)
    assert inputs == expected_inputs


def test_process_nok(set_package_conf_file_location: Callable[[str], None]):
    set_package_conf_file_location("processing_conf.yaml")
    converter = CaddyLogConverter()
    path = pathlib.Path(__file__).parent.absolute().joinpath("processing_nok.txt")
    with open(path) as fp:
        for line in fp:
            inputs = converter.process(line)
            assert len(inputs) == 0, (
                "Problem with this message which returned an input instead of none:"
                f" {line}"
            )
