"""The warning bearing ingest writes at exactly 1000 PR records, from a --prs file and from gh, and its silence one record either side."""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
REAL_RUN = subprocess.run
WARNING = (
    "bearing: warning: 1000 PR records is gh's limit; a history with more is cut\n"
)


class IngestLimitTest(unittest.TestCase):
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

    def records(self, count):
        # The fixture's ten records, then padding records with numbers and branch names of their own.
        fixture = json.loads((self.out / "prs.json").read_text(encoding="utf-8"))
        padding = [
            {
                **fixture[0],
                "number": 5000 + i,
                "mergeCommit": None,
                "title": f"pad-{i}",
                "headRefName": f"pad-{i}",
            }
            for i in range(count - 10)
        ]
        return fixture + padding

    def ingest_file(self, count):
        prs = Path(self.tmp.name) / f"prs-{count}.json"
        prs.write_bytes(json.dumps(self.records(count)).encode("utf-8"))
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "ingest",
                str(self.out / "repo"),
                "--prs",
                str(prs),
                "--data",
                str(Path(self.tmp.name) / f"data-{count}"),
            ],
            check=False,
            cwd=REPO,
            capture_output=True,
        )
        return (
            result.returncode,
            result.stdout.decode("utf-8").replace("\r\n", "\n"),
            result.stderr.decode("utf-8").replace("\r\n", "\n"),
        )

    def test_warns_at_1000(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        code, out, err = self.ingest_file(1000)
        self.assertEqual(code, 0, err)
        self.assertEqual(err, WARNING)
        lines = out.splitlines()
        self.assertEqual(len(lines), 993)
        self.assertEqual(
            lines[0],
            "merges 10  matched 9  unmatched merges 1  unmatched PRs 991  direct 2",
        )
        self.assertFalse(any("warning" in line for line in lines))

    def test_silent_at_999_and_1001(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        for count, unmatched in ((999, 990), (1001, 992)):
            with self.subTest(count=count):
                code, out, err = self.ingest_file(count)
                self.assertEqual(code, 0, err)
                self.assertEqual(err, "")
                self.assertEqual(
                    out.splitlines()[0],
                    f"merges 10  matched 9  unmatched merges 1  unmatched PRs {unmatched}  direct 2",
                )

    def test_warns_from_gh(self):
        from bearing.cli import main

        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        answer = subprocess.CompletedProcess(
            ["gh"], 0, stdout=json.dumps(self.records(1000)), stderr=""
        )

        def run(*args, **kwargs):
            if args and args[0][0] == "gh":
                return answer
            return REAL_RUN(*args, **kwargs)

        out, err = io.StringIO(), io.StringIO()
        with (
            patch("subprocess.run", run),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
        ):
            code = main(
                [
                    "ingest",
                    str(self.out / "repo"),
                    "--data",
                    str(Path(self.tmp.name) / "data-gh"),
                ]
            )
        self.assertEqual(code, 0)
        self.assertEqual(err.getvalue(), WARNING)
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 993)
        self.assertEqual(
            lines[0],
            "merges 10  matched 9  unmatched merges 1  unmatched PRs 991  direct 2",
        )
        self.assertFalse(any("warning" in line for line in lines))
