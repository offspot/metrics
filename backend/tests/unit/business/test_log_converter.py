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
from offspot_metrics_backend.business.inputs.shared_files import (
    SharedFilesOperation,
    SharedFilesOperationKind,
)
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig


@pytest.mark.parametrize(
    "log_line, expected_inputs",
    [
        (
            r"""{"level":"info","msg":"handled request","status":"200","""
            r""""request":{"host":"nomad.renaud.test","uri":"/","method":"GET"}}""",
            [ContentHomeVisit(content="Nomad exercices du CP à la 3è")],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"200","""
            r""""request":{"host":"kiwix.renaud.test","method":"GET","""
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
            r"""{"level":"info","msg":"handled request","status":"200","""
            r""""request":{"host":"kiwix.renaud.test","method":"GET","""
            r""""uri":"/content/wikipedia_en_all/"}}""",
            [ContentHomeVisit(content="Wikipedia")],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"edupi1.renaud.test","method":"POST","""
            r""""uri":"/api/documents/"}}""",
            [SharedFilesOperation(kind=SharedFilesOperationKind.FILE_CREATED)],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"edupi2.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/123"}}""",
            [SharedFilesOperation(kind=SharedFilesOperationKind.FILE_DELETED)],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"400","""
            r""""request":{"host":"edupi1.renaud.test","method":"POST","""
            r""""uri":"/api/documents/"}}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"400","""
            r""""request":{"host":"edupi2.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/123"}}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"edupi1.renaud.test","method":"GET","""
            r""""uri":"/api/documents/"}}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"edupi2.renaud.test","method":"GET","""
            r""""uri":"/api/documents/123"}}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"edupi1.renaud.test","method":"POST","""
            r""""uri":"/api/documents/1"}}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"edupi2.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/"}}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"imnotedupi.renaud.test","method":"POST","""
            r""""uri":"/api/documents/"}}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"imnotedupi.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/123"}}""",
            [],
        ),
    ],
)
def test_process_ok(
    log_line: str,
    expected_inputs: list[Input],
    reverse_proxy_config: Callable[[str], ReverseProxyConfig],
):
    converter = CaddyLogConverter(reverse_proxy_config("conf_ok.yaml"))
    inputs = converter.process(log_line)
    assert inputs == expected_inputs


def test_process_nok(reverse_proxy_config: Callable[[str], ReverseProxyConfig]):
    converter = CaddyLogConverter(reverse_proxy_config("processing_conf.yaml"))
    path = pathlib.Path(__file__).parent.absolute().joinpath("processing_nok.txt")
    with open(path) as fp:
        for line in fp:
            inputs = converter.process(line)
            assert len(inputs) == 0, (
                "Problem with this message which returned an input instead of none:"
                f" {line}"
            )
