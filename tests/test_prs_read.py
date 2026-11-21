"""The --prs file that cannot be read: what bearing ingest prints for each way a file can fail to load, and that it opens no store."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class PrsReadTest(unittest.TestCase):
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

    def run_ingest(self, name, file):
        # Each case has its own data directory, which must not exist yet.
        data = Path(self.tmp.name) / f"data-{name}"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bearing",
                "ingest",
                str(self.out / "repo"),
                "--prs",
                str(file),
                "--data",
                str(data),
            ],
            cwd=REPO,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertFalse((data / "bearing.db").exists())
        return result.stderr.decode("utf-8").replace("\r\n", "\n")

    def test_not_json(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        file = Path(self.tmp.name) / "not-json.json"
        file.write_bytes(b"{bad")
        err = self.run_ingest("not-json", file)
        self.assertEqual(
            err,
            f"bearing: cannot read {file}: not JSON: Expecting property name enclosed in double quotes (line 1, column 2)\n",
        )

    def test_not_utf8(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        file = Path(self.tmp.name) / "not-utf8.json"
        file.write_bytes(b"\xff\xfe\x5b")
        err = self.run_ingest("not-utf8", file)
        self.assertEqual(err, f"bearing: cannot read {file}: not UTF-8\n")

    def test_directory(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        file = Path(self.tmp.name) / "a-directory"
        file.mkdir()
        err = self.run_ingest("a-directory", file)
        self.assertTrue(err.startswith(f"bearing: cannot read {file}: "))
        self.assertTrue(err.endswith("\n"))
        self.assertEqual(err.count("\n"), 1)
        self.assertNotIn("[Errno", err)

    def test_bom(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        file = Path(self.tmp.name) / "bom.json"
        file.write_bytes(b"\xef\xbb\xbf" + (self.out / "prs.json").read_bytes())
        err = self.run_ingest("bom", file)
        self.assertEqual(
            err,
            f"bearing: cannot read {file}: not JSON: Unexpected UTF-8 BOM (decode using utf-8-sig) (line 1, column 1)\n",
        )

    def test_missing(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        file = Path(self.tmp.name) / "missing.json"
        err = self.run_ingest("missing", file)
        self.assertEqual(
            err, f"bearing: cannot read {file}: No such file or directory\n"
        )
