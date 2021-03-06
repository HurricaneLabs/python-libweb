import unittest

from libweb.dns import DnsblService, DnsService


class GoogleDnsMixin(object):
    def get_resolver(self):
        resolver = super(GoogleDnsMixin, self).get_resolver()
        resolver.nameservers = ["8.8.8.8", "8.8.4.4"]
        return resolver


class GoogleDnsService(GoogleDnsMixin, DnsService):
    pass


class GoogleDnsblService(GoogleDnsMixin, DnsblService):
    pass


class GoogleResolverTestMixin(object):
    def test_spamhaus_fails(self):
        self.service.conf = {
            "rrname": "test.dbl.spamhaus.org",
            "rrtype": "A"
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertNotIn("rdata", data)


class TestDns(unittest.TestCase):
    def get_service(self):
        return DnsService()

    def setUp(self):
        self.service = self.get_service()
        self.service.swallow_exceptions = False

    def tearDown(self):
        pass

    def test_single_dns_request(self):
        self.service.conf = {
            "rrname": "test.dbl.testing.machinae-app.io",
            "rrtype": "A"
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertIn("rdata", data)
        self.assertEqual(data["rdata"], "127.0.1.2")

    def test_multiple_dns_requests(self):
        self.service.conf = [
            {"rrname": "test.dbl.testing.machinae-app.io", "rrtype": "A"},
            {"rrname": "dbltest.com.dbl.testing.machinae-app.io", "rrtype": "A"}
        ]

        for data in self.service:
            self.assertIn("rdata", data)
            self.assertEqual(data["rdata"], "127.0.1.2")

    def test_nxdomain_stops_iteration(self):
        self.service.conf = {
            "rrname": "example.com.dbl.testing.machinae-app.io",
            "rrtype": "A"
        }

        self.assertEqual(len(list(self.service)), 0)

    def test_txt_strip_quotes(self):
        self.service.conf = {
            "rrname": "dbltest.com.dbl.testing.machinae-app.io",
            "rrtype": "TXT"
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertIn("rdata", data)
        self.assertEqual(data["rdata"], "https://www.spamhaus.org/query/domain/dbltest.com")

    def test_txt_split(self):
        self.service.conf = {
            "rrname": "dbltest.com.dbl.testing.machinae-app.io",
            "rrtype": "TXT",
            "split": "/"
        }

        rdata = list()
        for _ in self.service:
            rdata.append(_["rdata"])
        self.assertEqual(rdata, "https://www.spamhaus.org/query/domain/dbltest.com".split("/"))

    def test_dns_request_opts(self):
        self.service.conf = {
            "rrname": "{target}.dbl.testing.machinae-app.io",
            "rrtype": "A"
        }
        self.service.opts = {
            "target": "dbltest.com"
        }

        rdata = list()
        for data in self.service:
            self.assertIn("rdata", data)
            rdata.append(data["rdata"])
        self.assertEqual(set(rdata), set(["127.0.1.2"]))


class TestDnsbl(unittest.TestCase):
    def get_service(self):
        return DnsblService()

    def setUp(self):
        self.service = self.get_service()
        self.service.swallow_exceptions = False

    def tearDown(self):
        pass

    def test_dnsbl_request(self):
        self.service.conf = {
            "rrname": "{target}.zen.testing.machinae-app.io",
            "rrtype": "A"
        }
        self.service.opts = {
            "target": "127.0.0.2"
        }

        rdata = list()
        for data in self.service:
            self.assertIn("rdata", data)
            rdata.append(data["rdata"])
        self.assertEqual(set(rdata), set(["127.0.0.10", "127.0.0.2", "127.0.0.4"]))


class TestDnsGoogleResolver(GoogleResolverTestMixin, TestDns):
    def get_service(self):
        return GoogleDnsService()


class TestDnsblGoogleResolver(GoogleResolverTestMixin, TestDnsbl):
    def get_service(self):
        return GoogleDnsblService()
