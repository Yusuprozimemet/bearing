"""Error lines and the --stats line are UTF-8 with the console's code page set to cp1252, and argparse is left alone."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import bearing.cli

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
# A cp1252 console: the streams start in cp1252, so the test shows what reconfigure changed.
CP1252_ENV = {k: v for k, v in ENV.items() if k != "PYTHONUTF8"}
CP1252_ENV["PYTHONIOENCODING"] = "cp1252"


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "bearing", *args],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=CP1252_ENV,
    )


def one_line(stderr, start):
    text = stderr.replace(b"\r\n", b"\n").decode("utf-8")
    assert text.count("\n") == 1 and text.endswith("\n"), text
    assert text.startswith(start), text
    return text


class StderrTest(unittest.TestCase):
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

    def test_error_lines_are_utf8(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        name = str(Path(self.tmp.name) / "łódź-café")
        ingest_data = Path(self.tmp.name) / "ingest-data"
        cases = [
            (["changelog", "--data", name], "no store at"),
            (["timeline", ".", "--data", name], "no store at"),
            (
                [
                    "direction",
                    ".",
                    "--data",
                    name,
                    "--config",
                    "tests/fixtures/bearing.toml",
                ],
                "no store at",
            ),
            (
                [
                    "page",
                    ".",
                    "--data",
                    name,
                    "--config",
                    "tests/fixtures/bearing.toml",
                    "--out",
                    name + ".html",
                ],
                "no store at",
            ),
            (
                [
                    "ingest",
                    str(self.repo()),
                    "--prs",
                    name + ".json",
                    "--data",
                    str(ingest_data),
                ],
                "cannot read",
            ),
        ]
        for args, phrase in cases:
            with self.subTest(command=args[0], phrase=phrase):
                result = run(*args)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(result.stdout, b"")
                text = one_line(result.stderr, "bearing: ")
                self.assertIn(name, text)
                self.assertIn(phrase, text)

    def test_stats_stream_is_utf8(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = Path(self.tmp.name) / "stats-stream"
        ingest = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "ingest",
                str(self.repo()),
                "--prs",
                str(self.out / "prs.json"),
                "--data",
                str(data),
            ],
            check=False,
            cwd=REPO,
            capture_output=True,
            env=ENV,
        )
        self.assertEqual(ingest.returncode, 0, ingest.stderr)
        raw = io.BytesIO()
        err = io.TextIOWrapper(raw, encoding="cp1252")
        with mock.patch("sys.stderr", err), mock.patch("sys.stdout", io.StringIO()):
            code = bearing.cli.main(
                ["timeline", str(self.repo()), "--data", str(data), "--stats"]
            )
        self.assertEqual(code, 0)
        self.assertEqual(err.encoding, "utf-8")
        err.flush()
        self.assertEqual(
            raw.getvalue().replace(b"\r\n", b"\n"),
            b"blobs parsed 28  cache hits 0\n",
        )

    def test_argparse_left_alone(self):
        result = run("ingest", ".", "café")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, b"")
        stderr = result.stderr.replace(b"\r\n", b"\n")
        last = stderr.rstrip(b"\n").split(b"\n")[-1]
        self.assertEqual(last, b"bearing: error: unrecognized arguments: caf\xe9")

    def test_surrogate_is_escaped(self):
        name = str(Path(self.tmp.name) / "a\udc80b")
        result = run("changelog", "--data", name)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr.replace(b"\r\n", b"\n").count(b"\n"), 1)
        self.assertTrue(result.stderr.startswith(b"bearing: no store at"))
        self.assertIn(b"\\udc80", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)
