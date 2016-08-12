try:
    import html
except ImportError:
    import HTMLParser
    html_unescape = HTMLParser.HTMLParser().unescape  # pylint: disable=invalid-name
else:
    html_unescape = html.unescape  # pylint: disable=invalid-name
import re

from .http import HttpService


class RegexService(HttpService):
    def get_html(self):
        for request in self.make_requests():
            yield html_unescape(request.text)

    @property
    def regexes(self):
        return [re.compile(regex) for regex in self.conf.get("parse", [])]

    def get_results(self):
        for body in self.get_html():
            for regex in self.regexes:
                for match in regex.finditer(body):
                    yield match.groupdict()
