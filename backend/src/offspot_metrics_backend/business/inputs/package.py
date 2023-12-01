from dataclasses import dataclass

from offspot_metrics_backend.business.inputs.input import Input, TimedInput


@dataclass(eq=True, frozen=True)
class PackageHomeVisit(Input):
    """Input representing a visit of the home page of a package"""

    # title of the package
    package_title: str


@dataclass(eq=True, frozen=True)
class PackageRequest(TimedInput):
    """Input representing a web request on any asset of a package"""

    # title of the package
    package_title: str
