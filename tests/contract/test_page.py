"""The page's contract: the golden file is the page-v1 data `bearing page` writes for the fixture after `bearing ingest`."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "page-v1.json"
TOML = REPO / "tests" / "fixtures" / "bearing.toml"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
OPEN = '<script id="bearing-data" type="application/json">'


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=ENV,
    )


def bearing(*args):
    return run("-m", "bearing", *args)


class PageContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.result = run(BUILDER, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_golden(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = Path(self.tmp.name) / "data"
        repo = self.out / "repo"
        ingest = bearing("ingest", repo, "--prs", self.out / "prs.json", "--data", data)
        self.assertEqual(ingest.returncode, 0, ingest.stderr)
        page = Path(self.tmp.name) / "page.html"
        result = bearing("page", repo, "--data", data, "--config", TOML, "--out", page)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, b"")
        html = page.read_bytes().decode("utf-8")
        text = html.split(OPEN, 1)[1].split("</script>", 1)[0]
        self.assertEqual(
            text, GOLDEN.read_bytes().decode("utf-8").replace("\r\n", "\n")
        )
