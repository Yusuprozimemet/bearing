"""Ingest on a branch other than main: its first-parent line, gh's --base, and the errors for a name that is not a local branch."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "ingest.txt"
REAL_RUN = subprocess.run
RELEASE_LINES = (
    "merges 9  matched 9  unmatched merges 0  unmatched PRs 1  direct 2\n"
    "unmatched PR #10 86761f2 release\n"
)
GH_RELEASE = [
    "gh",
    "pr",
    "list",
    "--state",
    "merged",
    "--limit",
    "1000",
    "--json",
    "number,title,body,headRefName,baseRefName,mergeCommit,mergedAt",
    "--base",
    "release",
]


def gh_fake(outcome, calls):
    # Records each gh call and answers it with outcome (raised if it is an exception); every
    # other call, git's, runs for real.
    def run(*args, **kwargs):
        if args and args[0][0] == "gh":
            calls.append((args, kwargs))
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        return REAL_RUN(*args, **kwargs)

    return run


class IngestBranchTest(unittest.TestCase):
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
        if cls.result.returncode == 0:
            # A ref the fixture does not hold, so a tag can be asked for as a branch.
            REAL_RUN(
                ["git", "-C", str(cls.out / "repo"), "tag", "v-tag", "main"],
                check=True,
                capture_output=True,
            )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_main(self, argv, outcome):
        from bearing.cli import main

        calls = []
        out, err = io.StringIO(), io.StringIO()
        with (
            patch("subprocess.run", gh_fake(outcome, calls)),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
        ):
            try:
                code = main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue(), calls

    def test_main_named(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = self.out / "repo"
        data = Path(self.tmp.name) / "data-main-named"
        code, out, err, _ = self.run_main(
            [
                "ingest",
                str(repo),
                "--prs",
                str(self.out / "prs.json"),
                "--branch",
                "main",
                "--data",
                str(data),
            ],
            None,
        )
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")
        self.assertEqual(out, GOLDEN.read_text(encoding="utf-8"))

    def test_release(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = self.out / "repo"
        data = Path(self.tmp.name) / "data-release"
        code, out, err, _ = self.run_main(
            [
                "ingest",
                str(repo),
                "--prs",
                str(self.out / "prs.json"),
                "--branch",
                "release",
                "--data",
                str(data),
            ],
            None,
        )
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")
        self.assertEqual(out, RELEASE_LINES)

        code, out, err, _ = self.run_main(["changelog", "--data", str(data)], None)
        self.assertEqual(code, 0, err)
        lines = out.splitlines()
        self.assertIn("- #7 docs/notes (2026-01-27)", lines)
        self.assertFalse(any(line.startswith("- #10 ") for line in lines))
        self.assertFalse(any(line.startswith("- #11 ") for line in lines))

    def test_gh_base(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = self.out / "repo"
        data = Path(self.tmp.name) / "data-gh-base"
        text = (self.out / "prs.json").read_text(encoding="utf-8")
        outcome = subprocess.CompletedProcess(["gh"], 0, stdout=text, stderr="")
        code, out, err, calls = self.run_main(
            ["ingest", str(repo), "--branch", "release", "--data", str(data)], outcome
        )
        self.assertEqual(code, 0, err)
        self.assertEqual(out, RELEASE_LINES)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], (GH_RELEASE,))
        self.assertEqual(calls[0][1]["cwd"], str(repo))

    def test_not_a_branch(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = self.out / "repo"
        tip = REAL_RUN(
            ["git", "-C", str(repo), "rev-parse", "main"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        cases = [
            ("no-such-branch", "no-such-branch"),
            ("v-tag", "v-tag"),
            ("main-tip-sha", tip),
        ]
        for name, branch in cases:
            with self.subTest(name=name):
                data = Path(self.tmp.name) / f"data-not-a-branch-{name}"
                code, out, err, _ = self.run_main(
                    [
                        "ingest",
                        str(repo),
                        "--prs",
                        str(self.out / "prs.json"),
                        "--branch",
                        branch,
                        "--data",
                        str(data),
                    ],
                    None,
                )
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertEqual(
                    err, f"bearing: --branch {branch}: not a local branch in {repo}\n"
                )
                self.assertFalse((data / "bearing.db").exists())

    def test_no_main(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        empty = Path(tempfile.mkdtemp(dir=self.tmp.name))
        REAL_RUN(["git", "init", "-q", str(empty)], check=True, capture_output=True)
        data = Path(self.tmp.name) / "data-no-main"
        code, out, err, _ = self.run_main(
            [
                "ingest",
                str(empty),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(data),
            ],
            None,
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertEqual(
            err, f"bearing: --branch main: not a local branch in {empty}\n"
        )
        self.assertFalse((data / "bearing.db").exists())

    def test_not_a_repo(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        plain = Path(tempfile.mkdtemp(dir=self.tmp.name))
        data = Path(self.tmp.name) / "data-not-a-repo"
        code, out, err, _ = self.run_main(
            [
                "ingest",
                str(plain),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(data),
            ],
            None,
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("bearing: fatal: not a git repository"), err)
        self.assertFalse((data / "bearing.db").exists())
