"""Mapping the fixture's history onto its PRs: the report, the subject fallback, and UTF-8 input."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


class FixtureCase(unittest.TestCase):
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

    def copied_records(self, name, change):
        # change(records) edits the copy in place; the file is written as UTF-8 bytes.
        from bearing.ingest.mapping import load_prs

        records = copy.deepcopy(load_prs(self.out / "prs.json"))
        change(records)
        path = Path(self.tmp.name) / name
        path.write_bytes(json.dumps(records).encode("utf-8"))
        return load_prs(path)

    def by_number(self, records, number):
        return next(record for record in records if record["number"] == number)


class MappingTest(FixtureCase):
    def test_fixture_report(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.history import read_first_parent
        from bearing.ingest.mapping import format_report, load_prs, map_history

        result = map_history(
            read_first_parent(self.out / "repo"), load_prs(self.out / "prs.json")
        )
        self.assertEqual(
            format_report(result),
            [
                "merges 10  matched 9  unmatched merges 1  unmatched PRs 1  direct 2",
                "unmatched merge 8c1b9f1 Merge pull request #11 from acme/tooling/ci",
                "unmatched PR #7 e21c62d docs/notes",
            ],
        )


class FallbackTest(FixtureCase):
    def test_absent_and_null(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.history import read_first_parent
        from bearing.ingest.mapping import format_report, map_history

        def change(records):
            del self.by_number(records, 1)["mergeCommit"]
            self.by_number(records, 6)["mergeCommit"] = None

        records = self.copied_records("absent_and_null.json", change)
        result = map_history(read_first_parent(self.out / "repo"), records)
        self.assertEqual(
            format_report(result),
            [
                "merges 9  matched 8  unmatched merges 1  unmatched PRs 2  direct 3",
                "unmatched merge 8c1b9f1 Merge pull request #11 from acme/tooling/ci",
                "unmatched PR #6 - day-02/track-b-grow",
                "unmatched PR #7 e21c62d docs/notes",
            ],
        )

    def test_oid_off_the_line(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.history import read_first_parent
        from bearing.ingest.mapping import format_report, map_history

        def change(records):
            self.by_number(records, 1)["mergeCommit"] = {"oid": "0" * 40}

        records = self.copied_records("off_the_line.json", change)
        result = map_history(read_first_parent(self.out / "repo"), records)
        self.assertEqual(
            format_report(result),
            [
                "merges 10  matched 8  unmatched merges 2  unmatched PRs 2  direct 2",
                "unmatched merge 62c4b2f Merge pull request #1 from acme/day-01/track-a-core",
                "unmatched merge 8c1b9f1 Merge pull request #11 from acme/tooling/ci",
                "unmatched PR #1 0000000 day-01/track-a-core",
                "unmatched PR #7 e21c62d docs/notes",
            ],
        )


class LoadPrsTest(unittest.TestCase):
    def test_utf8(self):
        from bearing.ingest.mapping import load_prs

        data = '[{"number": 1, "title": "Café → bar", "mergeCommit": null}]'.encode()
        self.assertNotIn(b"\\u", data)
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            path = Path(tmp) / "prs.json"
            path.write_bytes(data)
            self.assertEqual(load_prs(path)[0]["title"], "Café → bar")
