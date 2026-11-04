"""The ingest line's contract: the golden file is what `bearing ingest` prints for the fixture."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "ingest.txt"


class IngestContractTest(unittest.TestCase):
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

    def test_golden(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "ingest",
                str(self.out / "repo"),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(Path(self.tmp.name) / "data"),
            ],
            check=False,
            cwd=REPO,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.replace(b"\r\n", b"\n"),
            GOLDEN.read_bytes().replace(b"\r\n", b"\n"),
        )
