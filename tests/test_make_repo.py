"""The fixture history that make_repo.py builds, asked of git and of prs.json."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"

# First-parent line of main, newest first.
SUBJECTS = [
    "Merge pull request #11 from acme/tooling/ci",
    "Merge pull request #10 from acme/release",
    "Merge pull request #9 from acme/day-03/track-b-break-cycle",
    "Merge pull request #8 from acme/day-03/track-a-rename",
    "Grow the core module (#6)",
    "Merge pull request #5 from acme/docs/typo-fix",
    "Fix README typo",
    "Merge pull request #3 from acme/day-02/track-a-cycle",
    "Merge pull request #4 from acme/docs/guide",
    "Merge pull request #2 from acme/tooling/scripts",
    "Merge pull request #1 from acme/day-01/track-a-core",
    "Initial commit",
]
# The root has no parents; steps 6 and 8 have one; the nine merges have two.
PARENTS = [2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 0]
DAYS = ["30", "28", "26", "23", "21", "19", "16", "14", "12", "09", "07", "05"]
SIDE_SUBJECT = "Merge pull request #7 from acme/docs/notes"

# number: (headRefName, baseRefName, day of mergedAt); #6 is the squash commit.
RECORDS = {
    1: ("day-01/track-a-core", "main", "07"),
    2: ("tooling/scripts", "main", "09"),
    3: ("day-02/track-a-cycle", "main", "14"),
    4: ("docs/guide", "main", "12"),
    5: ("docs/typo-fix", "main", "19"),
    6: ("day-02/track-b-grow", "main", "21"),
    7: ("docs/notes", "release", "27"),
    8: ("day-03/track-a-rename", "main", "23"),
    9: ("day-03/track-b-break-cycle", "main", "26"),
    10: ("release", "main", "28"),
}
SQUASH = {6: "Grow the core module (#6)"}
RECORD_KEYS = {
    "baseRefName",
    "body",
    "headRefName",
    "mergeCommit",
    "mergedAt",
    "number",
    "title",
}


class HistoryTest(unittest.TestCase):
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

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.out / "repo"), *args],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_first_parent_line(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        subjects = self.git("log", "--first-parent", "--format=%s", "main").splitlines()
        self.assertEqual(subjects, SUBJECTS)
        parents = self.git("log", "--first-parent", "--format=%P", "main").splitlines()
        self.assertEqual([len(line.split()) for line in parents], PARENTS)
        dates = self.git("log", "--first-parent", "--format=%aI", "main").splitlines()
        self.assertEqual(dates, [f"2026-01-{d}T12:00:00Z" for d in DAYS])
        everything = self.git("log", "--format=%H%x09%s", "main").splitlines()
        side = [
            line.split("\t")[0] for line in everything if line.endswith(SIDE_SUBJECT)
        ]
        self.assertEqual(len(side), 1)
        first_parent = self.git("log", "--first-parent", "--format=%H", "main").split()
        self.assertNotIn(side[0], first_parent)

    def test_pr_records(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        raw = (self.out / "prs.json").read_bytes()
        records = json.loads(raw)
        self.assertEqual([r["number"] for r in records], list(range(1, 11)))
        shas = {}
        for line in self.git("log", "--format=%H%x09%s", "main").splitlines():
            sha, subject = line.split("\t", 1)
            shas[subject] = sha
        for r in records:
            head, base, day = RECORDS[r["number"]]
            subject = SQUASH.get(
                r["number"], f"Merge pull request #{r['number']} from acme/{head}"
            )
            self.assertEqual(set(r), RECORD_KEYS)
            self.assertEqual(r["headRefName"], head)
            self.assertEqual(r["baseRefName"], base)
            self.assertEqual(r["mergedAt"], f"2026-01-{day}T12:00:00Z")
            self.assertEqual(r["mergeCommit"]["oid"], shas[subject])
        first_parent = self.git("log", "--first-parent", "--format=%H", "main").split()
        self.assertNotIn(shas[SIDE_SUBJECT], first_parent)
        self.assertIn(shas[SQUASH[6]], first_parent)
        self.assertEqual(
            raw,
            (json.dumps(json.loads(raw), sort_keys=True, indent=2) + "\n").encode(
                "utf-8"
            ),
        )
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
