"""The timeline command on the fixture: its lines, its --stats counts, its errors, and the target it leaves alone."""

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
LINES = [
    "62c4b2f #1 +module app.sub",
    "62c4b2f #1 +module app.sub.mod",
    "62c4b2f #1 +import app.sub.mod -> app.core",
    "62c4b2f #1 +import app.sub.mod -> app.pkg",
    "1756282 #2 +module scripts.run",
    "1756282 #2 +import scripts.helpers -> scripts.config",
    "1756282 #2 +import scripts.run -> scripts.helpers",
    "00394fb #3 +module app.a",
    "00394fb #3 +module app.b",
    "00394fb #3 +module app.crlf",
    "00394fb #3 +import app.a -> app.b",
    "00394fb #3 +import app.b -> app.a",
    "448fc4d #6 +module app.broken",
    "fde93a4 #8 +module app.extra",
    "fde93a4 #8 -module app.legacy",
    "fde93a4 #8 renamed scripts.helpers -> scripts.tools",
    "e5fa51f #9 +module tests.contract.test_api",
    "e5fa51f #9 -import app.b -> app.a",
]
EXPECTED = "".join(line + "\n" for line in LINES).encode()
# With pr_number NULL, the merge's lines carry #- and never the subject's number.
NULL_PR = [
    line.replace("fde93a4 #8 ", "fde93a4 #- ")
    if line.startswith("fde93a4 #8 ")
    else line
    for line in LINES
]


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "bearing", *args],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=ENV,
    )


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        env=ENV,
    )


class TimelineCliTest(unittest.TestCase):
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

    def repo(self):
        return self.out / "repo"

    def data_dir(self, name):
        # Each test makes its own data directories, so a test runs alone.
        return Path(self.tmp.name) / name

    def ingest(self, data):
        result = run(
            "ingest",
            str(self.repo()),
            "--prs",
            str(self.out / "prs.json"),
            "--data",
            str(data),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_lines(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data1 = self.data_dir("lines-1")
        self.ingest(data1)
        result = run("timeline", str(self.repo()), "--data", str(data1))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(result.stdout.replace(b"\r\n", b"\n"), EXPECTED)

        data2 = self.data_dir("lines-2")
        self.ingest(data2)
        conn = sqlite3.connect(data2 / "bearing.db")
        try:
            cursor = conn.execute(
                "UPDATE commits SET pr_number = NULL WHERE sha LIKE 'fde93a4%'"
            )
            self.assertEqual(cursor.rowcount, 1)
            conn.commit()
        finally:
            conn.close()
        result = run("timeline", str(self.repo()), "--data", str(data2))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(
            result.stdout.replace(b"\r\n", b"\n"),
            "".join(line + "\n" for line in NULL_PR).encode(),
        )

    def test_stats(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = self.data_dir("stats")
        self.ingest(data)
        first = run("timeline", str(self.repo()), "--data", str(data), "--stats")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout.replace(b"\r\n", b"\n"), EXPECTED)
        self.assertEqual(
            first.stderr.replace(b"\r\n", b"\n"),
            b"blobs parsed 28  cache hits 0\n",
        )
        second = run("timeline", str(self.repo()), "--data", str(data), "--stats")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout.replace(b"\r\n", b"\n"), EXPECTED)
        self.assertEqual(
            second.stderr.replace(b"\r\n", b"\n"),
            b"blobs parsed 0  cache hits 28\n",
        )
        # An ingest keeps the cache: the blobs are still in the store.
        self.ingest(data)
        third = run("timeline", str(self.repo()), "--data", str(data), "--stats")
        self.assertEqual(third.returncode, 0, third.stderr)
        self.assertEqual(
            third.stderr.replace(b"\r\n", b"\n"),
            b"blobs parsed 0  cache hits 28\n",
        )

    def test_errors(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        store = self.data_dir("errors-store")
        self.ingest(store)

        empty = self.data_dir("errors-empty")
        empty.mkdir()
        not_repo = self.data_dir("errors-not-repo")
        not_repo.mkdir()
        other = self.data_dir("errors-other")
        other.mkdir()
        self.assertEqual(git(other, "init", "-q").returncode, 0)
        bad = self.data_dir("errors-bad")
        bad.mkdir()
        (bad / "bearing.db").write_bytes(b"not a store\n")

        cases = [
            (
                str(self.repo()),
                empty,
                f"bearing: no store at {Path(empty) / 'bearing.db'}: run bearing ingest first\n",
            ),
            (
                str(not_repo),
                store,
                f"bearing: not a git repository: {not_repo}\n",
            ),
            (
                str(other),
                store,
                "bearing: not a commit: 62c4b2fcda436266c9cdd7ec8db866427452cfb9\n",
            ),
            (
                str(self.repo()),
                bad,
                f"bearing: cannot read store at {Path(bad) / 'bearing.db'}: file is not a database\n",
            ),
        ]
        for repo, data, message in cases:
            with self.subTest(message=message):
                result = run("timeline", repo, "--data", str(data))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(result.stdout, b"")
                self.assertEqual(
                    result.stderr.replace(b"\r\n", b"\n").decode(), message
                )
        self.assertEqual(list(empty.iterdir()), [])

    def test_read_only(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        refs = git(self.repo(), "for-each-ref")
        head = git(self.repo(), "rev-parse", "HEAD")
        data = self.data_dir("read-only")
        self.ingest(data)
        result = run("timeline", str(self.repo()), "--data", str(data))
        self.assertEqual(result.returncode, 0, result.stderr)
        for _ in range(2):
            result = run("timeline", str(self.repo()), "--data", str(data), "--stats")
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            git(self.repo(), "status", "--porcelain", "--ignored").stdout, b""
        )
        self.assertEqual(git(self.repo(), "for-each-ref").stdout, refs.stdout)
        self.assertEqual(git(self.repo(), "rev-parse", "HEAD").stdout, head.stdout)
