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

    def test_cycles_and_growth(self):
        """C07.1: structure_events reports import cycles that appear or break, and modules that grow."""
        from bearing.snapshot.diff import structure_events

        def snapshot(modules, imports):
            return {
                "version": "snapshot-v1",
                "ref": "fixture",
                "modules": [
                    {
                        "name": name,
                        "path": f"{name}.py",
                        "lines": lines,
                        "parse_error": False,
                    }
                    for name, lines in modules
                ],
                "imports": imports,
            }

        old = snapshot(
            [
                ("a", 10),
                ("b", 10),
                ("c", 10),
                ("d", 10),
                ("e", 10),
                ("m", 10),
                ("x", 10),
                ("y", 10),
                ("z", 10),
                ("g1", 200),
                ("g2", 199),
                ("g3", 201),
                ("g4", 150),
            ],
            [
                ["a", "b"],
                ["d", "e"],
                ["e", "d"],
                ["m", "z"],
                ["z", "m"],
                ["x", "y"],
                ["y", "x"],
            ],
        )
        new = snapshot(
            [
                ("a", 10),
                ("b", 10),
                ("c", 10),
                ("d", 10),
                ("e", 10),
                ("m", 10),
                ("k", 10),
                ("x", 10),
                ("w", 10),
                ("g1", 201),
                ("g2", 200),
                ("g3", 300),
                ("g5", 250),
                ("big", 500),
            ],
            [
                ["c", "a"],
                ["a", "b"],
                ["b", "a"],
                ["b", "c"],
                ["d", "e"],
                ["k", "m"],
                ["m", "k"],
            ],
        )
        renames = [("z.py", "k.py"), ("g4.py", "g5.py"), ("y.py", "w.py")]
        expected = [
            "+module big",
            "renamed g4 -> g5",
            "renamed y -> w",
            "renamed z -> k",
            "+import b -> a",
            "+import b -> c",
            "+import c -> a",
            "-import e -> d",
            "-import w -> x",
            "-import x -> w",
            "cycle+ a > b > a",
            "cycle+ a > b > c > a",
            "cycle- d > e > d",
            "cycle- w > x > w",
            "grew g1 201",
            "grew g5 250",
        ]
        self.assertEqual(structure_events(old, new, renames), expected)
        self.assertEqual(structure_events(old, new, list(reversed(renames))), expected)
        self.assertEqual(structure_events(old, old, []), [])
