"""A store Bearing cannot read: the CLI refuses it, says so on stderr, and leaves the file as it was."""

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class BrokenStoreTest(unittest.TestCase):
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

    def bearing(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "bearing", *args],
            check=False,
            cwd=REPO,
            capture_output=True,
        )

    def test_changelog_refuses(self):
        for name in ("empty", "text", "schema"):
            with self.subTest(store=name):
                data = Path(self.tmp.name) / f"data-changelog-{name}"
                data.mkdir()
                path = data / "bearing.db"
                if name == "empty":
                    path.write_bytes(b"")
                elif name == "text":
                    path.write_bytes(b"not a database, just text")
                else:
                    conn = sqlite3.connect(path)
                    conn.execute("CREATE TABLE x (a)")
                    conn.commit()
                    conn.close()
                before = path.read_bytes()
                result = self.bearing("changelog", "--data", str(data))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(result.stdout, b"")
                self.assertTrue(
                    result.stderr.decode("utf-8").startswith(
                        "bearing: cannot read store at "
                    )
                )
                self.assertEqual(path.read_bytes(), before)

    def test_ingest_refuses(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = Path(self.tmp.name) / "data-ingest"
        data.mkdir()
        (data / "bearing.db").write_bytes(b"not a database, just text")
        result = self.bearing(
            "ingest",
            str(self.out / "repo"),
            "--prs",
            str(self.out / "prs.json"),
            "--data",
            str(data),
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(
            result.stderr.decode("utf-8").startswith("bearing: cannot open store at ")
        )
