import json
import logging
import os
import re
from typing import Any, Dict, List

import yaml

from backend.business.inputs.content_visit import ContentHomeVisit, ContentObjectVisit
from backend.business.inputs.input import Input

logger = logging.getLogger(__name__)

Warning = str


class IncorrectConfiguration(Exception):
    pass


class LogConverter:
    """Converts logs received from the reverse proxy into inputs to process"""

    def parse_package_configuration_from_file(self, file_location: str | None = None):
        logger.info("Parsing PACKAGE_CONF_FILE")

        if file_location is None:
            file_location = os.getenv("PACKAGE_CONF_FILE", "/conf/packages.yml")
        with open(file_location, "r") as stream:
            conf_data = yaml.safe_load(stream)
            self.parse_package_configuration(conf_data=conf_data)

        for warning in self.warnings:
            logger.warning(warning)

        for host, file in self.files.items():
            logger.info(f"Found File {file} in {host}")

        for zim, data in self.zims.items():
            logger.info(f"Found Zim {zim} with {data} in {self.zim_host}")

        logger.info("Parsing PACKAGE_CONF_FILE completed")

    def parse_package_configuration(self, conf_data: Dict[str, Any]):
        self.files: Dict[str, Any] = {}
        self.zim_host: str | None = None
        self.zims: Dict[str, Any] = {}
        self.warnings: List[Warning] = []

        if not conf_data:
            raise IncorrectConfiguration("configuration is missing or empty")

        if "packages" not in conf_data:
            raise IncorrectConfiguration("'packages' key not found in configuration")

        for package in conf_data["packages"]:
            self.parse_one_package(package=package)

    def parse_one_package(self, package: Dict[str, Any]):
        url = package.get("url")
        if not url:
            self.warnings.append("Package with missing 'url' ignored")
            return

        title = package.get("title")
        if not title:
            self.warnings.append("Package with missing 'title' ignored")
            return

        match = re.match(r"^//(.*?)/.*", url)
        if not match:
            self.warnings.append(f"Unsupported URL: {url}")
            return
        host = match.group(1)

        kind = package.get("kind")
        if kind == "files":
            self.files[host] = {"title": title}
            return
        elif kind == "zim":
            if self.zim_host is None:
                self.zim_host = host
            else:
                if self.zim_host != host:
                    self.warnings.append(
                        f"Ignoring second zim host '{self.zim_host}', only one host"
                        " supported"
                    )
                    return

            match = re.match(r"^//.*?/viewer#(.*)", url)
            if not match:
                self.warnings.append(f"Unsupported ZIM URL: {url}")
                return
            zim = match.group(1)

            self.zims[zim] = {"title": title}
            return
        elif kind is None:
            self.warnings.append("Package with missing 'kind' ignored")
            return
        else:
            self.warnings.append(f"Package with unsupported 'kind' : '{kind}' ignored")
            return

    def process(self, line: str) -> List[Input]:
        logger.info(f"Parsing {line}")
        try:
            log = json.loads(line)
        except json.JSONDecodeError:
            return []
        if "message" not in log:
            return []
        try:
            message = json.loads(log["message"])
        except json.JSONDecodeError:
            return []
        if "level" not in message or message["level"] != "info":
            return []
        if "msg" not in message or message["msg"] != "handled request":
            return []

        if "request" not in message:
            return []
        if "host" not in message["request"] or "uri" not in message["request"]:
            return []

        host: str = message["request"]["host"]
        uri: str = message["request"]["uri"]
        content_type: str | None = message.get("resp_headers", {}).get("Content-Type")

        if host == self.zim_host:
            return self.process_zim(uri=uri, content_type=content_type)
        elif host in self.files:
            return self.process_file(uri=uri, host=host)
        else:
            return []

    def process_zim(self, uri: str, content_type: str | None) -> List[Input]:
        match = re.match(r"^/content/(.+?)(/.*)?$", uri)
        if not match:
            return []

        zim = match.group(1)
        object = match.group(2)

        if zim not in self.zims:
            return []

        title = self.zims[zim]["title"]
        if object is None or object == "/":
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
                return [ContentObjectVisit(content=title, object=object)]
            else:
                return []

    def process_file(self, uri: str, host: str) -> List[Input]:
        if uri == "/":
            return [ContentHomeVisit(content=self.files[host]["title"])]
        else:
            return []
