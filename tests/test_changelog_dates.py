"""The changelog's --since and --until take only dates in YYYY-MM-DD form, and refuse the rest before the store is read."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


def run(*args, env=None):
    return subprocess.run(
        [sys.executable, "-m", "bearing", *args],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=env,
    )


class ChangelogDatesTest(unittest.TestCase):
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
        cls.data = Path(cls.tmp.name) / "data"
        cls.ingested = run(
            "ingest",
            str(cls.out / "repo"),
            "--prs",
            str(cls.out / "prs.json"),
            "--data",
            str(cls.data),
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def assertRefused(self, result, last_line):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, b"")
        stderr = result.stderr.decode("utf-8").replace("\r\n", "\n")
        self.assertTrue(stderr.startswith("usage: bearing changelog"), stderr)
        self.assertEqual(stderr.rstrip("\n").splitlines()[-1], last_line)

    def test_word(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        self.assertRefused(
            run("changelog", "--since", "yesterday", "--data", str(self.data)),
            "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: 'yesterday'",
        )
        self.assertRefused(
            run("changelog", "--since", "it's", "--data", str(self.data)),
            "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: 'it's'",
        )

    def test_basic_form(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        self.assertRefused(
            run("changelog", "--since", "20260121", "--data", str(self.data)),
            "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: '20260121'",
        )

    def test_week_date(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        self.assertRefused(
            run("changelog", "--since", "2026-W03-2", "--data", str(self.data)),
            "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: '2026-W03-2'",
        )

    def test_no_such_day(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        self.assertRefused(
            run("changelog", "--since", "2026-02-30", "--data", str(self.data)),
            "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: '2026-02-30'",
        )

    def test_until(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        self.assertRefused(
            run("changelog", "--until", "20260121", "--data", str(self.data)),
            "bearing changelog: error: argument --until: not a date in YYYY-MM-DD form: '20260121'",
        )

    def test_no_store(self):
        missing = Path(self.tmp.name) / "missing"
        self.assertRefused(
            run("changelog", "--since", "20260121", "--data", str(missing)),
            "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: '20260121'",
        )
        self.assertFalse(missing.exists())
