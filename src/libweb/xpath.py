"""XPath Service

This module implements services using XML formatted HTTP responses
"""
import warnings
from io import BytesIO

import html5lib
from defusedxml.lxml import parse
from lxml import etree

from .http import HttpService


class XpathService(HttpService):
    """A simple service based on HTTP requests (using XML as the reponse body)

    Keyword arguments:
        xpath (dict): key/value matches for extracting data
    """
    def build_tree(self, content):  # pylint: disable=no-self-use
        """Uses defusedxml to parse the response into ElementTree"""
        return parse(BytesIO(content))

    def get_results(self):
        """Make the HTTP requests and yield a structured message"""
        for request in self.make_requests():
            tree = self.build_tree(request.content)
            if "xpath" in self.conf:
                for (key, xpath) in self.conf["xpath"].items():
                    if xpath.startswith("/"):
                        xpath = ".{0}".format(xpath)
                    for node in tree.xpath(xpath):
                        if getattr(node, "is_attribute", False):
                            value = str(node).strip()
                        elif getattr(node, "is_text", False):
                            value = str(node).strip()
                        elif isinstance(node, etree._Element):  # pylint: disable=protected-access
                            value = " ".join(node.itertext()).strip()

                        yield {key: value}


class HtmlXpathService(XpathService):
    """A simple service using XPATH with LXML to parse HTML.

    Keyword argumnets:
    """
    def build_tree(self, content):
        """Use the html5lib parser to parse HTML"""
        with warnings.catch_warnings():
            # Some sites use xmlns, like "fb", in ways that lxml doesn't like
            warnings.simplefilter("ignore")
            return html5lib.parse(content, namespaceHTMLElements=False, treebuilder="lxml")
