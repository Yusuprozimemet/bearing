"""The command line, run as a module and as the installed console script."""

import contextlib
import importlib.metadata
import io
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class CliTest(unittest.TestCase):
    def test_version_module(self):
        result = subprocess.run(
            [sys.executable, "-m", "bearing", "--version"],
            check=False,
            cwd=REPO,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.replace(b"\r\n", b"\n"), b"bearing 0.1.0\n")

    def test_console_script(self):
        eps = importlib.metadata.entry_points(group="console_scripts", name="bearing")
        self.assertEqual(len(eps), 1)
        ep = next(iter(eps))
        self.assertEqual(ep.value, "bearing.cli:main")
        # The import happens here, inside the test: on CI's base worktree the base's bearing
        # has no __version__, and the ImportError fails this test, not the collection.
        main = ep.load()
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                code = main(["--version"])
        except SystemExit as exc:
            code = exc.code
        self.assertIn(code, (0, None))
        self.assertEqual(out.getvalue(), "bearing 0.1.0\n")
