.. _quickstart:

Quickstart
==========

If you haven't done so already, please take a moment to
:ref:`install <install>` the libweb library before
continuing.


Learning by Example
-------------------

Here is a simple parser from libweb's README, showing how to get started
interacting with the web:

.. code:: python

    # spamhaus.py

    from libweb.dns import DnsblService

    conf = {
        "rrname": "{target}.zen.spamhaus.org",
        "rrtype": "A",
    }

    for result in DnsblService(opts={"target": "127.0.0.2"}, **conf):
        print(result)


Then, to run the sample parser:

.. code:: bash

    $ python3 spamhaus.py
    OrderedDict([('name', '2.0.0.127.zen.spamhaus.org.'), ('type', 'A'), ('class', 'IN'), ('ttl', 60), ('rdata', '127.0.0.2')])
    OrderedDict([('name', '2.0.0.127.zen.spamhaus.org.'), ('type', 'A'), ('class', 'IN'), ('ttl', 60), ('rdata', '127.0.0.10')])
    OrderedDict([('name', '2.0.0.127.zen.spamhaus.org.'), ('type', 'A'), ('class', 'IN'), ('ttl', 60), ('rdata', '127.0.0.4')])
    $

.. _quickstart-more-features:

More Features
-------------

Here is a more involved example demonstrating the features available in all of
the HTTP-based parsers:

.. code:: python

    # virustotal.py

    import sys

    from libweb.json import JsonService


    conf = {
        "url": "https://www.virustotal.com/vtapi/v2/ip-address/report",
        "params": {
            "ip": "{target}"
        },
        "auth": {
            "name": "virustotal",
            "params": ["apikey"]
        },
        "jsonpath": {
            "url": "$.detected_urls[*].url",
            "pdns": "$.resolutions[*]",
            "asn": "$.asn",
            "country": "$.country",
            "as_owner": "$.as_owner",
        }
    }

    creds = {
        "virustotal": [sys.argv[1]],
    }

    opts = {
        "target": sys.argv[2]
    }

    for result in JsonService(opts=opts, creds=creds, **conf):
        print(result)


You will need a VirusTotal API key to run this sample. Feel free to borrow the
key from our sister project, `Machinae`_. You can run the sample like so:

.. code:: bash

    $ python virustotal.py <apikey> 209.95.50.13
    OrderedDict([('asn', '29854'), ('country', 'US'), ('as_owner', 'WestHost, Inc.'), ('pdns', {'hostname': 'us-newyorkcity.privateinternetaccess.com', 'last_resolved': '2016-03-13 00:00:00'})])
    $

.. _`Machinae`: https://github.com/hurricanelabs/machinae
