import re
from typing import Any

import yaml
from pydantic.dataclasses import dataclass

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    # we don't NEED cython ext but it's faster so use it if avail.
    from yaml import SafeLoader

from offspot_metrics_backend.constants import BackendConf, logger


class IncorrectConfigurationError(Exception):
    """Exception raised when configuration in packages.yaml is incorrect"""

    pass


@dataclass(eq=True, frozen=True)
class Config:
    title: str
    host: str


@dataclass(eq=True, frozen=True)
class ZimConfig(Config):
    zim_name: str


@dataclass(eq=True, frozen=True)
class AppConfig(Config):
    ident: str


@dataclass(eq=True, frozen=True)
class FileConfig(Config):
    pass


class ReverseProxyConfig:
    """Holds the reverse proxy config, extracted from PACKAGE_CONF_FILE"""

    host_re = re.compile(r"^//(?P<host>.*?)/.*")
    viewer_re = re.compile(r"^//.*?/viewer#(?P<zim_name>.*)$")
    content_re = re.compile(r"^//.*?/content/(?P<zim_name>.+?)(?:/.*)?$")

    def __init__(self) -> None:
        self.files: list[FileConfig] = []
        self.apps: list[AppConfig] = []
        self.zims: list[ZimConfig] = []
        self.warnings: list[str] = []

    def parse_configuration(self):
        """Parse packages.yaml configuration based on provided file"""
        logger.info("Parsing PACKAGE_CONF_FILE")

        with open(BackendConf.package_conf_file_location) as fh:
            conf_data = yaml.load(fh, Loader=SafeLoader)
            self._parse_package_configuration_data(conf_data=conf_data)

        for warning in self.warnings:
            logger.warning(warning)

        for app_config in self.apps:
            logger.info(
                f"Found app package with ident {app_config.ident} and title"
                f" {app_config.title} in {app_config.host}"
            )

        for file_config in self.files:
            logger.info(
                f"Found file package with title {file_config.title} in "
                f"{file_config.host}"
            )

        for zim_config in self.zims:
            logger.info(
                f"Found zim package with name {zim_config.zim_name} and title "
                f"{zim_config.title} in {zim_config.host}"
            )

        logger.info("Parsing PACKAGE_CONF_FILE completed")

    def _parse_package_configuration_data(self, conf_data: dict[str, Any]):
        """Parse configuration based on dictionary of configuration data"""

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

        match = self.host_re.match(url)
        if not match:
            self.warnings.append(f"Unsupported URL: {url}")
            return
        host = match.group("host")

        kind = package.get("kind")

        if kind == "app":
            ident = str(package.get("ident"))
            self.apps.append(AppConfig(title=title, host=host, ident=ident))
        elif kind == "files":
            self.files.append(FileConfig(title=title, host=host))
            return
        elif kind == "zim":
            match_viewer = self.viewer_re.match(url)
            match_content = self.content_re.match(url)
            if match_viewer:
                zim_name = match_viewer.group("zim_name")
            elif match_content:
                zim_name = match_content.group("zim_name")
            else:
                self.warnings.append(f"Unsupported ZIM URL: {url}")
                return
            self.zims.append(ZimConfig(title=title, host=host, zim_name=zim_name))
            return
        elif kind is None:
            self.warnings.append("Package with missing 'kind' ignored")
            return
        else:
            self.warnings.append(f"Package with unsupported 'kind' : '{kind}' ignored")
            return
