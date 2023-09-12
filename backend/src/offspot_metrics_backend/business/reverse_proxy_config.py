import logging
import re
from typing import Any

import yaml

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    # we don't NEED cython ext but it's faster so use it if avail.
    from yaml import SafeLoader

from offspot_metrics_backend.constants import BackendConf

logger = logging.getLogger(__name__)


class IncorrectConfigurationError(Exception):
    """Exception raised when configuration in packages.yaml is incorrect"""

    pass


class ReverseProxyConfig:
    """Holds the reverse proxy config, extracted from PACKAGE_CONF_FILE"""

    def __init__(self) -> None:
        """Parse packages.yml configuration based on provided file"""
        logger.info("Parsing PACKAGE_CONF_FILE")

        with open(BackendConf.package_conf_file_location) as fh:
            conf_data = yaml.load(fh, Loader=SafeLoader)
            self._parse_package_configuration_data(conf_data=conf_data)

        for warning in self.warnings:
            logger.warning(warning)

        for host, file in self.files.items():
            logger.info(f"Found File {file} in {host}")

        for zim, data in self.zims.items():
            logger.info(f"Found ZIM {zim} with {data} in {self.zim_host}")

        logger.info("Parsing PACKAGE_CONF_FILE completed")

    def _parse_package_configuration_data(self, conf_data: dict[str, Any]):
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
            self._parse_one_package(package=package)

    def _parse_one_package(self, package: dict[str, Any]):
        """Parse one package configuration"""
        url = package.get("url")
        if not url:
            self.warnings.append("Package with missing 'url' ignored")
            return

        title = package.get("title")
        if not title:
            self.warnings.append("Package with missing 'title' ignored")
            return

        match = re.match(r"^//(?P<host>.*?)/.*", url)
        if not match:
            self.warnings.append(f"Unsupported URL: {url}")
            return
        host = match.group("host")

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

            match_viewer = re.match(r"^//.*?/viewer#(?P<zim>.*)$", url)
            match_content = re.match(r"^//.*?/content/(?P<zim>.+?)(?:/.*)?$", url)
            if match_viewer:
                zim = match_viewer.group("zim")
            elif match_content:
                zim = match_content.group("zim")
            else:
                self.warnings.append(f"Unsupported ZIM URL: {url}")
                return

            self.zims[zim] = {"title": title}
            return
        elif kind is None:
            self.warnings.append("Package with missing 'kind' ignored")
            return
        else:
            self.warnings.append(f"Package with unsupported 'kind' : '{kind}' ignored")
            return
