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
