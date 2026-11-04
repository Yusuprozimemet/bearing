"""The timeline's contract: the golden file is what `bearing timeline` prints for the fixture after `bearing ingest`."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "timeline.txt"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}


class TimelineContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.result = subprocess.run(
            [sys.executable, str(BUILDER), str(cls.out)],
            check=False,
            capture_output=True,
            text=True,
            env=ENV,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_golden(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = Path(self.tmp.name) / "data"
        ingest = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "ingest",
                str(self.out / "repo"),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(data),
            ],
            check=False,
            cwd=REPO,
            capture_output=True,
            env=ENV,
        )
        self.assertEqual(ingest.returncode, 0, ingest.stderr)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "timeline",
                str(self.out / "repo"),
                "--data",
                str(data),
            ],
            check=False,
            cwd=REPO,
            capture_output=True,
            env=ENV,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.replace(b"\r\n", b"\n"),
            GOLDEN.read_bytes().replace(b"\r\n", b"\n"),
        )
