"""git's numstat, parsed: the rename and binary rules, and the merge commit of the fixture."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class ChangesTest(unittest.TestCase):
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

    def test_parse_numstat(self):
        from bearing.direction.changes import parse_numstat

        raw = b"3\t1\tapp/a.py\x00-\t-\tlogo.png\x000\t0\t\x00scripts/helpers.py\x00scripts/tools.py\x00"
        self.assertEqual(
            parse_numstat(raw),
            [("app/a.py", 3, 1), ("logo.png", 0, 0), ("scripts/tools.py", 0, 0)],
        )

    def test_fixture_merge(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.direction.changes import changed_files
        from bearing.snapshot.tree import SnapshotError

        repo = self.out / "repo"
        self.assertEqual(
            changed_files(repo, "fde93a4"),
            [
                ("app/extra.py", 5, 0),
                ("app/legacy.py", 0, 3),
                ("scripts/run.py", 1, 1),
                ("scripts/tools.py", 0, 0),
            ],
        )
        with self.assertRaises(SnapshotError):
            changed_files(repo, "0" * 40)
