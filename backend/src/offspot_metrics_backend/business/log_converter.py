import json
import logging
import os
import re
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class LogConverter:
    """Converts logs received from the reverse proxy into inputs to process"""

    def __init__(self) -> None:
        logger.info("Parsing PACKAGE_CONF_FILE")

        file_location = os.getenv("PACKAGE_CONF_FILE", "/conf/packages.yml")
        with open(file_location, "r") as stream:
            conf_data = yaml.safe_load(stream)

            self.files: Dict[str, Any] = {}
            self.zim_host: str | None = None
            self.zims: Dict[str, Any] = {}

            for package in conf_data["packages"]:
                self.parse_one_package(package=package)

        logger.info("Parsing PACKAGE_CONF_FILE completed")

    def parse_one_package(self, package: Dict[str, Any]):
        url = package.get("url")
        if not url:
            logger.warn("Package with missing 'url' in PACKAGE_CONF_FILE")
            return

        title = package.get("title")
        if not title:
            logger.warn("Package with missing 'title' in PACKAGE_CONF_FILE")
            return

        match = re.match(r"^//(.*?)/.*", url)
        if not match:
            logger.warn(f"Unsupported URL: {url}")
            return
        host = match.group(1)

        kind = package.get("kind")
        if kind == "files":
            self.files[host] = {"title": title}
            logger.info(f"Found File {self.files[host]} in {host}")
        elif kind == "zim":
            if self.zim_host is None:
                self.zim_host = host
            else:
                if self.zim_host != host:
                    logger.warn(
                        f"Ignoring second zim host '{self.zim_host}', only one host"
                        " supported"
                    )
                    return

            match = re.match(r"^//.*?/viewer#(.*)", url)
            if not match:
                logger.warn(f"Unsupported ZIM URL: {url}")
                return
            zim = match.group(1)

            self.zims[zim] = {"title": title}
            logger.info(f"Found Zim {self.zims[zim]} in {self.zim_host}")
        elif kind is None:
            logger.warn("Package with missing 'kind' in PACKAGE_CONF_FILE")
            return
        else:
            logger.warn(
                f"Package with unsupported 'kind' : '{kind}' in " "PACKAGE_CONF_FILE"
            )
            return

    def process(self, line: str):
        log = json.loads(line)
        message = json.loads(log["message"])
        if message["level"] != "info":
            return
        if message["msg"] != "handled request":
            return

        host: str = message["request"]["host"]
        uri: str = message["request"]["uri"]

        if host == self.zim_host:
            match = re.match(r"^/content/(.+?)(/.*)?$", uri)
            if not match:
                return

            zim = match.group(1)
            object = match.group(2)

            if zim not in self.zims:
                return

            title = self.zims[zim]["title"]
            if object is None or object == "/":
                logger.info(f"Content home: {title}")
            else:
                content_type = LogConverter.message_content_type(message)
                if not content_type:
                    return

                if (
                    "html" in content_type
                    or "epub" in content_type
                    or "pdf" in content_type
                ):
                    logger.info(f"Content object: {object} in {title}")

        elif host in self.files:
            title = self.files[host]["title"]
            if uri == "/":
                logger.info(f"Content home: {title}")
            # else:
            #     content_type = LogConverter.message_content_type(message)
            #     if not content_type:
            #         return

            #     if (
            #         "html" in content_type
            #         or "epub" in content_type
            #         or "pdf" in content_type
            #     ):
            #         logger.info(f"Content object: {uri} in {title}")

    @classmethod
    def message_content_type(cls, message: Dict[str, Any]) -> str | None:
        return str(message.get("resp_headers", {}).get("Content-Type"))
