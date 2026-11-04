"""The changelog command on the fixture: its golden output, a date range, UTF-8 output and its errors."""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "changelog.md"
RANGE = [
    "# Changelog",
    "",
    "## day-02",
    "",
    "- #3 day-02/track-a-cycle (2026-01-14)",
    "  A small change to the fixture, so the tests have a real case to read.",
    "- #6 day-02/track-b-grow (2026-01-21)",
    "  A small change to the fixture, so the tests have a real case to read.",
    "",
    "## day-03",
    "",
    "- #8 day-03/track-a-rename (2026-01-23)",
    "  A small change to the fixture, so the tests have a real case to read.",
    "",
    "## docs",
    "",
    "- #5 docs/typo-fix (2026-01-19)",
    "  A small change to the fixture, so the tests have a real case to read.",
]


def run(*args, env=None):
    return subprocess.run(
        [sys.executable, "-m", "bearing", *args],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=env,
    )


class ChangelogCliTest(unittest.TestCase):
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

    def test_golden(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        result = run("changelog", "--data", str(self.data))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.replace(b"\r\n", b"\n"),
            GOLDEN.read_bytes().replace(b"\r\n", b"\n"),
        )
        merges = int(re.search(rb"merges (\d+)", self.ingested.stdout).group(1))
        entries = [
            line
            for line in result.stdout.replace(b"\r\n", b"\n").split(b"\n")
            if line.startswith(b"- #")
        ]
        self.assertEqual(merges, 10)
        self.assertEqual(len(entries), merges)

    def test_range(self):
        self.assertEqual(self.ingested.returncode, 0, self.ingested.stderr)
        result = run(
            "changelog",
            "--data",
            str(self.data),
            "--since",
            "2026-01-14",
            "--until",
            "2026-01-23",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.replace(b"\r\n", b"\n"),
            ("\n".join(RANGE) + "\n").encode("utf-8"),
        )
        result = run("changelog", "--data", str(self.data), "--since", "2026-02-01")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.replace(b"\r\n", b"\n"), b"# Changelog\n")


class OutputEncodingTest(unittest.TestCase):
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

    def test_utf8_stdout(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        records = json.loads((self.out / "prs.json").read_bytes().decode("utf-8"))
        changed = 0
        for record in records:
            if record["number"] in (1, 7):
                record["title"] = "Café → bar"
                changed += 1
        self.assertEqual(changed, 2)
        prs = Path(self.tmp.name) / "prs-utf8.json"
        prs.write_bytes(
            json.dumps(records, sort_keys=True, indent=2, ensure_ascii=False).encode(
                "utf-8"
            )
            + b"\n"
        )
        # A code page that cannot hold the title: the output must still be UTF-8.
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        data = Path(self.tmp.name) / "data-utf8"
        ingested = run(
            "ingest",
            str(self.out / "repo"),
            "--prs",
            str(prs),
            "--data",
            str(data),
            env=env,
        )
        self.assertEqual(ingested.returncode, 0, ingested.stderr)
        self.assertIn(
            "unmatched PR #7 e21c62d Café → bar",
            ingested.stdout.decode("utf-8").splitlines(),
        )
        result = run("changelog", "--data", str(data), env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "- #1 Café → bar (2026-01-07)",
            result.stdout.decode("utf-8").splitlines(),
        )


class DataDirTest(unittest.TestCase):
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

    def assertBearingError(self, result):
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.startswith(b"bearing: "), result.stderr)

    def test_errors(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        afile = Path(self.tmp.name) / "afile"
        afile.write_bytes(b"not a store\n")
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        prs = str(self.out / "prs.json")
        self.assertBearingError(
            run("ingest", str(self.out / "repo"), "--prs", prs, "--data", str(afile))
        )
        self.assertBearingError(run("changelog", "--data", str(afile)))
        self.assertBearingError(run("changelog", "--data", str(empty)))
        self.assertFalse((empty / "bearing.db").exists())
        self.assertEqual(list(empty.iterdir()), [])
        result = run("changelog", "--data", str(empty), "--since", "2026-13-01")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(b"--since", result.stderr)
