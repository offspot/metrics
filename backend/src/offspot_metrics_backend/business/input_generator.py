import abc
import re
from http import HTTPStatus

from pydantic.dataclasses import dataclass

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
    package_title: str

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
            return [
                PackageHomeVisit(package_title=self.package_title),
                PackageRequest(ts=log.ts, package_title=self.package_title),
            ]

        if log.content_type is None:
            return [PackageRequest(ts=log.ts, package_title=self.package_title)]

        if (
            "html" in log.content_type
            or "epub" in log.content_type
            or "pdf" in log.content_type
        ):
            return [
                PackageRequest(ts=log.ts, package_title=self.package_title),
                PackageItemVisit(package_title=self.package_title, item_path=zim_path),
            ]
        else:
            return [PackageRequest(ts=log.ts, package_title=self.package_title)]


@dataclass
class EdupiInputGenerator(InputGenerator):
    """A specific generator for edupi package"""

    package_title: str

    def process(self, log: LogData) -> list[Input]:
        """Transform one log event identified as edupi into inputs"""
        if (
            log.method == "POST"
            and log.status == HTTPStatus.CREATED
            and log.uri == "/api/documents/"
        ):
            return [
                PackageRequest(ts=log.ts, package_title=self.package_title),
                SharedFilesOperation(kind=SharedFilesOperationKind.FILE_CREATED),
            ]
        elif (
            log.method == "DELETE"
            and log.status == HTTPStatus.NO_CONTENT
            and log.uri.startswith("/api/documents/")
            and len(log.uri) > len("/api/documents/")
        ):
            return [
                PackageRequest(ts=log.ts, package_title=self.package_title),
                SharedFilesOperation(kind=SharedFilesOperationKind.FILE_DELETED),
            ]
        else:
            return [PackageRequest(ts=log.ts, package_title=self.package_title)]


@dataclass
class FilesInputGenerator(InputGenerator):
    """A generator for file packages"""

    package_title: str

    def process(self, log: LogData) -> list[Input]:
        """Process a given log line and generate corresponding inputs"""
        if log.uri == "/":
            return [
                PackageRequest(ts=log.ts, package_title=self.package_title),
                PackageHomeVisit(package_title=self.package_title),
            ]
        else:
            return [PackageRequest(ts=log.ts, package_title=self.package_title)]


@dataclass
class CommonInputGenerator(InputGenerator):
    """A generator cases not covered by other specific generators"""

    package_title: str

    def process(self, log: LogData) -> list[Input]:
        """Process a given log line and generate corresponding inputs"""
        return [PackageRequest(ts=log.ts, package_title=self.package_title)]
