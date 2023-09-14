from dataclasses import dataclass

from offspot_metrics_backend.business.inputs.input import Input


@dataclass
class ContentItemVisit(Input):
    """Input representing a visit of one item in one content package

    This typically represent an article in Wikipedia, a guide in iFixit, a question
    in Stack Overflow, ...
    """

    # name of the content (e.g. ZIM package name)
    content: str

    # name of the item (e.g. title of Wikipedia article or URL of Stack Overflow
    # question)
    item: str


@dataclass
class ContentHomeVisit(Input):
    """Input representing a visit of the home page of a content package"""

    # name of the content (e.g. ZIM package name)
    content: str
