import json
import logging
import re
from http import HTTPStatus

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

logger = logging.getLogger(__name__)


class CaddyLogConverter:
    """Converts logs received from Caddy reverse proxy into inputs to process"""

    def __init__(self, config: ReverseProxyConfig) -> None:
        self.config = config

    def process(self, line: str) -> list[Input]:
        """Transform one Caddy log line into corresponding inputs"""
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            return []
        if "level" not in message or message["level"] != "info":
            return []
        if "msg" not in message or message["msg"] != "handled request":
            return []

        if "request" not in message:
            return []
        if "host" not in message["request"]:
            return []
        if "uri" not in message["request"]:
            return []
        if "method" not in message["request"]:
            return []
        if "status" not in message:
            return []

        host: str = message["request"]["host"]
        uri: str = message["request"]["uri"]
        method: str = message["request"]["method"]
        status: int = int(message["status"])
        content_type: str | None = message.get("resp_headers", {}).get("Content-Type")

        if host == self.config.zim_host:
            return self._process_zim(uri=uri, content_type=content_type)
        elif host in self.config.edupi_hosts:
            return self._process_edupi(uri=uri, status=status, method=method)
        elif host in self.config.files:
            return self._process_file(uri=uri, host=host)
        else:
            return []

    def _process_zim(self, uri: str, content_type: str | None) -> list[Input]:
        """Transform one log event identified as ZIM into inputs"""
        match = re.match(r"^/content/(?P<zim>.+?)(?P<item>/.*)?$", uri)
        if not match:
            return []

        zim = match.group("zim")
        item = match.group("item")

        if zim not in self.config.zims:
            return []

        title = self.config.zims[zim]["title"]
        if item is None or item == "/":
            return [ContentHomeVisit(content=title)]
        else:
            if content_type is None:
                return []
            content_type = str(content_type)

            if (
                "html" in content_type
                or "epub" in content_type
                or "pdf" in content_type
            ):
                return [ContentItemVisit(content=title, item=item)]
            else:
                return []

    def _process_edupi(self, uri: str, status: int, method: str) -> list[Input]:
        """Transform one log event identified as edupi into inputs"""
        if (
            method == "POST"
            and status == HTTPStatus.CREATED
            and uri == "/api/documents/"
        ):
            return [SharedFilesOperation(kind=SharedFilesOperationKind.FILE_CREATED)]
        elif (
            method == "DELETE"
            and status == HTTPStatus.NO_CONTENT
            and uri.startswith("/api/documents/")
            and len(uri) > len("/api/documents/")
        ):
            return [SharedFilesOperation(kind=SharedFilesOperationKind.FILE_DELETED)]
        else:
            return []

    def _process_file(self, uri: str, host: str) -> list[Input]:
        """Transform one log event identified as static file into inputs"""
        if uri == "/":
            return [ContentHomeVisit(content=self.config.files[host]["title"])]
        else:
            return []
