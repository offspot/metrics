import datetime
from typing import NamedTuple

from pydantic import BaseModel, Field, ValidationError

from offspot_metrics_backend.business.input_generator import (
    CommonInputGenerator,
    EdupiInputGenerator,
    FileManagerInputGenerator,
    FilesInputGenerator,
    InputGenerator,
    ZimInputGenerator,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.log_data import LogData
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig


class CaddyLogRequest(BaseModel):
    """Sub-model class for parsing the request in a JSON log line of Caddy"""

    host: str
    uri: str
    method: str


class CaddyLogResponseHeaders(BaseModel):
    """Sub-model class for parsing the response headers in a JSON log line of Caddy"""

    content_type: list[str] | None = Field(alias="Content-Type", default=None)
    x_tfm_files_added: list[str] | None = Field(alias="X-Tfm-Files-Added", default=None)
    x_tfm_files_deleted: list[str] | None = Field(
        alias="X-Tfm-Files-Deleted", default=None
    )


class CaddyLog(BaseModel):
    """Base model class for parsing a JSON log line of Caddy reverse proxy"""

    level: str
    msg: str
    request: CaddyLogRequest
    status: int
    resp_headers: CaddyLogResponseHeaders
    ts: float


class ProcessingResult(NamedTuple):
    inputs: list[Input]
    ts: datetime.datetime | None
    warning: str | None


class CaddyLogConverter:
    """Converts logs received from Caddy reverse proxy into inputs to process"""

    def __init__(self, config: ReverseProxyConfig) -> None:
        self.generators: list[InputGenerator] = []
        for file in config.files:
            self.generators.append(
                FilesInputGenerator(host=file.host, package_title=file.title)
            )
        for zim in config.zims:
            self.generators.append(
                ZimInputGenerator(
                    host=zim.host, zim_name=zim.zim_name, package_title=zim.title
                )
            )
        for app in config.apps:
            if app.ident == "edupi.offspot.kiwix.org":
                self.generators.append(
                    EdupiInputGenerator(host=app.host, package_title=app.title),
                )
            elif app.ident == "file-manager.offspot.kiwix.org":
                self.generators.append(
                    FileManagerInputGenerator(host=app.host, package_title=app.title),
                )
            else:
                self.generators.append(
                    CommonInputGenerator(host=app.host, package_title=app.title),
                )

    def process(self, line: str) -> ProcessingResult:
        """Transform one Caddy log line into corresponding inputs"""

        try:
            log = CaddyLog.model_validate_json(line)
            del line
        except ValidationError:
            return ProcessingResult(inputs=[], ts=None, warning="JSON parsing failed")

        if log.level != "info":
            return ProcessingResult(inputs=[], ts=None, warning="Unexpected log level")

        if log.msg != "handled request":
            return ProcessingResult(inputs=[], ts=None, warning="Unexpected log msg")

        ts = datetime.datetime.fromtimestamp(log.ts)
        log_data = LogData(
            content_type=(
                log.resp_headers.content_type[0]
                if log.resp_headers.content_type
                and len(log.resp_headers.content_type) > 0
                else None
            ),
            status=log.status,
            uri=log.request.uri,
            method=log.request.method,
            ts=ts,
            x_tfm_files_added=(
                int(log.resp_headers.x_tfm_files_added[0])
                if log.resp_headers.x_tfm_files_added
                and len(log.resp_headers.x_tfm_files_added) > 0
                else None
            ),
            x_tfm_files_deleted=(
                int(log.resp_headers.x_tfm_files_deleted[0])
                if log.resp_headers.x_tfm_files_deleted
                and len(log.resp_headers.x_tfm_files_deleted) > 0
                else None
            ),
        )
        inputs: list[Input] = []
        for generator in self.generators:
            if generator.host != log.request.host:
                # ignore logs whose host are not matching the generator host
                continue
            inputs.extend(generator.process(log_data))
        return ProcessingResult(inputs=inputs, ts=ts, warning=None)
