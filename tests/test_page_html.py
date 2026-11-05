"""The page's HTML: PR text cannot end the data element or open a comment in it."""

import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from html.parser import HTMLParser
from pathlib import Path

from bearing.page.html import render

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "page-v1.json"
TOML = REPO / "tests" / "fixtures" / "bearing.toml"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
OPEN = '<script id="bearing-data" type="application/json">'
BODY = "## What I built\n\nx </script><script>alert(1)</script><!-- y\n"
NOTE = (
    "Flags are unverified: their rules have not been judged on a history they were "
    "not fitted to."
)


def run(*args, env=ENV):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=env,
    )


def bearing(*args, env=ENV):
    return run("-m", "bearing", *args, env=env)


class Page(HTMLParser):
    # Keeps the text of the elements the tests check, one capture at a time: none of them nest.
    def __init__(self):
        super().__init__()
        self.sections = []
        self.section = None
        self.lists = []
        self.buttons = {}
        self.counter = None
        self.styles = []
        self.scripts = []
        self.tag = None
        self.sink = None
        self.buf = []
        self.svgs = 0

    def capture(self, tag, sink):
        self.tag = tag
        self.buf = []
        self.sink = sink

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "svg":
            self.svgs += 1
            if self.section is not None:
                self.section["svgs"] += 1
        elif tag == "g" and self.section is not None:
            # A graph's boxes and arrows: the class starts with what the element is.
            if classes[:1] == ["module"]:
                self.section["modules"][a["data-name"]] = a["class"]
            elif classes[:1] == ["import"]:
                self.section["imports"][(a["data-from"], a["data-to"])] = a["class"]
        if tag == "section" and "step" in classes:
            self.section = {
                "sha": a["data-sha"],
                "hidden": "hidden" in a,
                "heading": None,
                "paragraphs": [],
                "events": [],
                "flags": [],
                "svgs": 0,
                "modules": {},
                "imports": {},
            }
            self.sections.append(self.section)
        elif tag == "ul":
            self.lists.append(classes)
        elif tag == "li" and self.lists and "events" in self.lists[-1]:
            self.capture(tag, self.section["events"].append)
        elif tag == "li" and self.lists and "flags" in self.lists[-1]:
            self.capture(tag, self.section["flags"].append)
        elif tag == "h2":
            self.capture(tag, lambda s, sec=self.section: sec.update(heading=s))
        elif tag == "p" and self.section is not None:
            self.capture(tag, self.section["paragraphs"].append)
        elif tag == "button":
            self.capture(tag, lambda s, k=a["id"]: self.buttons.update({k: s}))
        elif tag == "span" and a.get("id") == "counter":
            self.capture(tag, lambda s: setattr(self, "counter", s))
        elif tag == "style":
            self.capture(tag, self.styles.append)
        elif tag == "script":
            script = {"attrs": a}
            self.scripts.append(script)
            self.capture(tag, lambda s: script.update(text=s))

    def handle_endtag(self, tag):
        if tag == "ul":
            self.lists.pop()
        elif tag == "section":
            self.section = None
        if self.sink is not None and tag == self.tag:
            self.sink("".join(self.buf))
            self.sink = None

    def handle_data(self, data):
        if self.sink is not None:
            self.buf.append(data)


def parse(text):
    page = Page()
    page.feed(text)
    page.close()
    return page


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


class PageHtmlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.repo = cls.out / "repo"
        cls.built = run(BUILDER, cls.out)
        cls.data = Path(cls.tmp.name) / "data"
        cls.ingested = bearing(
            "ingest", cls.repo, "--prs", cls.out / "prs.json", "--data", cls.data
        )
        cls.golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        cls.result, cls.text = cls.page(cls.data, "page")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def page(cls, data, name):
        out = Path(cls.tmp.name) / f"{name}.html"
        result = bearing(
            "page", cls.repo, "--data", data, "--config", TOML, "--out", out
        )
        raw = out.read_bytes() if out.exists() else b""
        return result, raw.replace(b"\r\n", b"\n").decode("utf-8")

    def test_sections(self):
        self.assertEqual(self.built.returncode, 0, self.built.stderr)
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        page = parse(self.text)
        steps = self.golden["steps"]
        self.assertEqual(len(page.sections), 10)
        self.assertEqual([s["sha"] for s in page.sections], [s["sha"] for s in steps])
        self.assertEqual([s["hidden"] for s in page.sections], [False] + [True] * 9)
        four = page.sections[3]
        self.assertTrue(four["sha"].startswith("00394fb"))
        for part in ("Step 4 of 10", "2026-01-14", "#3", "day-02/track-a-cycle"):
            self.assertIn(part, four["heading"])
        self.assertEqual(four["events"], steps[3]["events"])
        self.assertEqual(four["flags"], [])
        ten = page.sections[9]
        self.assertTrue(ten["sha"].startswith("8c1b9f1"))
        self.assertIn("#11", ten["heading"])
        self.assertIn("Merge pull request #11 from acme/tooling/ci", ten["heading"])
        self.assertEqual(ten["paragraphs"], [])

    def test_flags_unverified(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        page = parse(self.text)
        self.assertTrue(page.sections[4]["sha"].startswith("bd726c8"))
        self.assertTrue(page.sections[7]["sha"].startswith("e5fa51f"))
        flagged = {i + 1: s["flags"] for i, s in enumerate(page.sections) if s["flags"]}
        self.assertEqual(
            flagged,
            {
                5: ["unverified: outside-area: area docs (scripts/run.py)"],
                8: [
                    (
                        "unverified: contract-impact: no contract impact "
                        "(tests/contract/test_api.py)"
                    )
                ],
            },
        )
        self.assertEqual(self.text.count('<li class="flag">'), 2)
        self.assertEqual(self.text.count(NOTE), 1)

    def test_pr_text_escaped(self):
        data = Path(self.tmp.name) / "escaped"
        ingested = bearing(
            "ingest", self.repo, "--prs", self.out / "prs.json", "--data", data
        )
        self.assertEqual(ingested.returncode, 0, ingested.stderr)
        with closing(sqlite3.connect(data / "bearing.db")) as conn:
            cur = conn.execute("UPDATE prs SET body = ? WHERE number = 3", (BODY,))
            self.assertEqual(cur.rowcount, 1)
            conn.commit()
        result, text = self.page(data, "escaped")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(text.count("<script"), 2)
        self.assertEqual(text.count("</script"), 2)
        paragraph = "x </script><script>alert(1)</script><!-- y"
        self.assertEqual(parse(text).sections[3]["paragraphs"], [paragraph])
        element = text.split(OPEN, 1)[1].split("</script>", 1)[0]
        self.assertEqual(json.loads(element)["steps"][3]["paragraph"], paragraph)

    def test_controls(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        page = parse(self.text)
        self.assertEqual(page.buttons, {"prev": "Previous", "next": "Next"})
        self.assertEqual(page.counter, "1 / 10")
        self.assertEqual(len(page.styles), 1)
        self.assertNotIn("url(", page.styles[0])
        self.assertNotIn("@import", page.styles[0])
        self.assertEqual(len(page.scripts), 2)
        script = page.scripts[1]
        self.assertNotIn("src", script["attrs"])
        for word in ("ArrowLeft", "ArrowRight", "hidden"):
            self.assertIn(word, script["text"])
        self.assertEqual(len(re.findall(r'src=|href="http', self.text)), 0)


class PageGraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.repo = cls.out / "repo"
        cls.built = run(BUILDER, cls.out)
        cls.data = Path(cls.tmp.name) / "data"
        cls.ingested = bearing(
            "ingest", cls.repo, "--prs", cls.out / "prs.json", "--data", cls.data
        )
        cls.raw0, cls.result0 = cls.page("0")
        cls.raw1, cls.result1 = cls.page("1")
        cls.text = cls.raw0.replace(b"\r\n", b"\n").decode("utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def page(cls, seed):
        # Two hash seeds: the same history must give the same bytes whatever the set order.
        out = Path(cls.tmp.name) / f"page-{seed}.html"
        env = {**ENV, "PYTHONHASHSEED": seed}
        result = bearing(
            "page",
            cls.repo,
            "--data",
            cls.data,
            "--config",
            TOML,
            "--out",
            out,
            env=env,
        )
        raw = out.read_bytes() if out.exists() else b""
        return raw, result

    def test_fixture_graphs(self):
        self.assertEqual(self.built.returncode, 0, self.built.stderr)
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        self.assertEqual(self.result0.returncode, 0, self.result0.stderr)
        page = parse(self.text)
        self.assertEqual(page.svgs, 10)
        self.assertEqual([s["svgs"] for s in page.sections], [1] * 10)
        four = page.sections[3]
        self.assertTrue(four["sha"].startswith("00394fb"))
        self.assertEqual(four["modules"]["app.a"], "module added cycle")
        self.assertEqual(four["modules"]["app.b"], "module added cycle")
        self.assertEqual(four["modules"]["app.crlf"], "module added")
        self.assertEqual(four["imports"][("app.a", "app.b")], "import added cycle")
        self.assertEqual(four["imports"][("app.b", "app.a")], "import added cycle")
        seven = page.sections[6]
        self.assertTrue(seven["sha"].startswith("fde93a4"))
        self.assertEqual(seven["modules"]["app.extra"], "module added")
        self.assertEqual(seven["modules"]["app.legacy"], "module removed")
        self.assertEqual(seven["modules"]["scripts.tools"], "module")
        self.assertNotIn("scripts.helpers", seven["modules"])
        eight = page.sections[7]
        self.assertTrue(eight["sha"].startswith("e5fa51f"))
        self.assertEqual(eight["imports"][("app.b", "app.a")], "import removed")
        self.assertEqual(eight["modules"]["tests.contract.test_api"], "module added")
        for value in [*eight["modules"].values(), *eight["imports"].values()]:
            self.assertNotIn("cycle", value.split())

    def test_same_under_two_seeds(self):
        self.assertEqual(self.result0.returncode, 0, self.result0.stderr)
        self.assertEqual(self.result1.returncode, 0, self.result1.stderr)
        text1 = self.raw1.replace(b"\r\n", b"\n").decode("utf-8")
        self.assertEqual(self.text.count("<svg"), 10)
        self.assertEqual(text1.count("<svg"), 10)
        self.assertEqual(self.raw0, self.raw1)
