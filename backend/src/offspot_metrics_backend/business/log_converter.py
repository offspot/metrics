import json
import logging
import os
import re
from typing import Any

import yaml

from offspot_metrics_backend.business.inputs.content_visit import (
    ContentHomeVisit,
    ContentItemVisit,
)
from offspot_metrics_backend.business.inputs.input import Input

logger = logging.getLogger(__name__)


class IncorrectConfigurationError(Exception):
    """Exception raised when configuration in packages.yaml is incorrect"""

    pass


class LogConverter:
    """Converts logs received from the reverse proxy into inputs to process"""

    def parse_package_configuration_from_file(self, file_location: str | None = None):
        """Parse packages.yml configuration based on provided file"""
        logger.info("Parsing PACKAGE_CONF_FILE")

        if file_location is None:
            file_location = os.getenv("PACKAGE_CONF_FILE", "/conf/packages.yml")
        with open(file_location) as stream:
            conf_data = yaml.safe_load(stream)
            self.parse_package_configuration(conf_data=conf_data)

        for warning in self.warnings:
            logger.warning(warning)

        for host, file in self.files.items():
            logger.info(f"Found File {file} in {host}")

        for zim, data in self.zims.items():
            logger.info(f"Found Zim {zim} with {data} in {self.zim_host}")

        logger.info("Parsing PACKAGE_CONF_FILE completed")

    def parse_package_configuration(self, conf_data: dict[str, Any]):
        """Parse configuration based on dictionary of configuration data"""
        self.files: dict[str, Any] = {}
        self.zim_host: str | None = None
        self.zims: dict[str, Any] = {}
        self.warnings: list[str] = []

        if not conf_data:
            raise IncorrectConfigurationError("configuration is missing or empty")

        if "packages" not in conf_data:
            raise IncorrectConfigurationError(
                "'packages' key not found in configuration"
            )

        for package in conf_data["packages"]:
            self.parse_one_package(package=package)

    def parse_one_package(self, package: dict[str, Any]):
        """Parse one package configuration"""
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
            elif self.zim_host != host:
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

    def process(self, line: str) -> list[Input]:
        """Transform one log line into corresponding inputs"""
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

    def process_zim(self, uri: str, content_type: str | None) -> list[Input]:
        """Transform one log event identified as ZIM into inputs"""
        match = re.match(r"^/content/(.+?)(/.*)?$", uri)
        if not match:
            return []

        zim = match.group(1)
        item = match.group(2)

        if zim not in self.zims:
            return []

        title = self.zims[zim]["title"]
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

    def process_file(self, uri: str, host: str) -> list[Input]:
        """Transform one log event identified as static file into inputs"""
        if uri == "/":
            return [ContentHomeVisit(content=self.files[host]["title"])]
        else:
            return []
