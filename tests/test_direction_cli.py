"""The direction command on the fixture: its report, the threshold in its config, and its errors."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
TOML = REPO / "tests" / "fixtures" / "bearing.toml"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
CHURN = [
    "## Churn",
    "",
    "| Week | Area | Added | Deleted |",
    "|---|---|---|---|",
    "| 2026-W02 | app | 13 | 0 |",
    "| 2026-W02 | lib | 4 | 0 |",
    "| 2026-W02 | tooling | 7 | 0 |",
    "| 2026-W03 | app | 19 | 0 |",
    "| 2026-W03 | docs | 5 | 0 |",
    "| 2026-W03 | lib | 4 | 0 |",
    "| 2026-W04 | app | 247 | 3 |",
    "| 2026-W04 | tooling | 2 | 2 |",
    "| 2026-W05 | app | 4 | 2 |",
    "| 2026-W05 | docs | 3 | 0 |",
    "| 2026-W05 | lib | 4 | 0 |",
    "| 2026-W05 | other | 5 | 0 |",
    "| 2026-W05 | tooling | 1 | 0 |",
    "",
]
COUPLING_HEAD = [
    "## Coupling",
    "",
    "| File | File | PRs | Hidden dependency |",
    "|---|---|---|---|",
]
ROW_APP_LIB = "| app/core.py | src/lib/util.py | #1, #3, #9 | app, lib |"
EXPECTED = CHURN + COUPLING_HEAD + [ROW_APP_LIB]
THRESHOLD_ROWS = [
    "| app/b.py | app/core.py | #3, #9 | no |",
    "| app/b.py | src/lib/util.py | #3, #9 | app, lib |",
    ROW_APP_LIB,
]


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


class DirectionCliTest(unittest.TestCase):
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

    def direction(self, data, config):
        return run(
            "direction",
            str(self.repo()),
            "--data",
            str(data),
            "--config",
            str(config),
        )

    def test_fixture_report(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertEqual(len(EXPECTED), 23)
        data = self.data_dir("report")
        self.ingest(data)
        result = self.direction(data, TOML)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(text(result.stdout), "".join(line + "\n" for line in EXPECTED))

    def test_threshold(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = self.data_dir("threshold")
        self.ingest(data)
        raw = TOML.read_bytes()
        self.assertIn(b"min_prs = 3", raw)

        config2 = Path(self.tmp.name) / "min2.toml"
        config2.write_bytes(raw.replace(b"min_prs = 3", b"min_prs = 2"))
        result = self.direction(data, config2)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = text(result.stdout).split("\n")
        self.assertEqual(lines[:18], CHURN)
        # Day 9 adds a section after Coupling: only a blank line may follow the rows.
        self.assertEqual(lines[18:25], COUPLING_HEAD + THRESHOLD_ROWS)
        self.assertEqual(lines[25], "")

        config4 = Path(self.tmp.name) / "min4.toml"
        config4.write_bytes(raw.replace(b"min_prs = 3", b"min_prs = 4"))
        result = self.direction(data, config4)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = text(result.stdout).split("\n")
        self.assertEqual(lines[:18], CHURN)
        self.assertEqual(lines[18:22], COUPLING_HEAD)
        self.assertEqual(lines[22], "")

    def test_errors(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = self.data_dir("errors")
        self.ingest(data)

        missing = Path(self.tmp.name) / "missing.toml"
        result = self.direction(data, missing)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(
            text(result.stderr),
            f"bearing: no config at {missing}: pass --config FILE\n",
        )

        broken = Path(self.tmp.name) / "broken.toml"
        broken.write_bytes(b"[areas\n")
        result = self.direction(data, broken)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(
            text(result.stderr).startswith(f"bearing: cannot read config {broken}: "),
            result.stderr,
        )

        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        result = self.direction(empty, TOML)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        db = empty / "bearing.db"
        self.assertEqual(
            text(result.stderr),
            f"bearing: no store at {db}: run bearing ingest first\n",
        )
        self.assertFalse(db.exists())

        bare = Path(self.tmp.name) / "bare"
        bare.mkdir()
        result = run("direction", str(self.repo()), cwd=bare)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(
            text(result.stderr),
            "bearing: no config at bearing.toml: pass --config FILE\n",
        )
        self.assertFalse((bare / ".bearing").exists())
