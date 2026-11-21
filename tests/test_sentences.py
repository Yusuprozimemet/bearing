"""What a PR's changelog paragraph keeps: the first two sentences, and a short paragraph whole."""

import unittest


class SentenceTest(unittest.TestCase):
    def test_three_sentences_give_two(self):
        from bearing.ingest.text import what_i_built

        cases = [
            ("## What I built\n\nOne. Two. Three.\n", "One. Two."),
            ("## What I built\n\nOne.  Two.\tThree.\n", "One.  Two."),
            (
                "## What I built\n\nFirst line. Second\nline.  Third one.\n",
                "First line. Second\nline.",
            ),
            ("## What I built\n\nOne.\nTwo.\nThree.\n", "One.\nTwo."),
            ("One. Two. Three. Four.\n", "One. Two."),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                self.assertEqual(what_i_built(body), expected)

    def test_bang_and_question_end(self):
        from bearing.ingest.text import what_i_built

        cases = [
            ("## What I built\n\nDone! Really? Yes.\n", "Done! Really?"),
            ("## What I built\n\nWhy? Because. More.\n", "Why? Because."),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                self.assertEqual(what_i_built(body), expected)

    def test_short_unchanged(self):
        from bearing.ingest.text import what_i_built

        cases = [
            ("## What I built\n\nOne. Two.\n", "One. Two."),
            ("## What I built\n\nOne sentence.\n", "One sentence."),
            ("## What I built\n\nNo end mark\n", "No end mark"),
            ("## What I built\n\nIs it? Yes!\n", "Is it? Yes!"),
            (
                "## What I built\n\napp/b.py stops importing app.a. Version 1.2 is out.\n",
                "app/b.py stops importing app.a. Version 1.2 is out.",
            ),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                self.assertEqual(what_i_built(body), expected)
