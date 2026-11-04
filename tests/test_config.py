"""bearing.toml: the areas in file order, the coupling threshold, and the messages for a bad file."""

import tempfile
import unittest
from pathlib import Path


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text):
        # bytes, so the file has LF endings on every platform
        path = self.dir / "bearing.toml"
        path.write_bytes(text.encode("utf-8"))
        return path

    def test_areas_and_threshold(self):
        from bearing.direction.config import area_of, load_config

        path = self.write(
            "[areas]\n"
            'docs = ["docs/", "README.md"]\n'
            'app = ["app/"]\n'
            'deep = ["app/sub/"]\n'
            "[coupling]\n"
            "min_prs = 2\n"
        )
        areas, min_prs = load_config(path)
        self.assertEqual(
            areas,
            [
                ("docs", ("docs/", "README.md")),
                ("app", ("app/",)),
                ("deep", ("app/sub/",)),
            ],
        )
        self.assertEqual(min_prs, 2)
        self.assertEqual(area_of("README.md", areas), "docs")
        self.assertEqual(area_of("app/sub/m.py", areas), "app")
        self.assertEqual(area_of("tests/x.py", areas), "other")

        path = self.write('[areas]\napp = ["app/"]\n')
        self.assertEqual(load_config(path), ([("app", ("app/",))], 3))

    def test_errors(self):
        from bearing.direction.config import ConfigError, load_config

        missing = self.dir / "missing.toml"
        areas_message = f"config {self.dir / 'bearing.toml'}: [areas] must map names to lists of path prefixes"
        threshold_message = f"config {self.dir / 'bearing.toml'}: [coupling] min_prs must be a positive integer"
        cases = [
            ("missing", f"no config at {missing}: pass --config FILE"),
            ("[areas", None),
            ("[coupling]\nmin_prs = 2\n", areas_message),
            ('[areas]\napp = "app/"\n', areas_message),
            ("[areas]\napp = []\n", areas_message),
            ('[areas]\napp = ["app/"]\n[coupling]\nmin_prs = 0\n', threshold_message),
            (
                '[areas]\napp = ["app/"]\n[coupling]\nmin_prs = true\n',
                threshold_message,
            ),
        ]
        for text, message in cases:
            with self.subTest(text=text):
                path = missing if text == "missing" else self.write(text)
                with self.assertRaises(ConfigError) as cm:
                    load_config(path)
                if message is None:
                    prefix = f"cannot read config {path}: "
                    self.assertTrue(str(cm.exception).startswith(prefix))
                    self.assertGreater(len(str(cm.exception)), len(prefix))
                else:
                    self.assertEqual(str(cm.exception), message)
