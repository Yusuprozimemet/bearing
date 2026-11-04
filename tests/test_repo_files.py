"""The repository's ignore and attribute rules, asked of git itself."""

import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class RepoFilesTest(unittest.TestCase):
    def test_gitignore(self):
        result = subprocess.run(
            ["git", "check-ignore", "bearing.egg-info/PKG-INFO", ".bearing/bearing.db"],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        lines = [line.rstrip("\r") for line in result.stdout.splitlines()]
        self.assertEqual(lines, ["bearing.egg-info/PKG-INFO", ".bearing/bearing.db"])

    def test_fixtures_eol_lf(self):
        result = subprocess.run(
            ["git", "check-attr", "eol", "--", "tests/fixtures/make_repo.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "tests/fixtures/make_repo.py: eol: lf")
