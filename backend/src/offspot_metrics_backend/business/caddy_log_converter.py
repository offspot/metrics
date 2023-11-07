import datetime
import logging

from pydantic import BaseModel, Field, ValidationError

from offspot_metrics_backend.business.input_generator import (
    EdupiInputGenerator,
    FilesInputGenerator,
    InputGenerator,
    ZimInputGenerator,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.log_data import LogData
from offspot_metrics_backend.business.reverse_proxy_config import ReverseProxyConfig

logger = logging.getLogger(__name__)


class CaddyLogRequest(BaseModel):
    """Sub-model class for parsing the request in a JSON log line of Caddy"""

    host: str
    uri: str
    method: str


class CaddyLogResponseHeaders(BaseModel):
    """Sub-model class for parsing the response headers in a JSON log line of Caddy"""

    content_type: list[str] | None = Field(alias="Content-Type", default=None)


class CaddyLog(BaseModel):
    """Base model class for parsing a JSON log line of Caddy reverse proxy"""

    level: str
    msg: str
    request: CaddyLogRequest
    status: int
    resp_headers: CaddyLogResponseHeaders
    ts: float


class CaddyLogConverter:
    """Converts logs received from Caddy reverse proxy into inputs to process"""

    def __init__(self, config: ReverseProxyConfig) -> None:
        self.generators: list[InputGenerator] = []
        for file in config.files:
            self.generators.append(
                FilesInputGenerator(host=file.host, title=file.title)
            )
        for zim in config.zims:
            self.generators.append(
                ZimInputGenerator(host=zim.host, zim_name=zim.zim_name, title=zim.title)
            )
        for app in config.apps:
            if app.ident == "edupi.offspot.kiwix.org":
                self.generators.append(EdupiInputGenerator(host=app.host))

    def process(self, line: str) -> list[Input]:
        """Transform one Caddy log line into corresponding inputs"""

        try:
            log = CaddyLog.model_validate_json(line)
        except ValidationError:
            return []

        if log.level != "info" or log.msg != "handled request":
            return []

        log_data = LogData(
            content_type=log.resp_headers.content_type[0]
            if log.resp_headers.content_type and len(log.resp_headers.content_type) > 0
            else None,
            status=log.status,
            uri=log.request.uri,
            method=log.request.method,
            ts=datetime.datetime.fromtimestamp(log.ts),
        )
        inputs: list[Input] = []
        for generator in self.generators:
            if generator.host != log.request.host:
                # ignore logs whose host are not matching the generator host
                continue
            inputs.extend(generator.process(log_data))
        return inputs
