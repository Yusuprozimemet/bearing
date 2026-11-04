"""Storing the fixture's history: the counts after one ingest, and after a second one into the same store."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class StoreTest(unittest.TestCase):
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

    def test_stored_once(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.history import read_first_parent
        from bearing.ingest.mapping import load_prs, map_history
        from bearing.store.db import open_store, save

        commits = read_first_parent(self.out / "repo")
        records = load_prs(self.out / "prs.json")
        result = map_history(commits, records)
        data = Path(self.tmp.name) / "data"
        for run in (1, 2):
            with self.subTest(run=run):
                conn = open_store(data)
                save(conn, commits, records, result)
                counts = {
                    "commits": conn.execute("SELECT COUNT(*) FROM commits").fetchone()[
                        0
                    ],
                    "matched": conn.execute(
                        "SELECT COUNT(*) FROM commits WHERE pr_number IS NOT NULL"
                    ).fetchone()[0],
                    "direct": conn.execute(
                        "SELECT COUNT(*) FROM commits WHERE kind = 'direct'"
                    ).fetchone()[0],
                    "prs": conn.execute("SELECT COUNT(*) FROM prs").fetchone()[0],
                }
                self.assertEqual(
                    counts,
                    {"commits": 12, "matched": 9, "direct": 2, "prs": 10},
                )
                self.assertEqual(
                    conn.execute("SELECT name FROM schema_migrations").fetchall(),
                    [("001_history.sql",)],
                )
                self.assertTrue((data / "bearing.db").exists())
                conn.close()
