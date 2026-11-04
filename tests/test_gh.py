"""The gh reader: its command and output, its errors, and ingest on gh's records and on a --prs file."""

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


class FetchPrsTest(unittest.TestCase):
    def test_command_and_output(self):
        from bearing.ingest.gh import fetch_prs

        command = [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "1000",
            "--json",
            "number,title,body,headRefName,baseRefName,mergeCommit,mergedAt",
        ]
        outcome = subprocess.CompletedProcess(
            command, 0, stdout='[{"number": 1, "title": "Café → bar"}]', stderr=""
        )
        calls = []
        with patch("subprocess.run", gh_fake(outcome, calls)):
            records = fetch_prs("some/repo")
        self.assertEqual(records, [{"number": 1, "title": "Café → bar"}])
        self.assertEqual(len(calls), 1)
        args, kwargs = calls[0]
        self.assertEqual(args, (command,))
        self.assertEqual(
            kwargs,
            {"cwd": "some/repo", "capture_output": True, "encoding": "utf-8"},
        )

    def test_errors(self):
        from bearing.ingest.gh import GhError, fetch_prs

        cases = [
            (
                "not-found",
                FileNotFoundError(),
                "gh not found: install GitHub's CLI or pass --prs FILE",
            ),
            (
                "exit-1",
                subprocess.CompletedProcess(
                    ["gh"], 1, stdout="", stderr="HTTP 401: Bad credentials\n"
                ),
                "gh pr list failed: HTTP 401: Bad credentials",
            ),
            (
                "exit-4",
                subprocess.CompletedProcess(["gh"], 4, stdout="", stderr=""),
                "gh pr list failed: exit 4",
            ),
        ]
        for name, outcome, message in cases:
            with self.subTest(name=name):
                with (
                    patch("subprocess.run", gh_fake(outcome, [])),
                    self.assertRaises(GhError) as caught,
                ):
                    fetch_prs("some/repo")
                self.assertEqual(str(caught.exception), message)
        with self.subTest(name="not-json"):
            outcome = subprocess.CompletedProcess(
                ["gh"], 0, stdout="not json", stderr=""
            )
            with (
                patch("subprocess.run", gh_fake(outcome, [])),
                self.assertRaises(GhError) as caught,
            ):
                fetch_prs("some/repo")
            self.assertTrue(
                str(caught.exception).startswith("gh pr list printed no JSON: ")
            )


class IngestLiveTest(unittest.TestCase):
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

    def gh_answer(self):
        text = (self.out / "prs.json").read_text(encoding="utf-8")
        return subprocess.CompletedProcess(["gh"], 0, stdout=text, stderr="")

    def run_main(self, main, argv, outcome):
        calls = []
        out, err = io.StringIO(), io.StringIO()
        with (
            patch("subprocess.run", gh_fake(outcome, calls)),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
        ):
            code = main(argv)
        return code, out.getvalue(), err.getvalue(), calls

    def test_without_prs(self):
        from bearing.cli import main

        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = self.out / "repo"
        data = Path(self.tmp.name) / "data-without-prs"
        code, out, err, calls = self.run_main(
            main, ["ingest", str(repo), "--data", str(data)], self.gh_answer()
        )
        self.assertEqual(code, 0, err)
        self.assertEqual(out, GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]["cwd"], str(repo))

    def test_gh_errors(self):
        from bearing.cli import main

        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = self.out / "repo"
        cases = [
            (
                "not-found",
                FileNotFoundError(),
                "bearing: gh not found: install GitHub's CLI or pass --prs FILE\n",
            ),
            (
                "exit-1",
                subprocess.CompletedProcess(
                    ["gh"], 1, stdout="", stderr="HTTP 401: Bad credentials\n"
                ),
                "bearing: gh pr list failed: HTTP 401: Bad credentials\n",
            ),
        ]
        for name, outcome, message in cases:
            with self.subTest(name=name):
                data = Path(self.tmp.name) / f"data-gh-{name}"
                code, out, err, _ = self.run_main(
                    main, ["ingest", str(repo), "--data", str(data)], outcome
                )
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertEqual(err, message)
                self.assertFalse((data / "bearing.db").exists())

    def test_with_prs_no_gh(self):
        from bearing.cli import main

        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        repo = self.out / "repo"
        data = Path(self.tmp.name) / "data-with-prs"
        code, out, err, calls = self.run_main(
            main,
            [
                "ingest",
                str(repo),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(data),
            ],
            self.gh_answer(),
        )
        self.assertEqual(code, 0, err)
        self.assertEqual(out, GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(calls, [])
