import logging
import re
from http import HTTPStatus

from pydantic import BaseModel, Field, ValidationError

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


class CaddyLogRequest(BaseModel):
    host: str
    uri: str
    method: str


class CaddyLogResponseHeaders(BaseModel):
    content_type: list[str] | None = Field(alias="Content-Type", default=None)


class CaddyLog(BaseModel):
    level: str
    msg: str
    request: CaddyLogRequest
    status: int
    resp_headers: CaddyLogResponseHeaders


class CaddyLogConverter:
    """Converts logs received from Caddy reverse proxy into inputs to process"""

    def __init__(self, config: ReverseProxyConfig) -> None:
        self.config = config

    def process(self, line: str) -> list[Input]:
        """Transform one Caddy log line into corresponding inputs"""

        try:
            log = CaddyLog.model_validate_json(line)
        except ValidationError:
            return []

        if log.level != "info" or log.msg != "handled request":
            return []

        content_type = (
            log.resp_headers.content_type[0]
            if log.resp_headers.content_type and len(log.resp_headers.content_type) > 0
            else None
        )

        if log.request.host == self.config.zim_host:
            return self._process_zim(uri=log.request.uri, content_type=content_type)
        elif log.request.host in self.config.edupi_hosts:
            return self._process_edupi(
                uri=log.request.uri, status=log.status, method=log.request.method
            )
        elif log.request.host in self.config.files:
            return self._process_file(uri=log.request.uri, host=log.request.host)
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
