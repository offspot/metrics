import abc
import re
from http import HTTPStatus

from pydantic.dataclasses import dataclass

from offspot_metrics_backend.business.inputs.content_visit import (
    ContentHomeVisit,
    ContentItemVisit,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.inputs.shared_files import (
    SharedFilesOperation,
    SharedFilesOperationKind,
)
from offspot_metrics_backend.business.log_data import LogData


@dataclass
class InputGenerator(abc.ABC):
    """A generic input generator interface

    An input generator is responsible to process a log line and
    generate corresponding inputs. It is associated with a hostname used
    on the Pi (i.e. if we have two hosts, we have two generators, one per host)
    """

    host: str

    @abc.abstractmethod
    def process(self, log: LogData) -> list[Input]:
        """Process a given log line and generate corresponding inputs"""
        ...  # pragma: no cover


@dataclass
class ZimInputGenerator(InputGenerator):
    """A generator for zim packages"""

    zim_name: str
    title: str

    zim_re = re.compile(r"^/content/(?P<zim_name>.+?)(?P<zim_path>/.*)?$")

    def process(self, log: LogData) -> list[Input]:
        """Process a given log line and generate corresponding inputs"""
        match = self.zim_re.match(log.uri)
        if not match:
            return []

        zim_name = match.group("zim_name")
        zim_path = match.group("zim_path")

        if zim_name != self.zim_name:
            return []

        if zim_path is None or zim_path == "/":
            return [ContentHomeVisit(content=self.title)]
        else:
            if log.content_type is None:
                return []

            if (
                "html" in log.content_type
                or "epub" in log.content_type
                or "pdf" in log.content_type
            ):
                return [ContentItemVisit(content=self.title, item=zim_path)]
            else:
                return []


@dataclass
class EdupiInputGenerator(InputGenerator):
    """A specific generator for edupi package"""

    def process(self, log: LogData) -> list[Input]:
        """Transform one log event identified as edupi into inputs"""
        if (
            log.method == "POST"
            and log.status == HTTPStatus.CREATED
            and log.uri == "/api/documents/"
        ):
            return [SharedFilesOperation(kind=SharedFilesOperationKind.FILE_CREATED)]
        elif (
            log.method == "DELETE"
            and log.status == HTTPStatus.NO_CONTENT
            and log.uri.startswith("/api/documents/")
            and len(log.uri) > len("/api/documents/")
        ):
            return [SharedFilesOperation(kind=SharedFilesOperationKind.FILE_DELETED)]
        else:
            return []


@dataclass
class FilesInputGenerator(InputGenerator):
    """A generator for file packages"""

    title: str

    def process(self, log: LogData) -> list[Input]:
        """Process a given log line and generate corresponding inputs"""
        if log.uri == "/":
            return [ContentHomeVisit(content=self.title)]
        else:
            return []
