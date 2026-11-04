"""Reading a branch's area and a PR body's paragraph: the two text functions, on the fixture and on made-up bodies."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class AreaTest(unittest.TestCase):
    def test_areas(self):
        from bearing.ingest.text import area

        cases = [
            ("day-03/track-a-rename", "day-03"),
            ("docs/guide", "docs"),
            ("tooling/ci", "tooling"),
            ("release", "other"),
            ("", "other"),
            (None, "other"),
            ("other-owner/patch-1/x", "other-owner"),
        ]
        for branch, expected in cases:
            with self.subTest(branch=branch):
                self.assertEqual(area(branch), expected)


class ParagraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.result = subprocess.run(
            [sys.executable, str(BUILDER), str(cls.out)],
            check=False,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_paragraphs(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.text import what_i_built

        records = json.loads((self.out / "prs.json").read_bytes().decode("utf-8"))
        bodies = {record["number"]: record["body"] for record in records}
        cases = [
            (
                bodies[1],
                "A small change to the fixture, so the tests have a real case to read.",
            ),
            (
                bodies[2],
                "A script that prints a greeting, and the helper module it imports.",
            ),
            (bodies[9], "app/b.py stops importing app.a, so the cycle is gone."),
            ("", ""),
            (
                "### What I built\r\n\r\nLine one  \r\nline two\r\n\r\nMore\r\n",
                "Line one\nline two",
            ),
            ("Intro.\n\n## What I built\n\nBuilt it.\n", "Built it."),
            ("## What I built\n\n## Why\n\nBecause.\n", "Because."),
            ("## Heading only\n", ""),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                self.assertEqual(what_i_built(body), expected)
