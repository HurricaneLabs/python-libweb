"""HTTP Services

This module implements services using HTTP(s) for communication
"""
# import datetime
import gzip
import io
import warnings
import zipfile
# from collections import OrderedDict

import magic
import pytz
import relatime
import requests
from tzlocal import get_localzone
try:
    from requests.packages.urllib3 import exceptions  # pylint: disable=ungrouped-imports
except ImportError:  # pragma nocover
    # Apparently, some linux distros strip the packages out of requests
    # I'm not going to tell you what I think of that, just going to deal with it
    from urllib3 import exceptions

from . import __version__, WebService


class HttpService(WebService):  # pylint: disable=abstract-method
    """A simple service based on HTTP requests. This class should not be used directly"""
    _session = None
    user_agent = "python-libweb/{0}".format(__version__)

    @property
    def session(self):
        """Return a requests Session object which sets a User-Agent header"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": self.user_agent})
            # if self.proxies:
            #     self._session.proxies = self.proxies
        return self._session

    def unzip_content(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """Automatically detect and decompress zip or gzip content

        Override this to provide support for additional compressed content types
        """
        content = request.content

        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as magick:
            mime = magick.id_buffer(content)

        if mime == "application/zip":
            self.logger.debug("Unzipping 'application/zip'")
            zip_buffer = io.BytesIO(content)
            with zipfile.ZipFile(zip_buffer) as zfo:
                fname = zfo.namelist()[0]
                with zfo.open(fname) as fobj:
                    request.orig_content = fobj.read()
        elif mime == "application/x-gzip":
            self.logger.debug("Unzipping 'application/x-gzip'")
            gz_buffer = io.BytesIO(content)
            with gzip.GzipFile(fileobj=gz_buffer) as gzo:
                request.orig_content = gzo.read()
        else:
            request.orig_content = content

        return request

    def process_params(self, orig_params):  # pylint: disable=no-self-use
        """Process parameters into usable pieces.

        Override this if you provide any config parameters that may require
        interpreation, such as the relatime parameter
        """
        params = orig_params.copy()
        for (key, value) in params.items():
            if hasattr(value, "items"):
                conf = params.pop(key)
                if "relatime" in conf:
                    local_tz = get_localzone()

                    dto = relatime.timeParser(conf["relatime"], timezone=str(local_tz))
                    target_tz = pytz.timezone(conf.get("timezone", "UTC"))
                    dto = dto.astimezone(target_tz)
                    dto = dto.replace(tzinfo=None)
                    time_format = conf.get("format", "%Y-%m-%dT%H:%M:%S.%fZ")
                    if time_format.lower() == "as_epoch":
                        try:
                            timestamp = dto.timestamp()
                        except AttributeError:
                            import calendar
                            timestamp = calendar.timegm(dto.timetuple())
                        params[key] = str(int(timestamp))
                    else:
                        params[key] = dto.strftime(time_format)
        return params

    def get_auth(self, auth):
        """Find and apply authentication

        Override this if you need to support additional styles of authentication
        """
        kwargs = dict()
        if auth and self.creds:
            if not hasattr(auth, "items"):
                creds = self.creds.get(auth)
                kwargs["auth"] = tuple(creds)
            else:
                creds = self.creds.get(auth.get("name"))
                if not isinstance(creds, list):
                    creds = [creds]
                if "headers" in auth:
                    kwargs["headers"] = kwargs.get("headers", {})
                    for (key, value) in zip(auth.get("headers"), creds):
                        kwargs["headers"][key] = value
                elif "params" in auth:
                    kwargs["params"] = kwargs.get("params", {})
                    for (key, value) in zip(auth.get("params"), creds):
                        kwargs["params"][key] = value
                elif "postdata" in auth:
                    kwargs["data"] = kwargs.get("data", {})
                    for (key, value) in zip(auth.get("postdata"), creds):
                        kwargs["data"][key] = value
        return kwargs

    def build_request(self, url, method="GET", **kwargs):  # pylint: disable=no-self-use
        """Apply request hooks to automatically transform request content

        Override this if you need to customze the Request object generated.
        """
        hooks = kwargs.pop("hooks", [])
        request = requests.Request(method, url, **kwargs)
        for (event, hook) in hooks:
            request.register_hook(event, hook)
        return request

    def prepare_request(self, request):
        """Applies session state to the request"""
        return self.session.prepare_request(request)

    def send_request(self, request, verify_ssl=True):
        """Suppress SSL if necessary and send the request"""
        with warnings.catch_warnings():
            if not verify_ssl:  # pragma nocover
                warnings.simplefilter("ignore", exceptions.InsecureRequestWarning)
            return self.session.send(request, verify=verify_ssl)

    def _req(self, url, **conf):
        """Helper function for assembling and submitting requests"""
        kwargs = {
            "headers": {},
            "data": {},
            "params": {},
            "hooks": [],
            "method": conf.get("method", "get").upper(),
        }

        for key in kwargs:
            func = getattr(self, "process_{}".format(key), None)
            kwargs[key] = conf.get(key, {})
            if callable(func):
                kwargs[key] = func(kwargs[key])  # pylint: disable=not-callable

        for (key, value) in self.get_auth(conf.get("auth", {})).items():
            if hasattr(value, "items"):
                # if key not in kwargs:
                #     kwargs[key] = dict()
                kwargs[key].update(value)
            else:
                kwargs[key] = value

        kwargs = {key: value for (key, value) in kwargs.items() if value}

        kwargs["hooks"] = list()
        if conf.get("decompress", False):
            kwargs["hooks"].append(("response", self.unzip_content))

        raw_request = self.build_request(url, **kwargs)
        request = self.prepare_request(raw_request)
        return self.send_request(request, verify_ssl=conf.get("verify_ssl", True))

    def make_requests(self):
        """Iterate over configuration for multiple requests"""
        query = self.conf

        url_list = query.pop("url")
        if not isinstance(url_list, list):
            url_list = [url_list]

        for url in url_list:
            url = url.format(**self.opts)

            for key in ("params", "data", "headers"):  # pragma nocover
                if key in query:
                    settings = query.pop(key)
                    for (setting, value) in settings.items():
                        settings.update({setting: value.format(**self.opts)})
                    query[key] = settings

            request = self._req(url, **query)
            ignored_status_codes = [int(sc) for sc in query.get("ignored_status_codes", [])]
            if request.status_code not in ignored_status_codes:
                request.raise_for_status()
            yield request
