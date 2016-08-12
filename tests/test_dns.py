import unittest

from libweb.dns import DnsblService, DnsService


class TestDns(unittest.TestCase):
    def setUp(self):
        self.service = DnsService()
        self.service.swallow_exceptions = False

    def tearDown(self):
        pass

    def test_single_dns_request(self):
        self.service.conf = {
            "rrname": "test.dbl.spamhaus.org",
            "rrtype": "A"
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertIn("rdata", data)
        self.assertEqual(data["rdata"], "127.0.1.2")

    def test_multiple_dns_requests(self):
        self.service.conf = [
            {"rrname": "test.dbl.spamhaus.org", "rrtype": "A"},
            {"rrname": "dbltest.com.dbl.spamhaus.org", "rrtype": "A"}
        ]

        for data in self.service:
            self.assertIn("rdata", data)
            self.assertEqual(data["rdata"], "127.0.1.2")

    def test_nxdomain_stops_iteration(self):
        self.service.conf = {
            "rrname": "example.com.dbl.spamhaus.org",
            "rrtype": "A"
        }

        self.assertEqual(len(list(self.service)), 0)

    def test_txt_strip_quotes(self):
        self.service.conf = {
            "rrname": "dbltest.com.dbl.spamhaus.org",
            "rrtype": "TXT"
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertIn("rdata", data)
        self.assertEqual(data["rdata"], "https://www.spamhaus.org/query/domain/dbltest.com")

    def test_txt_split(self):
        self.service.conf = {
            "rrname": "dbltest.com.dbl.spamhaus.org",
            "rrtype": "TXT",
            "split": "/"
        }

        rdata = list()
        for _ in self.service:
            rdata.append(_["rdata"])
        self.assertEqual(rdata, "https://www.spamhaus.org/query/domain/dbltest.com".split("/"))

    def test_dns_request_opts(self):
        self.service.conf = {
            "rrname": "{target}.dbl.spamhaus.org",
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
    def setUp(self):
        self.service = DnsblService()

    def tearDown(self):
        pass

    def test_dnsbl_request(self):
        self.service.conf = {
            "rrname": "{target}.zen.spamhaus.org",
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
