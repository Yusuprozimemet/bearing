"""Said versus done: the contract-impact claim in a pull request body, and the flags against its files."""

import unittest


class SaidVsDoneTest(unittest.TestCase):
    def test_claim(self):
        from bearing.direction.said_vs_done import says_no_contract_impact

        claims = [
            "## Contract impact\n\nNone\n",
            "## Contract impact\r\n\r\nNone. The format is unchanged.\r\n",
            "### contract impact\n\n  none\n",
            "Contract impact: None\n",
            "contract impact: none, only tests\n",
            "## What I built\n\nX.\n\n## Contract impact\n\nNone\n",
        ]
        no_claims = [
            "## Contract impact\n\nAdds snapshot-v2.\n",
            "## Contract impact\n\nNonetheless the format changes.\n",
            "## Contract impact\n\n## Next\n\nNone\n",
            "It says Contract impact: none in passing.\n",
            "Contract impact: unknown\n",
            "",
            None,
        ]
        for body in claims:
            with self.subTest(body=body):
                self.assertTrue(says_no_contract_impact(body))
        for body in no_claims:
            with self.subTest(body=body):
                self.assertFalse(says_no_contract_impact(body))

    def test_flags(self):
        from bearing.direction.said_vs_done import said_vs_done

        areas = [
            ("docs", ("docs/", "README.md")),
            ("app", ("app/",)),
            ("api", ("app/api/",)),
        ]
        rules = [("contract-impact", ("tests/contract/",)), ("outside-area", ())]
        prs = [
            (
                7,
                "docs/fix",
                "## Contract impact\n\nNone\n",
                ["tests/contract/t.py", "app/x.py", "README.md", "docs/a.md"],
            ),
            (2, "api/handler", None, ["app/api/h.py"]),
            (
                3,
                "day-04/track-a",
                "Contract impact: none\n",
                ["app/y.py", "tests/contract/u.py"],
            ),
            (4, "release", "Contract impact: none\n", ["app/z.py"]),
            (
                5,
                "app/thing",
                "## Contract impact\n\nAdds v2.\n",
                ["tests/contract/v.py"],
            ),
            (6, "tooling/ci", None, ["tests/contract/w.py"]),
        ]
        self.assertEqual(
            said_vs_done(prs, areas, rules),
            [
                (7, "contract-impact", "no contract impact", ["tests/contract/t.py"]),
                (7, "outside-area", "area docs", ["app/x.py", "tests/contract/t.py"]),
                (3, "contract-impact", "no contract impact", ["tests/contract/u.py"]),
                (5, "outside-area", "area app", ["tests/contract/v.py"]),
            ],
        )
        self.assertEqual(said_vs_done(prs, areas, []), [])
