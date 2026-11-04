"""The blob cache: what it returns, what it counts, and what a second store and a second snapshot see of it."""

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
MAIN_SHA = "448fc4dc915289f0b3f0254cf80360b56f48513a"


def boom():
    raise AssertionError("read called")


class BlobCacheTest(unittest.TestCase):
    def test_round_trip(self):
        from bearing.snapshot.cache import BlobCache
        from bearing.store.db import open_store

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            data = Path(tmp)
            conn = open_store(data)
            cache = BlobCache(conn)
            self.assertEqual(
                cache.get("a" * 40, lambda: b"import b\nfrom . import c\n"),
                (2, [(0, "b", ()), (1, "", ("c",))]),
            )
            self.assertEqual((cache.parsed, cache.hits), (1, 0))
            self.assertEqual(
                cache.get("a" * 40, boom),
                (2, [(0, "b", ()), (1, "", ("c",))]),
            )
            self.assertEqual((cache.parsed, cache.hits), (1, 0))
            self.assertEqual(cache.get("b" * 40, lambda: b"def f(:\n"), (1, None))
            conn.commit()
            conn.close()

            conn2 = sqlite3.connect(data / "bearing.db")
            cache2 = BlobCache(conn2)
            result = cache2.get("a" * 40, boom)
            self.assertEqual(result, (2, [(0, "b", ()), (1, "", ("c",))]))
            self.assertIs(type(result[1][0]), tuple)
            self.assertEqual(cache2.get("b" * 40, boom), (1, None))
            self.assertEqual((cache2.parsed, cache2.hits), (0, 2))
            conn2.close()


class SnapshotCacheTest(unittest.TestCase):
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

    def test_counts(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.snapshot.cache import BlobCache
        from bearing.snapshot.tree import snapshot
        from bearing.store.db import open_store

        repo = self.out / "repo"
        conn = open_store(Path(self.tmp.name) / "data")
        cache = BlobCache(conn)
        self.assertEqual(
            snapshot(repo, MAIN_SHA, cache),
            snapshot(repo, MAIN_SHA),
        )
        self.assertEqual((cache.parsed, cache.hits), (15, 0))
        self.assertEqual(
            snapshot(repo, "main", cache),
            snapshot(repo, "main"),
        )
        self.assertEqual((cache.parsed, cache.hits), (21, 0))
        conn.commit()
        cache2 = BlobCache(conn)
        self.assertEqual(
            snapshot(repo, "main", cache2),
            snapshot(repo, "main"),
        )
        self.assertEqual((cache2.parsed, cache2.hits), (0, 16))
        conn.close()
