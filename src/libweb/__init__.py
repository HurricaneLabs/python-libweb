"""
python-libweb - A library for parsing the web
=============================================

Description goes here

.. moduleauthor:: Steve McMaster <mcmaster@hurricanelabs.com>
"""


import logging
import time


__version__ = "1.0.0"


class WebService:  # pylint: disable=too-few-public-methods
    """
    Base service inherited by other services throughout libweb. Should not be
    instantiated directly.
    """
    swallow_exceptions = True
    """
    If False, exceptions raised when communicating with the service will
    propagate to the caller. Otherwise, they will result in empty iteration
    """

    def __init__(self, creds=None, opts=None, **conf):
        """
        Kwargs:
            creds (dict): A dictionary of credentials to be used by the service
            opts (dict): Options specific to the request
            conf (dict): Settings for configuring the service
        """
        if opts:
            self.opts = opts
        else:
            self.opts = {}
        self.conf = conf
        self.creds = creds
        self.logger = logging.getLogger("{0}.{1}".format(
            self.__class__.__module__,
            self.__class__.__name__
        ))

    def get_results(self):
        """Communicates with the web service and yields parsed results

        Note:
            This method must be implemented by subclasses, there is no default
            behavior.
        """
        raise NotImplementedError

    def __iter__(self):
        start = time.time()
        try:
            for result in self.get_results():
                yield result
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error(str(exc))
            if not self.swallow_exceptions:
                raise
        duration = round(time.time() - start, 2)
        self.logger.debug("Query took %s seconds", duration)
