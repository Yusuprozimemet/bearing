"""The kit's round-2 direction report: its line count and its first flagged line."""

import unittest
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1] / "docs" / "kit" / "direction.md"


class KitReportTest(unittest.TestCase):
    def test_round_2(self):
        # bytes, so CRLF checkouts read the same lines as LF ones
        data = REPORT.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
        lines = data.splitlines()
        self.assertEqual(len(lines), 181)
        flagged = [line for line in lines if line.startswith("- #")]
        self.assertEqual(len(flagged), 26)
        self.assertEqual(
            flagged[0],
            "- #8 outside-area: area dashboard | scripts/test_token_usage.py, scripts/token-usage.py",
        )
