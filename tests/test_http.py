# import datetime
import logging
try:
    from unittest import mock, TestCase
except ImportError:
    from unittest import TestCase
    from mock import mock

import fauxfactory
import httpbin.core
# import pytz
from wsgi_intercept import add_wsgi_intercept, requests_intercept

from libweb.http import HttpService


class TestHttp(TestCase):
    def get_app(self):
        return httpbin.core.app

    def setUp(self):
        requests_intercept.install()
        add_wsgi_intercept("httpbin.org", 80, self.get_app)

        logging.getLogger("requests").setLevel("ERROR")
        self.fake_target = fauxfactory.gen_ipaddr()
        self.service = HttpService(self.fake_target)

    def tearDown(self):
        requests_intercept.uninstall()

    def do_request(self, url, **conf):
        if "method" not in conf:
            conf["method"] = "GET"

        return self.service._req(url, **conf)

    def test_get_request(self):
        r = self.do_request("http://httpbin.org/get")
        self.assertEqual(r.status_code, 200)

    def test_post_request(self):
        param_key = fauxfactory.gen_alpha().lower()
        param_value = fauxfactory.gen_alpha().lower()
        data = {param_key: param_value}

        r = self.do_request("http://httpbin.org/post", method="POST", data=data)
        data = r.json().get("form", {})
        self.assertEqual(data.get(param_key, None), param_value)

    def test_decompress_false_default(self):
        def mock_unzip_content(self, r, *args, **kwargs):
            r.unzip_content_called = True
            return r

        with mock.patch.object(HttpService, "unzip_content", new=mock_unzip_content):
            r = self.do_request("http://httpbin.org/gzip")
        self.assertFalse(hasattr(r, "unzip_content_called"))

    def test_unzip_plain(self):
        data = fauxfactory.gen_alpha().lower().encode()

        @property
        def mock_content(self):
            return data

        import requests
        with mock.patch.object(requests.models.Response, "content", new=mock_content):
            r = self.do_request("http://httpbin.org/get", decompress=True)
        self.assertEqual(r.orig_content, data)

    def test_unzip_gzip(self):
        data = fauxfactory.gen_alpha().lower().encode()

        @property
        def mock_content(self):
            import gzip
            try:
                return gzip.compress(data)
            except AttributeError:
                from cStringIO import StringIO
                fgz = StringIO()
                with gzip.GzipFile(mode="wb", fileobj=fgz) as gzo:
                    gzo.write(data)
                return fgz.getvalue()

        import requests
        with mock.patch.object(requests.models.Response, "content", new=mock_content):
            r = self.do_request("http://httpbin.org/get", decompress=True)
        self.assertEqual(r.orig_content, data)

    def test_unzip_zip(self):
        filename = fauxfactory.gen_alpha().lower()
        data = fauxfactory.gen_alpha().lower().encode()

        @property
        def mock_content(self):
            import io
            import zipfile

            out_file = io.BytesIO()
            with zipfile.ZipFile(out_file, mode="w") as zf:
                zf.writestr(filename, data)

            return out_file.getvalue()

        import requests
        with mock.patch.object(requests.models.Response, "content", new=mock_content):
            r = self.do_request("http://httpbin.org/get", decompress=True)
        self.assertEqual(r.orig_content, data)

    def test_http_headers(self):
        header_key = "X-{}".format(fauxfactory.gen_alpha().lower().capitalize())
        header_value = fauxfactory.gen_alpha().lower()

        r = self.do_request("http://httpbin.org/headers", headers={header_key: header_value})
        data = r.json().get("headers", {})
        self.assertEqual(data.get(header_key, None), header_value)

    def test_get_params(self):
        param_key = fauxfactory.gen_alpha().lower()
        param_value = fauxfactory.gen_alpha().lower()

        r = self.do_request("http://httpbin.org/get", params={param_key: param_value})
        data = r.json().get("args", {})
        self.assertEqual(data.get(param_key, None), param_value)

    def test_get_params_relatime(self):
        import relatime
        import pytz
        from tzlocal import get_localzone

        param_key = fauxfactory.gen_alpha().lower()
        param_value = {"relatime": "-1d@d"}
        expected = relatime.timeParser("-1d@d", timezone=str(get_localzone()))
        target_tz = pytz.timezone("UTC")
        expected = expected.astimezone(target_tz)
        expected = expected.replace(tzinfo=None)

        r = self.do_request("http://httpbin.org/get", params={param_key: param_value})
        data = r.json().get("args", {})
        self.assertEqual(data.get(param_key, None), expected.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    def test_get_params_relatime_timezone(self):
        import relatime
        import pytz
        from tzlocal import get_localzone

        param_key = fauxfactory.gen_alpha().lower()
        param_value = {"relatime": "-1d@d", "timezone": "America/New_York"}
        expected = relatime.timeParser("-1d@d", timezone=str(get_localzone()))
        target_tz = pytz.timezone("America/New_York")
        expected = expected.astimezone(target_tz)
        expected = expected.replace(tzinfo=None)

        r = self.do_request("http://httpbin.org/get", params={param_key: param_value})
        data = r.json().get("args", {})
        self.assertEqual(data.get(param_key, None), expected.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    def test_get_params_relatime_epoch(self):
        import relatime
        from tzlocal import get_localzone

        tz = get_localzone()

        param_key = fauxfactory.gen_alpha().lower()
        param_value = {"relatime": "-1d@d", "format": "as_epoch", "timezone": str(tz)}
        expected = relatime.timeParser("-1d@d", timezone=str(tz))

        r = self.do_request("http://httpbin.org/get", params={param_key: param_value})
        data = r.json().get("args", {})

        try:
            expected = expected.timestamp()
        except AttributeError:
            import calendar
            expected = calendar.timegm(expected.timetuple())
        self.assertEqual(data.get(param_key, None), str(int(expected)))

    def test_http_basic_auth(self):
        authname = fauxfactory.gen_alpha()
        username = fauxfactory.gen_alpha()
        password = fauxfactory.gen_alpha()
        self.service.creds = {
            authname: (username, password)
        }

        url = "http://httpbin.org/basic-auth/{0}/{1}".format(username, password)
        r = self.do_request(url, auth=authname)
        data = r.json()
        self.assertIn("authenticated", data)
        self.assertTrue(data["authenticated"])
        self.assertIn("user", data)
        self.assertEqual(data["user"], username)

    def test_header_auth(self):
        header_key = "X-{}".format(fauxfactory.gen_alpha().lower().capitalize())
        authname = fauxfactory.gen_alpha()
        apikey = fauxfactory.gen_alpha()
        self.service.creds = {
            authname: (apikey,)
        }
        auth = {
            "name": authname,
            "headers": [header_key]
        }

        r = self.do_request("http://httpbin.org/headers", auth=auth)
        data = r.json().get("headers", {})
        self.assertIn(header_key, data)
        self.assertEqual(data[header_key], apikey)

    def test_param_auth(self):
        param_key = fauxfactory.gen_alpha()
        authname = fauxfactory.gen_alpha()
        apikey = fauxfactory.gen_alpha()
        self.service.creds = {
            authname: (apikey,)
        }
        auth = {
            "name": authname,
            "params": [param_key]
        }

        r = self.do_request("http://httpbin.org/get", auth=auth)
        data = r.json().get("args", {})
        self.assertIn(param_key, data)
        self.assertEqual(data[param_key], apikey)

    def test_post_data_auth(self):
        param_key = fauxfactory.gen_alpha()
        authname = fauxfactory.gen_alpha()
        apikey = fauxfactory.gen_alpha()
        self.service.creds = {
            authname: (apikey,)
        }
        auth = {
            "name": authname,
            "postdata": [param_key]
        }

        r = self.do_request("http://httpbin.org/post", method="POST", auth=auth)
        data = r.json().get("form", {})
        self.assertIn(param_key, data)
        self.assertEqual(data[param_key], apikey)

    def test_error_code_raises_exception(self):
        import requests.exceptions

        with self.assertRaises(requests.exceptions.HTTPError):
            self.service.conf = {
                "url": "http://httpbin.org/status/404"
            }
            [_ for _ in self.service.make_requests()]

    def test_ignored_error_codes_ignored(self):
        status_code = 400 + fauxfactory.gen_integer(min_value=0, max_value=22)

        self.service.conf = {
            "url": "http://httpbin.org/status/{0}".format(str(status_code)),
            "ignored_status_codes": [status_code]
        }
        [self.assertEqual(status_code, _.status_code) for _ in self.service.make_requests()]
