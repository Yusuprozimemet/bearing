"""The command line's argument errors: no command, dates in the wrong order, and equal dates."""

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


class CliErrorsTest(unittest.TestCase):
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

    def test_no_command(self):
        result = run()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, b"")
        stderr = result.stderr.decode("utf-8").replace("\r\n", "\n")
        self.assertTrue(stderr.startswith("usage: bearing "), stderr)
        self.assertEqual(
            stderr.rstrip("\n").splitlines()[-1],
            "bearing: error: the following arguments are required: command",
        )

    def test_reversed_dates(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        result = run(
            "changelog",
            "--data",
            str(self.data),
            "--since",
            "2026-01-23",
            "--until",
            "2026-01-21",
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, b"")
        stderr = result.stderr.decode("utf-8").replace("\r\n", "\n")
        self.assertTrue(stderr.startswith("usage: bearing changelog "), stderr)
        self.assertEqual(
            stderr.rstrip("\n").splitlines()[-1],
            "bearing changelog: error: --since 2026-01-23 is after --until 2026-01-21",
        )

    def test_reversed_dates_no_store(self):
        missing = Path(self.tmp.name) / "missing"
        reversed_args = ["changelog", "--since", "2026-01-23", "--until", "2026-01-21"]
        expected = run(*reversed_args, "--data", str(self.data))
        result = run(*reversed_args, "--data", str(missing))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.returncode, expected.returncode)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stdout, expected.stdout)
        self.assertEqual(
            result.stderr.decode("utf-8").replace("\r\n", "\n"),
            expected.stderr.decode("utf-8").replace("\r\n", "\n"),
        )
        stderr = result.stderr.decode("utf-8").replace("\r\n", "\n")
        self.assertEqual(
            stderr.rstrip("\n").splitlines()[-1],
            "bearing changelog: error: --since 2026-01-23 is after --until 2026-01-21",
        )
        self.assertFalse(missing.exists())

    def test_equal_dates(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        result = run(
            "changelog",
            "--data",
            str(self.data),
            "--since",
            "2026-01-21",
            "--until",
            "2026-01-21",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(
            result.stdout.decode("utf-8").replace("\r\n", "\n").splitlines(),
            [
                "# Changelog",
                "",
                "## day-02",
                "",
                "- #6 day-02/track-b-grow (2026-01-21)",
                "  A small change to the fixture, so the tests have a real case to read.",
            ],
        )
