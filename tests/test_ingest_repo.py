"""The repository check of ingest: a path that is not a repository is refused before any database is written."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class IngestRepoTest(unittest.TestCase):
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

    def test_missing_path(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = Path(self.tmp.name) / "missing"
        data = Path(self.tmp.name) / "data-missing"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "ingest",
                str(repo),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(data),
            ],
            cwd=REPO,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(
            result.stderr.decode("utf-8").replace("\r\n", "\n"),
            f"bearing: not a git repository: {repo}\n",
        )
        self.assertFalse((data / "bearing.db").exists())

    def test_check_repo(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.snapshot.tree import SnapshotError, check_repo

        self.assertIsNone(check_repo(self.out / "repo"))
        plain = Path(tempfile.mkdtemp(dir=self.tmp.name))
        with self.assertRaises(SnapshotError) as caught:
            check_repo(plain)
        self.assertEqual(str(caught.exception), f"not a git repository: {plain}")
