"""The page's HTML: a shell around the data, which sits in one JSON element."""

import json


def render(data):
    text = json.dumps(data, sort_keys=True, indent=2) + "\n"
    return (
        "<!doctype html>\n<html>\n<head>\n"
        '<meta charset="utf-8">\n<title>Bearing</title>\n'
        "</head>\n<body>\n"
        '<script id="bearing-data" type="application/json">'
        + text
        + "</script>\n</body>\n</html>\n"
    )
