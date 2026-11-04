"""The first-parent history of the fixture, and the merge subjects parsed from it."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class FirstParentTest(unittest.TestCase):
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

    def test_fixture_line(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.history import read_first_parent

        commits = read_first_parent(self.out / "repo")
        expected = subprocess.run(
            [
                "git",
                "-C",
                str(self.out / "repo"),
                "log",
                "--first-parent",
                "--reverse",
                "--format=%H",
                "main",
            ],
            check=False,
            capture_output=True,
            text=True,
        ).stdout.split()
        self.assertEqual(len(commits), 12)
        self.assertEqual([c.sha for c in commits], expected)
        self.assertEqual(
            [len(c.parents) for c in commits], [0, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2]
        )
        self.assertEqual(commits[0].committed_at, "2026-01-05T12:00:00+00:00")
        self.assertEqual(
            commits[-1].subject, "Merge pull request #11 from acme/tooling/ci"
        )


class MergeSubjectTest(unittest.TestCase):
    def test_subjects(self):
        from bearing.ingest.history import parse_merge_subject

        self.assertEqual(
            parse_merge_subject("Merge pull request #7 from acme/docs/notes"),
            (7, "acme", "docs/notes"),
        )
        self.assertEqual(
            parse_merge_subject("Merge pull request #12 from other-owner/patch-1"),
            (12, "other-owner", "patch-1"),
        )
        self.assertEqual(
            parse_merge_subject("Merge pull request #10 from acme/release"),
            (10, "acme", "release"),
        )
        self.assertIsNone(parse_merge_subject("Grow the core module (#6)"))
        self.assertIsNone(parse_merge_subject("Fix README typo"))
        self.assertIsNone(parse_merge_subject("Merge branch 'main' into x"))
