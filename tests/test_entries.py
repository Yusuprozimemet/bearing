"""Reading the changelog's entries from the stored fixture, and formatting them: the golden file and the edge cases."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"


def store(repo, prs, data):
    # One ingest of the history at repo, with the records from prs, into the store under data.
    from bearing.ingest.history import read_first_parent
    from bearing.ingest.mapping import load_prs, map_history
    from bearing.store.db import open_store, save

    commits = read_first_parent(repo)
    records = load_prs(prs)
    conn = open_store(data)
    save(conn, commits, records, map_history(commits, records))
    return conn


class EntriesTest(unittest.TestCase):
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

    def test_fixture_entries(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.changelog import read_entries

        conn = store(
            self.out / "repo", self.out / "prs.json", Path(self.tmp.name) / "data"
        )
        entries = read_entries(conn)
        conn.close()
        self.assertEqual(len(entries), 10)
        self.assertEqual([e.number for e in entries], [1, 2, 4, 3, 5, 6, 8, 9, 10, 11])
        self.assertEqual(
            [e.area for e in entries],
            [
                "day-01",
                "tooling",
                "docs",
                "day-02",
                "docs",
                "day-02",
                "day-03",
                "day-03",
                "other",
                "tooling",
            ],
        )
        self.assertEqual(entries[0].date, "2026-01-07")
        self.assertEqual(entries[-1].date, "2026-01-30")
        self.assertEqual(entries[2].paragraph, "")
        self.assertEqual(
            entries[-1].title, "Merge pull request #11 from acme/tooling/ci"
        )
        self.assertEqual(entries[-1].paragraph, "")

    def test_date_is_the_commit(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.changelog import read_entries

        # A copy of prs.json whose #3 record says it merged in February; the commit still says January.
        records = json.loads((self.out / "prs.json").read_text(encoding="utf-8"))
        for record in records:
            if record["number"] == 3:
                record["mergedAt"] = "2026-02-20T12:00:00Z"
        late = Path(self.tmp.name) / "prs-late.json"
        late.write_bytes(json.dumps(records, ensure_ascii=False).encode("utf-8"))
        changed = json.loads(late.read_text(encoding="utf-8"))
        self.assertEqual(
            [r["mergedAt"] for r in changed if r["number"] == 3],
            ["2026-02-20T12:00:00Z"],
        )

        conn = store(self.out / "repo", late, Path(self.tmp.name) / "data-late")
        entries = read_entries(conn)
        conn.close()
        self.assertEqual([e.date for e in entries if e.number == 3], ["2026-01-14"])


class ChangelogFormatTest(unittest.TestCase):
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

    def test_golden_and_edges(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.ingest.changelog import Entry, format_changelog, read_entries

        conn = store(
            self.out / "repo", self.out / "prs.json", Path(self.tmp.name) / "data"
        )
        golden = "".join(line + "\n" for line in format_changelog(read_entries(conn)))
        conn.close()
        self.assertEqual(
            golden.encode("utf-8"),
            (REPO / "tests" / "fixtures" / "expected" / "changelog.md").read_bytes(),
        )

        cases = [
            (
                "no entries",
                format_changelog([]),
                ["# Changelog"],
            ),
            (
                "no number",
                format_changelog(
                    [Entry(None, "Merge branch 'x'", "2026-02-01", "other", "")]
                ),
                [
                    "# Changelog",
                    "",
                    "## other",
                    "",
                    "- #- Merge branch 'x' (2026-02-01)",
                ],
            ),
            (
                "given order kept",
                format_changelog(
                    [
                        Entry(5, "five", "2026-02-03", "docs", ""),
                        Entry(3, "three", "2026-02-02", "docs", ""),
                    ]
                ),
                [
                    "# Changelog",
                    "",
                    "## docs",
                    "",
                    "- #5 five (2026-02-03)",
                    "- #3 three (2026-02-02)",
                ],
            ),
        ]
        for name, got, expected in cases:
            with self.subTest(case=name):
                self.assertEqual(got, expected)
