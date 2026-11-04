"""The ingest command on the fixture: the report it prints, the target it leaves alone, and its errors."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "ingest.txt"


class IngestCliTest(unittest.TestCase):
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

    def ingest(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "bearing", "ingest", *args],
            check=False,
            cwd=REPO,
            capture_output=True,
        )

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.out / "repo"), *args],
            check=False,
            capture_output=True,
        ).stdout

    def test_report(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = Path(self.tmp.name) / "data-report"
        result = self.ingest(
            str(self.out / "repo"),
            "--prs",
            str(self.out / "prs.json"),
            "--data",
            str(data),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        golden = GOLDEN.read_bytes()
        self.assertEqual(
            result.stdout.replace(b"\r\n", b"\n"), golden.replace(b"\r\n", b"\n")
        )

    def test_target_untouched(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        refs = self.git("for-each-ref")
        head = self.git("rev-parse", "HEAD")
        data = Path(self.tmp.name) / "data-untouched"
        result = self.ingest(
            str(self.out / "repo"),
            "--prs",
            str(self.out / "prs.json"),
            "--data",
            str(data),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("status", "--porcelain", "--ignored"), b"")
        self.assertEqual(self.git("for-each-ref"), refs)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertTrue((data / "bearing.db").exists())

    def test_errors(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        empty = Path(tempfile.mkdtemp(dir=self.tmp.name))
        cases = {
            "missing-prs": [
                str(self.out / "repo"),
                "--prs",
                str(Path(self.tmp.name) / "missing.json"),
                "--data",
                str(Path(self.tmp.name) / "data-err1"),
            ],
            "not-a-repo": [
                str(empty),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(Path(self.tmp.name) / "data-err2"),
            ],
        }
        for name, args in cases.items():
            with self.subTest(name=name):
                result = self.ingest(*args)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b"")
                self.assertTrue(result.stderr.startswith(b"bearing: "), result.stderr)
