import logging
from unittest import TestCase

import fauxfactory
import httpbin.core
from wsgi_intercept import add_wsgi_intercept, requests_intercept

from libweb.xpath import HtmlXpathService, XpathService


class TestXpath(TestCase):
    def get_app(self):
        return httpbin.core.app

    def setUp(self):
        requests_intercept.install()
        add_wsgi_intercept("httpbin.org", 80, self.get_app)

        logging.getLogger("requests").setLevel("ERROR")
        self.fake_target = fauxfactory.gen_ipaddr()
        self.service = XpathService(self.fake_target)
        self.service.swallow_exceptions = False
        self.html_service = HtmlXpathService(self.fake_target)
        self.html_service.swallow_exceptions = False

    def tearDown(self):
        requests_intercept.uninstall()

    def do_request(self, url, **conf):
        if "method" not in conf:
            conf["method"] = "GET"

        return self.service._req(url, **conf)

    def test_parse_xml(self):
        from lxml import etree
        r = self.do_request("http://httpbin.org/xml")
        xml = self.service.build_tree(r.content)
        self.assertIsInstance(xml, etree._ElementTree)

    def test_parse_html(self):
        from lxml import etree
        r = self.do_request("http://httpbin.org/html")
        xml = self.html_service.build_tree(r.content)
        self.assertIsInstance(xml, etree._ElementTree)

    def test_parse_error(self):
        from lxml import etree
        r = self.do_request("http://httpbin.org/get")

        with self.assertRaises(etree.XMLSyntaxError):
            self.service.build_tree(r.content)

    def test_xpath_get_element(self):
        result_key = fauxfactory.gen_alpha().lower()
        self.service.conf = {
            "url": "http://httpbin.org/xml",
            "xpath": {result_key: '//slide[@type="all"][1]'}
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertIn(result_key, data)
        self.assertEqual(data[result_key], "Wake up to WonderWidgets!")

    def test_xpath_get_text(self):
        result_key = fauxfactory.gen_alpha().lower()
        self.service.conf = {
            "url": "http://httpbin.org/xml",
            "xpath": {result_key: '//slide[@type="all"][1]/title/text()'}
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertIn(result_key, data)
        self.assertEqual(data[result_key], "Wake up to WonderWidgets!")

    def test_xpath_get_attribute(self):
        result_key = fauxfactory.gen_alpha().lower()
        self.service.conf = {
            "url": "http://httpbin.org/xml",
            "xpath": {result_key: '//slide[@type="all"][1]/@type'}
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertIn(result_key, data)
        self.assertEqual(data[result_key], "all")
