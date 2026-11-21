"""The shape of a --prs file: what bearing ingest refuses before it opens the store, and the line it prints for each refusal."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class PrsRecordsTest(unittest.TestCase):
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

    def fixture(self):
        return json.loads((self.out / "prs.json").read_text(encoding="utf-8"))

    def run_ingest(self, name, payload):
        # Each case has its own file and its own data directory, which must not exist yet.
        file = Path(self.tmp.name) / f"{name}.json"
        file.write_bytes(json.dumps(payload).encode("utf-8"))
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
        return (
            result.returncode,
            result.stdout.decode("utf-8").replace("\r\n", "\n"),
            result.stderr.decode("utf-8").replace("\r\n", "\n"),
            data,
        )

    def assert_refused(self, name, payload, message):
        code, out, err, data = self.run_ingest(name, payload)
        file = Path(self.tmp.name) / f"{name}.json"
        self.assertEqual(code, 1, err)
        self.assertEqual(out, "")
        self.assertEqual(err, f"bearing: {file}: {message}\n")
        self.assertFalse((data / "bearing.db").exists())

    def test_not_a_list(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assert_refused("not-a-list", {}, "not a list of PR records")

    def test_not_an_object(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assert_refused("not-an-object", [1], "record 1 is not an object")

    def test_no_title(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        records = self.fixture()
        del records[2]["title"]
        self.assert_refused("no-title", records, "record 3 has no title")

    def test_number_type(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        records = self.fixture()
        records[2]["number"] = "3"
        self.assert_refused(
            "number-str", records, "record 3's number is not an integer"
        )
        records = self.fixture()
        records[2]["number"] = True
        self.assert_refused(
            "number-true", records, "record 3's number is not an integer"
        )

    def test_merge_commit_type(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        records = self.fixture()
        records[2]["mergeCommit"] = "x"
        self.assert_refused(
            "merge-commit", records, "record 3's mergeCommit is not an object"
        )

    def test_repeats(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        records = self.fixture()
        records[2]["number"] = 2
        self.assert_refused("repeats", records, "record 3 repeats number 2")

    def test_before_warning(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        # The fixture's ten records, then padding records to 1000 as test_ingest_limit does.
        fixture = self.fixture()
        padding = [
            {
                **fixture[0],
                "number": 5000 + i,
                "mergeCommit": None,
                "title": f"pad-{i}",
                "headRefName": f"pad-{i}",
            }
            for i in range(1000 - 10)
        ]
        records = fixture + padding
        del records[2]["title"]
        code, out, err, data = self.run_ingest("padded", records)
        file = Path(self.tmp.name) / "padded.json"
        self.assertEqual(code, 1, err)
        self.assertEqual(out, "")
        self.assertEqual(err, f"bearing: {file}: record 3 has no title\n")
        self.assertNotIn("warning", err)
        self.assertFalse((data / "bearing.db").exists())

    def test_messages(self):
        from bearing.ingest.mapping import check_records

        record = {"number": 1, "title": "t", "headRefName": "h", "baseRefName": "main"}
        no_head = {key: value for key, value in record.items() if key != "headRefName"}
        raising = [
            ({"a": 1}, "p.json: not a list of PR records"),
            ([[]], "p.json: record 1 is not an object"),
            ([{}], "p.json: record 1 has no number"),
            (
                [{**record, "number": 1.0}],
                "p.json: record 1's number is not an integer",
            ),
            (
                [{**record, "number": "x", "title": 5}],
                "p.json: record 1's number is not an integer",
            ),
            ([no_head], "p.json: record 1 has no headRefName"),
            (
                [{**record, "baseRefName": None}],
                "p.json: record 1's baseRefName is not a string",
            ),
            (
                [{**record, "body": 5, "mergedAt": 5}],
                "p.json: record 1's body is not a string",
            ),
            (
                [{**record, "mergedAt": 0}],
                "p.json: record 1's mergedAt is not a string",
            ),
            (
                [{**record, "mergeCommit": {"oid": 7}}],
                "p.json: record 1's mergeCommit oid is not a string",
            ),
            ([record, 3], "p.json: record 2 is not an object"),
            (
                [record, {**record, "number": 2}, record],
                "p.json: record 3 repeats number 1",
            ),
        ]
        for records, expected in raising:
            with self.assertRaises(ValueError) as cm:
                check_records("p.json", records)
            self.assertEqual(str(cm.exception), expected)
        passing = [
            [],
            [record],
            [{**record, "body": None, "mergedAt": None, "mergeCommit": None}],
            [{**record, "mergeCommit": {}}],
            [{**record, "mergeCommit": {"oid": None}}],
        ]
        for records in passing:
            self.assertIsNone(check_records("p.json", records))
