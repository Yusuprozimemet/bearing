"""The drawing: the classes of the cycle example, and the boxes of a 41-module graph."""

import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from itertools import pairwise


def snap(modules, imports):
    return {
        "modules": [{"name": name} for name in modules],
        "imports": [list(pair) for pair in imports],
    }


class Graph(HTMLParser):
    # Every <g> in document order, and each module's <rect> keyed by its data-name.
    def __init__(self):
        super().__init__()
        self.groups = []
        self.rects = {}
        self.open = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "g":
            self.groups.append(attrs)
            self.open.append(attrs)
        elif tag == "rect" and self.open and "data-name" in self.open[-1]:
            self.rects[self.open[-1]["data-name"]] = attrs

    def handle_endtag(self, tag):
        if tag == "g":
            self.open.pop()


def parse(text):
    parser = Graph()
    parser.feed(text)
    return parser


class DrawTest(unittest.TestCase):
    def test_classes(self):
        from bearing.page.svg import draw

        old = snap(["a", "b", "gone", "keep"], [("a", "gone"), ("b", "keep")])
        new = snap(
            ["a", "b", "c", "keep"],
            [("a", "b"), ("b", "a"), ("c", "keep"), ("b", "keep")],
        )
        events = [
            "+module c",
            "-module gone",
            "+import a -> b",
            "+import b -> a",
            "+import c -> keep",
            "-import a -> gone",
            "cycle+ a > b > a",
        ]
        out = draw(old, new, events)
        parser = parse(out)
        modules = {
            g["data-name"]: g["class"]
            for g in parser.groups
            if g["class"].startswith("module")
        }
        imports = {
            (g["data-from"], g["data-to"]): g["class"]
            for g in parser.groups
            if g["class"].startswith("import")
        }
        self.assertEqual(
            modules,
            {
                "a": "module cycle",
                "b": "module cycle",
                "c": "module added",
                "gone": "module removed",
                "keep": "module",
            },
        )
        self.assertEqual(
            imports,
            {
                ("a", "b"): "import added cycle",
                ("b", "a"): "import added cycle",
                ("a", "gone"): "import removed",
                ("b", "keep"): "import",
                ("c", "keep"): "import added",
            },
        )
        last_import = max(
            i for i, g in enumerate(parser.groups) if g["class"].startswith("import")
        )
        first_module = min(
            i for i, g in enumerate(parser.groups) if g["class"].startswith("module")
        )
        self.assertLess(last_import, first_module)
        for banned in ("xmlns", "href", "src", "style="):
            self.assertNotIn(banned, out)

        out = draw(snap([], []), snap(["a&b<c"], []), [])
        self.assertIn(">a&amp;b&lt;c</text>", out)
        self.assertEqual(parse(out).groups[0]["data-name"], "a&b<c")

    def test_positions(self):
        from bearing.page.svg import draw

        names = ["top"] + [f"m{i:02d}" for i in range(40)]
        imports = [("top", name) for name in names[1:]]
        out = draw(snap([], []), snap(names, imports), [])
        parser = parse(out)
        boxes = parser.rects
        self.assertEqual(len(boxes), 41)

        top_boxes = [name for name, r in boxes.items() if r["y"] == "16"]
        self.assertEqual(top_boxes, ["top"])
        self.assertEqual(boxes["top"]["x"], "16")
        m_boxes = {name: r for name, r in boxes.items() if name != "top"}
        for r in boxes.values():
            self.assertEqual(r["height"], "32")
        for r in m_boxes.values():
            self.assertEqual(r["width"], "48")
        for r in m_boxes.values():
            self.assertGreater(int(r["y"]), 16)

        rows = Counter(int(r["y"]) for r in m_boxes.values())
        self.assertEqual(rows, Counter({96: 15, 152: 15, 208: 10}))
        for y in (96, 152, 208):
            row = sorted(
                (int(r["x"]), name) for name, r in m_boxes.items() if int(r["y"]) == y
            )
            self.assertEqual([name for _, name in row], sorted(name for _, name in row))
            xs = [x for x, _ in row]
            self.assertEqual([b - a for a, b in pairwise(xs)], [64] * (len(xs) - 1))

        rects = [
            (int(r["x"]), int(r["y"]), int(r["width"]), int(r["height"]))
            for r in boxes.values()
        ]
        for x, _, w, _ in rects:
            self.assertLessEqual(x + w, 960)
        for i, (ax, ay, aw, ah) in enumerate(rects):
            for bx, by, bw, bh in rects[i + 1 :]:
                overlap = (
                    ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah
                )
                self.assertFalse(overlap)

        svg_width = int(re.search(r'<svg [^>]*width="(\d+)"', out).group(1))
        self.assertEqual(svg_width, max(x + w for x, _, w, _ in rects) + 16)
