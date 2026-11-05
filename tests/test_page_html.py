"""The page's HTML: PR text cannot end the data element or open a comment in it."""

import json
import re
import unittest

from bearing.page.html import render

OPEN = '<script id="bearing-data" type="application/json">'


class RenderTest(unittest.TestCase):
    def test_script_end_is_escaped(self):
        title = "</script><script>alert(1)</script>"
        paragraph = "a\n<!-- PROJECT: x -->\nb"
        data = {
            "version": "page-v1",
            "steps": [
                {
                    "sha": "0" * 40,
                    "date": "2026-01-01",
                    "number": 1,
                    "title": title,
                    "paragraph": paragraph,
                    "events": [],
                    "flags": [],
                }
            ],
        }
        html = render(data)
        self.assertEqual(
            len(re.findall(r"</script", html, re.IGNORECASE)),
            len(re.findall(r"<script", html, re.IGNORECASE)),
        )
        text = html.split(OPEN, 1)[1].split("</script>", 1)[0]
        self.assertNotIn("<", text)
        step = json.loads(text)["steps"][0]
        self.assertEqual(step["title"], title)
        self.assertEqual(step["paragraph"], paragraph)
