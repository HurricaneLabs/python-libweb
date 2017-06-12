libweb - A library for parsing the web
======================================

libweb is, simply, a parsing engine for the web. The goal of the libweb project
is to provide a library capable of parsing the vast majority of consumable
content on the web. libweb strives to maintain compatibility with current
versions of Python, and specifically tests against Python 2.7 and Python 3.3+.

Installation
------------

python-libweb can be installed using pip3:

::

    pip3 install libweb

Or, if you're feeling adventurous, can be installed directly from
github:

::

    pip3 install git+https://github.com/HurricaneLabs/python-libweb.git

Usage
-----

.. code:: python

    # spamhaus.py

    from libweb.dns import DnsblService

    conf = {
        "rrname": "{target}.zen.spamhaus.org",
        "rrtype": "A",
    }

    for result in DnsblService(opts={"target": "127.0.0.2"}, **conf):
        print(result)

Known Issues
------------
-  TODO

Upcoming Features
-----------------
-  TODO

Version History
---------------

Version 1.0.0 (2017-06-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Switch to jsonpath_rw_ext
-  Minor restructuring in JsonService to allow better subclassing
-  Official first release to PyPI

Version 0.99.0 (2017-01-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Initial release
