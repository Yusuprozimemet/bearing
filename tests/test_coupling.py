"""Coupling by pull request: the pairs of files, the PRs they share, and the threshold."""

import unittest


class CouplingTest(unittest.TestCase):
    def test_pairs(self):
        from bearing.direction.coupling import coupling

        prs = [
            (1, ["x/a", "y/b", "x/c"]),
            (3, ["x/a", "y/b"]),
            (2, ["x/a", "x/c"]),
            (4, ["y/b", "x/a"]),
            (4, ["x/a", "y/b"]),
        ]
        areas = [("x", ("x/",)), ("y", ("y/",))]
        self.assertEqual(
            coupling(prs, areas, 2),
            [
                ("x/a", "x/c", [1, 2], "x", "x"),
                ("x/a", "y/b", [1, 3, 4], "x", "y"),
            ],
        )
        self.assertEqual(coupling(prs, areas, 4), [])
