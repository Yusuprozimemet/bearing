"""The direction command and changed_files on a directory that is not a repository, and on a repository without the commit."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
TOML = REPO / "tests" / "fixtures" / "bearing.toml"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
STORE_COMMIT = "62c4b2fcda436266c9cdd7ec8db866427452cfb9"


def run(*args, cwd=REPO):
    return subprocess.run(
        [sys.executable, "-m", "bearing", *args],
        check=False,
        cwd=cwd,
        capture_output=True,
        env=ENV,
    )


def text(data):
    return data.replace(b"\r\n", b"\n").decode()


class DirectionRepoTest(unittest.TestCase):
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
        cls.store = Path(cls.tmp.name) / "store"
        ingest = run(
            "ingest",
            str(cls.out / "repo"),
            "--prs",
            str(cls.out / "prs.json"),
            "--data",
            str(cls.store),
        )
        assert ingest.returncode == 0, ingest.stderr
        cls.empty = Path(cls.tmp.name) / "empty"
        cls.empty.mkdir()
        cls.other = Path(cls.tmp.name) / "other"
        cls.other.mkdir()
        subprocess.run(["git", "init", "-q", str(cls.other)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def direction(self, repo):
        return run(
            "direction",
            str(repo),
            "--data",
            str(self.store),
            "--config",
            str(TOML),
        )

    def test_not_a_repo(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        result = self.direction(self.empty)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(
            text(result.stderr), f"bearing: not a git repository: {self.empty}\n"
        )

    def test_not_a_commit(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        result = self.direction(self.other)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(
            text(result.stderr), f"bearing: not a commit: {STORE_COMMIT}\n"
        )

    def test_changed_files(self):
        from bearing.direction.changes import changed_files
        from bearing.snapshot.tree import SnapshotError

        with self.assertRaises(SnapshotError) as caught:
            changed_files(self.empty, STORE_COMMIT)
        self.assertEqual(str(caught.exception), f"not a git repository: {self.empty}")

        with self.assertRaises(SnapshotError) as caught:
            changed_files(self.other, STORE_COMMIT)
        self.assertEqual(str(caught.exception), f"not a commit: {STORE_COMMIT}")

    def test_one_git_call(self):
        from bearing.direction.changes import changed_files, commit_changes

        rows = [
            ("app/extra.py", 5, 0),
            ("app/legacy.py", 0, 3),
            ("scripts/run.py", 1, 1),
            ("scripts/tools.py", 0, 0),
        ]
        repo = self.out / "repo"
        with mock.patch("subprocess.run", wraps=subprocess.run) as spy:
            self.assertEqual(changed_files(repo, "fde93a4"), rows)
        self.assertEqual(spy.call_count, 1)

        with mock.patch("subprocess.run", wraps=subprocess.run) as spy:
            files, _renames = commit_changes(repo, "fde93a4")
        self.assertEqual(files, rows)
        self.assertEqual(spy.call_count, 1)
