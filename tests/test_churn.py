"""Churn by ISO week and area: the year boundaries, the sums, and the rows that come out sorted."""

import unittest


class ChurnTest(unittest.TestCase):
    def test_weeks_and_areas(self):
        from bearing.direction.churn import churn

        commits = [
            ("2025-12-29T10:00:00+00:00", [("app/a.py", 2, 1), ("docs/x.md", 1, 0)]),
            ("2026-01-02T23:00:00+00:00", [("app/b.py", 3, 0)]),
            ("2027-01-01T00:00:00+00:00", [("z.txt", 0, 4)]),
            ("2026-01-05T08:00:00+00:00", [("docs/y.md", 0, 0)]),
        ]
        areas = [("app", ("app/",)), ("docs", ("docs/",))]
        self.assertEqual(
            churn(commits, areas),
            [
                ("2026-W01", "app", 5, 1),
                ("2026-W01", "docs", 1, 0),
                ("2026-W02", "docs", 0, 0),
                ("2026-W53", "other", 0, 4),
            ],
        )
