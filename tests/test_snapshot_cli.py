"""The snapshot command on the fixture: its errors, and the target it leaves alone."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}


class SnapshotCliTest(unittest.TestCase):
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

    def snapshot(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "bearing", "snapshot", *args],
            check=False,
            cwd=REPO,
            capture_output=True,
            env=ENV,
        )

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.out / "repo"), *args],
            check=False,
            capture_output=True,
            env=ENV,
        ).stdout

    def test_errors(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        empty = tempfile.mkdtemp(dir=self.tmp.name)
        cases = {
            "not-a-commit": (
                [str(self.out / "repo"), "no-such-ref"],
                b"bearing: not a commit: no-such-ref\n",
            ),
            "not-a-repo": (
                [empty, "main"],
                f"bearing: not a git repository: {empty}\n".encode(),
            ),
        }
        for name, (args, message) in cases.items():
            with self.subTest(name=name):
                result = self.snapshot(*args)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b"")
                self.assertEqual(result.stderr.replace(b"\r\n", b"\n"), message)

    def test_read_only(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        refs = self.git("for-each-ref")
        head = self.git("rev-parse", "HEAD")
        result = self.snapshot(str(self.out / "repo"), "main")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.snapshot(str(self.out / "repo"), "no-such-ref")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(self.git("status", "--porcelain", "--ignored"), b"")
        self.assertEqual(self.git("for-each-ref"), refs)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
