import warnings
from io import BytesIO

import html5lib
from defusedxml.lxml import parse
from lxml import etree

from .http import HttpService


class XpathService(HttpService):
    def build_tree(self, content):  # pylint: disable=no-self-use
        return parse(BytesIO(content))

    def get_results(self):
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
    def build_tree(self, content):
        with warnings.catch_warnings():
            # Some sites use xmlns, like "fb", in ways that lxml doesn't like
            warnings.simplefilter("ignore")
            return html5lib.parse(content, namespaceHTMLElements=False, treebuilder="lxml")
