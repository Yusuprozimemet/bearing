"""Renames in git's numstat, the last name of each file, and the report that follows renames."""

import tempfile
import unittest
from contextlib import closing
from unittest import mock


class RenamesTest(unittest.TestCase):
    def test_parse_renames(self):
        from bearing.direction.changes import commit_changes, parse_renames
        from bearing.snapshot.tree import SnapshotError

        raw = (
            b"3\t1\tapp/a.py\x00-\t-\tlogo.png\x000\t0\t\x00scripts/helpers.py\x00"
            b"scripts/tools.py\x001\t0\t\x00docs/old.md\x00docs/new.md\x00"
        )
        self.assertEqual(
            parse_renames(raw),
            [
                ("scripts/helpers.py", "scripts/tools.py"),
                ("docs/old.md", "docs/new.md"),
            ],
        )
        self.assertEqual(parse_renames(b"3\t1\tapp/a.py\x00"), [])
        self.assertEqual(parse_renames(b""), [])
        with self.assertRaises(SnapshotError):
            commit_changes("no-such-repo", "HEAD")

    def test_chain(self):
        from bearing.direction.coupling import latest_names

        commits = [
            (["a.py"], []),
            (["b.py", "x.py"], [("a.py", "b.py")]),
            (["c.py"], [("b.py", "c.py")]),
        ]
        self.assertEqual(latest_names(commits), [["c.py"], ["c.py", "x.py"], ["c.py"]])

    def test_reused_path(self):
        from bearing.direction.coupling import latest_names

        commits = [
            (["a.py", "x.py"], []),
            (["b.py"], [("a.py", "b.py")]),
            (["a.py", "x.py"], []),
        ]
        self.assertEqual(
            latest_names(commits), [["b.py", "x.py"], ["b.py"], ["a.py", "x.py"]]
        )

    def test_report_direct_rename(self):
        from bearing.direction.report import direction_report
        from bearing.store.db import open_store

        commits = [
            ("r0", 0, 0, "direct", None, "2026-01-04"),
            ("m1", 1, 2, "merge", 1, "2026-01-05"),
            ("d2", 2, 1, "direct", None, "2026-01-06"),
            ("m3", 3, 2, "merge", 2, "2026-01-07"),
        ]
        answers = {
            "m1": ([("old/m.py", 3, 0), ("x/y.py", 1, 0)], []),
            "d2": ([("new/m.py", 0, 0)], [("old/m.py", "new/m.py")]),
            "m3": ([("new/m.py", 2, 0), ("x/y.py", 1, 0)], []),
        }
        calls = []

        def fake(repo, sha):
            calls.append(sha)
            return answers[sha]

        with tempfile.TemporaryDirectory() as tmp, closing(open_store(tmp)) as conn:
            conn.executemany(
                "INSERT INTO commits (sha, position, parent_count, subject, committed_at,"
                " kind, pr_number) VALUES (?, ?, ?, '', ?, ?, ?)",
                [
                    (sha, position, parents, f"{date}T12:00:00+00:00", kind, pr)
                    for sha, position, parents, kind, pr, date in commits
                ],
            )
            conn.executemany(
                "INSERT INTO prs (number, title, body, head_ref, base_ref)"
                " VALUES (?, '', '', ?, 'main')",
                [(1, "x/one"), (2, "x/two")],
            )
            conn.commit()
            areas = [("old", ("old/",)), ("new", ("new/",)), ("x", ("x/",))]
            with mock.patch("bearing.direction.report.commit_changes", fake):
                lines = direction_report(
                    "no-such-repo", conn, areas, 2, [("outside-area", ())]
                )
        self.assertEqual(
            lines,
            [
                "## Churn",
                "",
                "| Week | Area | Added | Deleted |",
                "|---|---|---|---|",
                "| 2026-W02 | new | 2 | 0 |",
                "| 2026-W02 | old | 3 | 0 |",
                "| 2026-W02 | x | 2 | 0 |",
                "",
                "## Coupling",
                "",
                "| File | File | PRs | Hidden dependency |",
                "|---|---|---|---|",
                "| new/m.py | x/y.py | #1, #2 | new, x |",
                "",
                "## Said vs done",
                "",
                "- #1 outside-area: area x | old/m.py",
                "- #2 outside-area: area x | new/m.py",
            ],
        )
        self.assertEqual(calls, ["m1", "d2", "m3"])
