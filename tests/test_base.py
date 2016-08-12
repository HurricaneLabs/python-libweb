import sys
try:
    from unittest import mock, TestCase
except ImportError:
    from unittest import TestCase
    from mock import mock

import fauxfactory

from libweb import WebService


class TestHttp(TestCase):
    def setUp(self):
        self.service = WebService()

    def test_get_results_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.service.get_results()

    if sys.version_info[0] == 3:
        def test_iter_swallows_exceptions(self):
            with self.assertLogs():
                [_ for _ in self.service]

        def test_swallow_exceptions_false(self):
            with self.assertLogs():
                self.service.swallow_exceptions = False

                with self.assertRaises(NotImplementedError):
                    [_ for _ in self.service]

    def test_iter_calls_get_results(self):
        with mock.patch.object(WebService, "get_results", return_value=[]) as m:
            [_ for _ in self.service]
            m.assert_called_once()

    def test_opts_property(self):
        test_key = fauxfactory.gen_alpha().lower()
        test_value = fauxfactory.gen_alpha().lower()
        self.service = WebService(opts={test_key: test_value})

        self.assertIn(test_key, self.service.opts)
        self.assertEqual(self.service.opts[test_key], test_value)
