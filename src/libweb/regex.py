"""Regex Services

This module implements services using HTTP for communication and regular expressions
to parse the results
"""

import itertools
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
    """An HTTP-based service that is scraped using regular expressions.

    Keyword arguments:
        parse (list): Regular expressions used to parse data from the service
    """

    def get_html(self):
        """Make the HTTP request(s) and unescape the returned HTML"""
        for request in self.make_requests():
            yield html_unescape(request.text)

    @property
    def regexes(self):
        """Compile the regular expressions provided in the configuration"""
        return [re.compile(regex) for regex in self.conf.get("parse", [])]

    def get_results(self):
        """Apply the configured regular expressions to the service's response"""
        for body in self.get_html():
            iters = [regex.finditer(body) for regex in self.regexes]
            try:
                zip_longest = itertools.zip_longest
            except AttributeError:
                # Python 2.7
                zip_longest = itertools.izip_longest  # pylint: disable=no-member
            for matches in zip_longest(*iters):
                yield dict(itertools.chain.from_iterable(
                    [m.groupdict().items() for m in matches if m is not None]
                ))
