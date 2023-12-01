import datetime
import pathlib
from collections.abc import Callable

import pytest

from offspot_metrics_backend.business.caddy_log_converter import (
    CaddyLog,
    CaddyLogConverter,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.inputs.package import (
    PackageHomeVisit,
    PackageItemVisit,
    PackageRequest,
)
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
            r""""request":{"host":"nomad.renaud.test","uri":"/","method":"GET"},"""
            r""""resp_headers":{},"ts":1688459792.8632474}""",
            [
                PackageHomeVisit(package_title="Nomad exercices du CP à la 3è"),
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Nomad exercices du CP à la 3è",
                ),
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"200","""
            r""""request":{"host":"kiwix.renaud.test","method":"GET","""
            r""""uri":"/content/wikipedia_en_all/questions/149/"""
            r"""1-5-million-lines-of-code-0-tests-where"},"""
            r""""resp_headers":{"Content-Type":["text/html; charset=utf"]},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageItemVisit(
                    package_title="Wikipedia",
                    item_path="/questions/149/1-5-million-lines-of-code-0-tests-where",
                ),
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Wikipedia",
                ),
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"200","""
            r""""request":{"host":"kiwix.renaud.test","method":"GET","""
            r""""uri":"/content/wikipedia_en_all/"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageHomeVisit(package_title="Wikipedia"),
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Wikipedia",
                ),
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"edupi1.renaud.test","method":"POST","""
            r""""uri":"/api/documents/"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                SharedFilesOperation(kind=SharedFilesOperationKind.FILE_CREATED),
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 1",
                ),
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"edupi2.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/123"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                SharedFilesOperation(kind=SharedFilesOperationKind.FILE_DELETED),
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 2",
                ),
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"edupi2.renaud.test","method":"GET","""
            r""""uri":"/api/documents/123"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 2",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"400","""
            r""""request":{"host":"edupi1.renaud.test","method":"POST","""
            r""""uri":"/api/documents/"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 1",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"400","""
            r""""request":{"host":"edupi2.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/123"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 2",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"edupi1.renaud.test","method":"GET","""
            r""""uri":"/api/documents/"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 1",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"edupi2.renaud.test","method":"GET","""
            r""""uri":"/api/documents/123"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 2",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"edupi1.renaud.test","method":"POST","""
            r""""uri":"/api/documents/1"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 1",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"edupi2.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Shared files 2",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"201","""
            r""""request":{"host":"imnotedupi.renaud.test","method":"POST","""
            r""""uri":"/api/documents/"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","status":"204","""
            r""""request":{"host":"imnotedupi.renaud.test","method":"DELETE","""
            r""""uri":"/api/documents/123"},"resp_headers":{},"""
            r""""ts":1688459792.8632474}""",
            [],
        ),
        (
            r"""{"level":"info","msg":"handled request","request":{"host":"""
            r""""nomad.renaud.test","uri":"/page2.html","method":"GET"},"status":"""
            r"""200, "resp_headers": {},"ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Nomad exercices du CP à la 3è",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","request":{"host":"""
            r""""kiwix.renaud.test","uri":"/content/wikipedia_en_all/questions/149/"""
            r"""1-5-million-lines-of-code-0-tests-where-should-we-start","method":"""
            r""""GET"},"status":200, "resp_headers": {},"ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Wikipedia",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","request":{"host":"kiwix."""
            r"""renaud.test","uri":"/content/wikipedia_en_all/assets/image.png","""
            r""""method":"GET"},"resp_headers":{"Content-Type":["image/png"]},"""
            r""""status":200,"ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Wikipedia",
                )
            ],
        ),
        (
            r"""{"level":"info","msg":"handled request","request":{"host":"wikifundi."""
            r"""renaud.test","uri":"/something/anywhere.html","""
            r""""method":"GET"},"resp_headers":{"Content-Type":["image/png"]},"""
            r""""status":200,"ts":1688459792.8632474}""",
            [
                PackageRequest(
                    ts=datetime.datetime.fromtimestamp(1688459792.8632474),
                    package_title="Wikifundi",
                )
            ],
        ),
    ],
)
def test_process_ok(
    log_line: str,
    expected_inputs: list[Input],
    reverse_proxy_config: Callable[[str], ReverseProxyConfig],
):
    converter = CaddyLogConverter(reverse_proxy_config("conf_ok.yaml"))
    result = converter.process(log_line)
    assert result.warning is None
    assert set(result.inputs) == set(expected_inputs)  # items order is not relevant


def test_process_nok(reverse_proxy_config: Callable[[str], ReverseProxyConfig]):
    converter = CaddyLogConverter(reverse_proxy_config("processing_conf.yaml"))
    path = pathlib.Path(__file__).parent.absolute().joinpath("processing_nok.txt")
    with open(path) as fp:
        for line in fp:
            result = converter.process(line)
            assert len(result.inputs) == 0, (
                "Problem with this message which returned an input instead of none:"
                f" {line}"
            )


def test_load_log_full():
    log = CaddyLog.model_validate_json(
        '{"level":"info","ts":1688459792.8632474,"logger":"http.log.access.log0","msg"'
        ':"handled request","request":{"remote_ip":"172.18.0.1","remote_port":"40236",'
        '"proto":"HTTP/1.1","method":"GET","host":"mathews.localhost:8000","uri":"/pag'
        'e2.html","headers":{"Sec-Fetch-Site":["same-origin"],"Accept":["text/html,app'
        'lication/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"],"A'
        'ccept-Language":["en-US,en;q=0.5"],"Accept-Encoding":["gzip, deflate, br"],"C'
        'onnection":["keep-alive"],"Referer":["http://mathews.localhost:8000/"],"User-'
        'Agent":["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/201001'
        '01 Firefox/114.0"],"Upgrade-Insecure-Requests":["1"],"Sec-Fetch-Dest":["docum'
        'ent"],"Sec-Fetch-Mode":["navigate"],"Sec-Fetch-User":["?1"]}},"user_id":"","d'
        'uration":0.00134691,"size":124,"status":200,"resp_headers":{"Content-Type":["'
        'text/html; charset=utf-8"],"Last-Modified":["Thu, 29 Jun 2023 08:12:31 GMT"],'
        '"Accept-Ranges":["bytes"],"Content-Length":["124"],"Server":["Caddy"],"Etag":'
        '["\\"rx09gv3g\\""]}}'
    )
    assert log.level == "info"
    assert log.status == 200
    assert log.request.host == "mathews.localhost:8000"
    assert log.msg == "handled request"
    assert log.request.uri == "/page2.html"
    assert log.request.method == "GET"
    assert log.resp_headers
    assert log.resp_headers.content_type == ["text/html; charset=utf-8"]


def test_load_log_no_content_type():
    log = CaddyLog.model_validate_json(
        '{"level":"info","ts":1688459792.8632474,"logger":"http.log.access.log0","msg"'
        ':"handled request","request":{"remote_ip":"172.18.0.1","remote_port":"40236",'
        '"proto":"HTTP/1.1","method":"GET","host":"mathews.localhost:8000","uri":"/pag'
        'e2.html","headers":{"Sec-Fetch-Site":["same-origin"],"Accept":["text/html,app'
        'lication/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"],"A'
        'ccept-Language":["en-US,en;q=0.5"],"Accept-Encoding":["gzip, deflate, br"],"C'
        'onnection":["keep-alive"],"Referer":["http://mathews.localhost:8000/"],"User-'
        'Agent":["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/201001'
        '01 Firefox/114.0"],"Upgrade-Insecure-Requests":["1"],"Sec-Fetch-Dest":["docum'
        'ent"],"Sec-Fetch-Mode":["navigate"],"Sec-Fetch-User":["?1"]}},"user_id":"","d'
        'uration":0.00134691,"size":124,"status":200,"resp_headers":{"Last-Modified":['
        '"Thu, 29 Jun 2023 08:12:31 GMT"],"Accept-Ranges":["bytes"],"Content-Length":['
        '"124"],"Server":["Caddy"],"Etag":["\\"rx09gv3g\\""]}}'
    )
    assert log.level == "info"
    assert log.status == 200
    assert log.request.host == "mathews.localhost:8000"
    assert log.request.uri == "/page2.html"
    assert log.request.method == "GET"
    assert log.resp_headers
    assert log.resp_headers.content_type is None
