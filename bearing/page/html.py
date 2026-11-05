"""The page's HTML: a shell around the data, which sits in one JSON element."""

import json


def render(data):
    # PR text could otherwise end the script element, or open an HTML comment inside it.
    text = json.dumps(data, sort_keys=True, indent=2).replace("<", "\\u003c") + "\n"
    return (
        "<!doctype html>\n<html>\n<head>\n"
        '<meta charset="utf-8">\n<title>Bearing</title>\n'
        "</head>\n<body>\n"
        '<script id="bearing-data" type="application/json">'
        + text
        + "</script>\n</body>\n</html>\n"
    )
