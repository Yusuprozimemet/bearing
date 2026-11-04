"""The fixture's HEAD is pinned: two builds give the same history and the same prs.json."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
# HEAD of main after the builder's last merge. A change to the builder's history moves it, and
# every test that reads the history with it.
HEAD_SHA = "8c1b9f1b90d3e582590942e15b131cea986d94c3"


class FixtureTest(unittest.TestCase):
    def build(self, parent):
        out = Path(parent) / "out"
        result = subprocess.run(
            [sys.executable, str(BUILDER), str(out)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        head = subprocess.run(
            ["git", "-C", str(out / "repo"), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(head.returncode, 0, head.stderr)
        return head.stdout.strip(), (out / "prs.json").read_bytes()

    def test_head_sha(self):
        with (
            tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as first,
            tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as second,
        ):
            head_a, prs_a = self.build(first)
            head_b, prs_b = self.build(second)
        self.assertEqual(head_a, head_b)
        self.assertEqual(prs_a, prs_b)
        self.assertEqual(head_a, HEAD_SHA)
