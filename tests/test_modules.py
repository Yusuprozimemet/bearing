"""Module names, line counts, import parsing and import edges: the snapshot's pure functions, on made-up trees and bytes."""

import unittest
import warnings


class ModuleNameTest(unittest.TestCase):
    """C05.1: module_names names each path from its import root, and leaves out the empty names."""

    def test_names(self):
        from bearing.snapshot import modules

        paths = [
            "app/__init__.py",
            "app/core.py",
            "app/pkg/__init__.py",
            "src/lib/__init__.py",
            "src/lib/util.py",
            "scripts/helpers.py",
            "tests/contract/test_api.py",
            "setup.py",
            "src/x.py",
            "x.py",
            "__init__.py",
            "src/__init__.py",
        ]
        expected = {
            "app/__init__.py": "app",
            "app/core.py": "app.core",
            "app/pkg/__init__.py": "app.pkg",
            "src/lib/__init__.py": "lib",
            "src/lib/util.py": "lib.util",
            "scripts/helpers.py": "scripts.helpers",
            "tests/contract/test_api.py": "tests.contract.test_api",
            "setup.py": "setup",
            "src/x.py": "src.x",
            "x.py": "x",
        }
        self.assertEqual(modules.module_names(paths), expected)
        self.assertEqual(modules.module_names(paths[::-1]), expected)
        self.assertEqual(modules.module_names(["src/x.py"]), {"src/x.py": "x"})


class LinesTest(unittest.TestCase):
    """C05.2: count_lines counts b"\\n" and a last line without one; a lone \\r is no line end."""

    def test_counts(self):
        from bearing.snapshot import modules

        cases = [
            (b"", 0),
            (b"a", 1),
            (b"a\n", 1),
            (b"a\nb", 2),
            (b"a\r\nb\r\n", 2),
            (b"a\rb\n", 1),
            (b"\n\n\n", 3),
        ]
        for data, expected in cases:
            with self.subTest(data=data):
                self.assertEqual(modules.count_lines(data), expected)


class ParseTest(unittest.TestCase):
    """C05.3: parse_imports returns None for what does not parse, and [] for what only warns."""

    def test_imports_and_errors(self):
        from bearing.snapshot import modules

        for data in [
            b"def broken(:\n    return 1\n",
            b"x = '\xe9'\n",
            b"x = 1\x00\n",
            b"1+" * 200000 + b"1\n",
            b"x=" + b"-" * 200000 + b"1\n",
        ]:
            with self.subTest(data=data[:20]):
                self.assertIsNone(modules.parse_imports(data))
        self.assertEqual(
            modules.parse_imports(b"# -*- coding: latin-1 -*-\nx = '\xe9'\n"), []
        )
        self.assertEqual(
            modules.parse_imports(
                b"import b\r\n\r\ndef f():\r\n    from ..pkg import h, k\r\n"
            ),
            [(0, "b", ()), (2, "pkg", ("h", "k"))],
        )
        self.assertEqual(
            modules.parse_imports(b"from . import core\nimport a.b, c\n"),
            [(0, "a.b", ()), (0, "c", ()), (1, "", ("core",))],
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertEqual(modules.parse_imports(b'x = "\\d"\n'), [])


class ResolveTest(unittest.TestCase):
    """C05.4: import_edges resolves each import to the modules of the tree, and to nothing else."""

    def test_edges(self):
        from bearing.snapshot import modules

        sources = {
            "app/__init__.py": "from . import core",
            "app/core.py": "import os\nimport app.core",
            "app/pkg/__init__.py": "",
            "app/sub/__init__.py": "",
            "app/sub/mod.py": "from ..pkg import h\nfrom ..core import f\nfrom ... import app",
            "app/x.py": "import core\nfrom app import pkg, sub",
            "src/lib/util.py": "import app.core\nimport app.nothing",
            "scripts/run.py": "import helpers\nimport app",
            "scripts/helpers.py": "from config import DEBUG",
            "scripts/config.py": "",
            "scripts/app.py": "",
            "app/broken.py": "def broken(:",
        }
        imports = {
            path: modules.parse_imports(source.encode("utf-8"))
            for path, source in sources.items()
        }
        names = modules.module_names(sources)
        self.assertEqual(
            modules.import_edges(imports, names),
            [
                ["app", "app.core"],
                ["app.sub.mod", "app.core"],
                ["app.sub.mod", "app.pkg"],
                ["app.x", "app.pkg"],
                ["app.x", "app.sub"],
                ["lib.util", "app.core"],
                ["scripts.helpers", "scripts.config"],
                ["scripts.run", "app"],
                ["scripts.run", "scripts.helpers"],
            ],
        )
