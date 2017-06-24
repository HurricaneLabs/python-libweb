libweb - A library for parsing the web |Docs| |Build Status| |codecov.io|
=========================================================================

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

::

    NOTE: This example will NOT work if you're using 8.8.8.8 or 8.8.4.4 as your resolver!

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

Version 1.0.1 (2017-06-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Code changes
    - Minor change to base WebService class to enable MRO in Python 2.7
- Test changes
    - Changed DNS tests to use non-Spamhaus domains, as Spamhaus doesn't work through Google resolvers
    - Added additional tests to force tests through Google resolvers
- Administrative (non-code) changes:
    - Added travis-ci.org
    - Added codecov.io
    - Fixed readthedocs project name

Version 1.0.0 (2017-06-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Switch to jsonpath_rw_ext
-  Minor restructuring in JsonService to allow better subclassing
-  Official first release to PyPI

Version 0.99.0 (2017-01-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Initial release

.. |Docs| image:: https://readthedocs.org/projects/libweb/badge/?version=latest
    :target: http://libweb.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. |Build Status| image:: https://travis-ci.org/HurricaneLabs/python-libweb.svg?branch=master
    :target: https://travis-ci.org/HurricaneLabs/python-libweb
.. |codecov.io| image:: https://codecov.io/gh/HurricaneLabs/python-libweb/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/HurricaneLabs/python-libweb
