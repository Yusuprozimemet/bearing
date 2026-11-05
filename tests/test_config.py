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

    def test_rules(self):
        from bearing.direction.config import load_rules

        path = self.write(
            "[areas]\n"
            'app = ["app/"]\n'
            "[rules.contract-impact]\n"
            'paths = ["tests/contract/", "api/"]\n'
            "[rules.outside-area]\n"
        )
        self.assertEqual(
            load_rules(path),
            [("contract-impact", ("tests/contract/", "api/")), ("outside-area", ())],
        )

        path = self.write('[areas]\napp = ["app/"]\n')
        self.assertEqual(load_rules(path), [])

    def test_rule_errors(self):
        from bearing.direction.config import ConfigError, load_rules

        areas = '[areas]\napp = ["app/"]\n'
        missing = self.dir / "missing.toml"
        table_message = f"config {self.dir / 'bearing.toml'}: [rules] must be a table of rule tables"
        unknown_message = f"config {self.dir / 'bearing.toml'}: unknown rule typo: the rules are outside-area, contract-impact"
        paths_message = f"config {self.dir / 'bearing.toml'}: [rules.contract-impact] paths must be a list of path prefixes"
        cases = [
            ("missing", f"no config at {missing}: pass --config FILE"),
            ("rules = 3\n" + areas, table_message),
            ("rules = { outside-area = 1 }\n" + areas, table_message),
            (areas + "[rules.typo]\n", unknown_message),
            (areas + "[rules.contract-impact]\n", paths_message),
            (areas + "[rules.contract-impact]\npaths = []\n", paths_message),
            (areas + '[rules.contract-impact]\npaths = "tests/"\n', paths_message),
        ]
        for text, message in cases:
            with self.subTest(text=text):
                path = missing if text == "missing" else self.write(text)
                with self.assertRaises(ConfigError) as cm:
                    load_rules(path)
                self.assertEqual(str(cm.exception), message)

    def test_outside_area_shared(self):
        from bearing.direction.config import ConfigError, load_rules

        path = self.write(
            '[areas]\napp = ["app/"]\n[rules.outside-area]\nshared = ["CHANGES.md", "docs/shared/"]\n'
        )
        self.assertEqual(
            load_rules(path), [("outside-area", ("CHANGES.md", "docs/shared/"))]
        )

        path = self.write(
            '[areas]\napp = ["app/"]\n[rules.outside-area]\npaths = ["x/"]\n'
        )
        self.assertEqual(load_rules(path), [("outside-area", ())])

        message = f"config {self.dir / 'bearing.toml'}: [rules.outside-area] shared must be a list of path prefixes"
        for shared in ["shared = []", 'shared = "CHANGES.md"', "shared = [1]"]:
            text = f'[areas]\napp = ["app/"]\n[rules.outside-area]\n{shared}\n'
            with self.subTest(text=text):
                path = self.write(text)
                with self.assertRaises(ConfigError) as cm:
                    load_rules(path)
                self.assertEqual(str(cm.exception), message)

    def test_example(self):
        from bearing.direction.config import load_config, load_rules

        path = Path(__file__).resolve().parents[1] / "bearing.toml.example"
        areas, min_prs = load_config(path)
        self.assertGreaterEqual(len(areas), 1)
        self.assertEqual(min_prs, 3)
        self.assertEqual(
            load_rules(path),
            [("outside-area", ()), ("contract-impact", ("tests/contract/",))],
        )

    def test_kit_config(self):
        from bearing.direction.config import load_config, load_rules

        path = Path(__file__).resolve().parents[1] / "docs" / "kit" / "bearing.toml"
        areas, min_prs = load_config(path)
        self.assertEqual(
            areas,
            [
                (
                    "dashboard",
                    (
                        "scripts/spec-drift.py",
                        "scripts/test_spec_drift.py",
                        "docs/dashboard/",
                        ".github/workflows/spec-drift-tests.yml",
                        "spec-drift.config.json",
                        "scripts/demo-data.py",
                        "scripts/test_demo_data.py",
                        "kit/compare-page.py",
                        "kit/page/",
                        "kit/starter-check.py",
                    ),
                ),
                (
                    "tooling",
                    (
                        "scripts/",
                        ".github/",
                        ".claude/",
                        "kit/replay/",
                        "kit/compare-page.py",
                        "kit/page/",
                        ".gitignore",
                        ".gitattributes",
                        ".flake8",
                    ),
                ),
                ("specs", ("specs/",)),
                (
                    "docs",
                    (
                        "docs/",
                        "kit/ASSESSMENT.md",
                        "kit/comparison/",
                        "kit/examples/",
                        "kit/jobmatch/",
                        "kit/lessons/",
                        "kit/six-kits-assessment.md",
                        "kit/six-kits-plan.md",
                        "kit/v2-manifest.md",
                        "README.md",
                        "CLAUDE.md",
                        "plan.md",
                    ),
                ),
            ],
        )
        self.assertEqual(min_prs, 3)
        self.assertEqual(
            load_rules(path),
            [
                (
                    "outside-area",
                    (
                        "kit/CHANGES.md",
                        "kit/SOURCE.md",
                        "CHANGES.md",
                        "SOURCE.md",
                        "CLAUDE.md",
                        "README.md",
                        "AGENTS.md",
                        "plan.md",
                        "specs/README.md",
                        "specs/_template.md",
                        "specs/_short-template.md",
                        "templates/",
                    ),
                )
            ],
        )
