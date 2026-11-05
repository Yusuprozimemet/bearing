"""The kit's round-2 flags: each flag of the direction report, with the maintainer's mark."""

import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1] / "docs" / "kit"
FLAGS = KIT / "flags.md"
REPORT = KIT / "direction.md"


class KitFlagsTest(unittest.TestCase):
    def test_marks(self):
        # bytes, so CRLF checkouts read the same lines as LF ones
        flags_bytes = FLAGS.read_bytes().replace(b"\r\n", b"\n")
        try:
            flags_text = flags_bytes.decode("ascii")
        except UnicodeDecodeError:
            self.fail("docs/kit/flags.md is not ASCII")
        report = REPORT.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
        lines = flags_text.splitlines()

        flagged = [line for line in lines if line.startswith("- #")]
        cut = [line.rpartition(" -- ")[0] for line in flagged]
        marks = [line.rpartition(" -- ")[2] for line in flagged]
        report_flags = [line for line in report.splitlines() if line.startswith("- #")]
        self.assertEqual(cut, report_flags)
        self.assertEqual(len(report_flags), 26)

        for line, mark in zip(flagged, marks):
            with self.subTest(flag=line[:40]):
                ok = mark == "real" or (
                    mark.startswith("rule: ") and len(mark) > len("rule: ")
                )
                self.assertTrue(ok, f"mark {mark!r} is neither real nor rule: <what>")

        counts = [line for line in lines if line.startswith("Marks: ")]
        self.assertEqual(len(counts), 1)
        match = re.fullmatch(r"Marks: real (\d+), rule (\d+)", counts[0])
        self.assertIsNotNone(match, counts[0])
        self.assertEqual(int(match.group(1)), marks.count("real"))
        self.assertEqual(
            int(match.group(2)), sum(mark.startswith("rule: ") for mark in marks)
        )

        for line in lines:
            if not line.startswith("- #"):
                self.assertFalse(line.endswith(" -- real"), line)

        self.assertGreaterEqual(marks.count("real") * 2, len(flagged))
