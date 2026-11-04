"""The snapshot line's contract: the golden file is what `bearing snapshot` prints for the fixture."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "snapshot-448fc4d.json"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}


class SnapshotContractTest(unittest.TestCase):
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
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "snapshot",
                str(self.out / "repo"),
                "448fc4dc915289f0b3f0254cf80360b56f48513a",
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
