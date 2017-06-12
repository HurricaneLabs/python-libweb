"""DNS Services

This module implements services using DNS for communication
"""
from __future__ import absolute_import

from collections import OrderedDict

import dns.name
import dns.resolver

from . import WebService


class DnsService(WebService):
    """A simple service based on DNS requests

    Keyword arguments:
        rrname (str): The record name to lookup
        rrtype (str): The DNS record type to request
        split (str, optional): A string with which to split the result (for TXT records)
    """

    def get_resolver(self):  # pylint: disable=no-self-use
        """Returns a dns.resolver.Resolver instance"""
        resolver = dns.resolver.Resolver()
        resolver.domain = dns.name.Name("")
        return resolver

    def get_rrname(self, rrname):
        """Formats the rrname using the options passed to the service

        Args:
            rrname (str): A string template for rendering the rrname to be requested
        """
        name = rrname.format(**self.opts)
        if not name.endswith("."):
            name = "{}.".format(name)
        return name

    def make_requests(self):
        """Iterate over the requests for this service and yield the rrsets"""
        query_list = self.conf
        if not isinstance(query_list, list):
            query_list = [query_list]

        for query in query_list:
            rrname = self.get_rrname(query["rrname"])
            rrtype = query["rrtype"]
            resolver = self.get_resolver()
            try:
                rrset = resolver.query(rrname, rrtype)
            except dns.resolver.NXDOMAIN:
                raise StopIteration
            else:
                yield rrset

    def get_results(self):
        """Make the DNS requests and yield a structured response"""
        for rrset in self.make_requests():
            for rdata in rrset:
                resp = rdata.to_text()

                if rdata.rdtype == 16:
                    resp = resp.strip('"')
                    if self.conf.get("split", None):
                        resp = resp.split(self.conf.get("split"))

                if not isinstance(resp, list):
                    resp = [resp]

                for answer in resp:
                    yield OrderedDict([
                        ("name", rrset.name.to_text()),
                        ("type", rdata.__class__.__name__),
                        ("class", "IN"),
                        ("ttl", rrset.ttl),
                        ("rdata", answer),
                    ])


class DnsblService(DnsService):
    """A DNS-based service where the service options are reversed for use in a DNSBL

    Keyword arguments:
        rrname (str): The record name to lookup
        rrtype (str): The DNS record type to request
        split (str, optional): A string with which to split the result (for TXT records)
    """

    def get_rrname(self, rrname):
        """Formats the rrname using the options passed to the service. All options are
        split using "." as the separator and then the order reversed, as is required
        for DNSBL services (such as Spamhaus).

        Args:
            rrname (str): A string template for rendering the rrname to be requested
        """
        opts = dict()
        for (key, val) in self.opts.items():
            opts[key] = ".".join(reversed(val.split(".")))
        return rrname.format(**opts)
