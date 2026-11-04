"""Structure events between two snapshots: added, removed and renamed modules, and the import edges that change."""

import unittest


class StructureEventsTest(unittest.TestCase):
    """C06.1: structure_events reports module and import changes, applying renames to the old edges."""

    def test_events(self):
        from bearing.snapshot.diff import structure_events

        def snapshot(modules, imports):
            return {
                "version": "snapshot-v1",
                "ref": "fixture",
                "modules": [
                    {"name": name, "path": path, "lines": 1, "parse_error": False}
                    for name, path in modules
                ],
                "imports": imports,
            }

        old = snapshot(
            [
                ("app", "app/__init__.py"),
                ("app.b", "app/b.py"),
                ("app.c", "app/c.py"),
                ("app.old", "app/old.py"),
                ("scripts.helpers", "scripts/helpers.py"),
                ("scripts.run", "scripts/run.py"),
            ],
            [
                ["app", "app.b"],
                ["app.b", "app.c"],
                ["app.c", "app.old"],
                ["scripts.helpers", "app.b"],
                ["scripts.run", "scripts.helpers"],
            ],
        )
        new = snapshot(
            [
                ("app", "app/__init__.py"),
                ("app.c", "src/app/c.py"),
                ("app.new", "app/new.py"),
                ("scripts.run", "scripts/run.py"),
                ("scripts.tools", "scripts/tools.py"),
            ],
            [
                ["app", "app.c"],
                ["app.c", "app.new"],
                ["scripts.run", "scripts.tools"],
                ["scripts.tools", "app.c"],
            ],
        )
        renames = [
            ("scripts/helpers.py", "scripts/tools.py"),
            ("app/c.py", "src/app/c.py"),
            ("docs/old.md", "app/new.py"),
            ("app/old.py", "scripts/run.py"),
            ("app/__init__.py", "app/new.py"),
        ]
        expected = [
            "+module app.new",
            "-module app.b",
            "-module app.old",
            "renamed scripts.helpers -> scripts.tools",
            "+import app -> app.c",
            "+import app.c -> app.new",
            "+import scripts.tools -> app.c",
            "-import app -> app.b",
            "-import app.b -> app.c",
            "-import app.c -> app.old",
            "-import scripts.tools -> app.b",
        ]
        self.assertEqual(structure_events(old, new, renames), expected)
        self.assertEqual(structure_events(old, new, list(reversed(renames))), expected)
        self.assertEqual(structure_events(old, old, []), [])
