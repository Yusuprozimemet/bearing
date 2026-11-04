"""The snapshot of the fixture's main and of its golden commit, read from git's object store."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "snapshot-448fc4d.json"


def module_lines(snap):
    return [
        f"{m['name']} {m['path']} {m['lines']} {m['parse_error']}"
        for m in snap["modules"]
    ]


class SnapshotTreeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.result = subprocess.run(
            [sys.executable, str(BUILDER), str(cls.out)],
            check=False,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_main(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.snapshot.tree import SnapshotError, snapshot

        repo = self.out / "repo"
        snap = snapshot(repo, "main")
        self.assertEqual(snap["version"], "snapshot-v1")
        self.assertEqual(snap["ref"], "8c1b9f1b90d3e582590942e15b131cea986d94c3")
        self.assertEqual(
            module_lines(snap),
            [
                "app app/__init__.py 1 False",
                "app.a app/a.py 3 False",
                "app.b app/b.py 5 False",
                "app.broken app/broken.py 2 True",
                "app.core app/core.py 257 False",
                "app.crlf app/crlf.py 5 False",
                "app.extra app/extra.py 5 False",
                "app.pkg app/pkg/__init__.py 5 False",
                "app.sub app/sub/__init__.py 1 False",
                "app.sub.mod app/sub/mod.py 8 False",
                "lib src/lib/__init__.py 1 False",
                "lib.util src/lib/util.py 17 False",
                "scripts.config scripts/config.py 3 False",
                "scripts.run scripts/run.py 5 False",
                "scripts.tools scripts/tools.py 7 False",
                "tests.contract.test_api tests/contract/test_api.py 5 False",
            ],
        )
        self.assertEqual(
            snap["imports"],
            [
                ["app", "app.core"],
                ["app.a", "app.b"],
                ["app.sub.mod", "app.core"],
                ["app.sub.mod", "app.pkg"],
                ["lib.util", "app.core"],
                ["scripts.run", "scripts.tools"],
                ["scripts.tools", "scripts.config"],
            ],
        )
        with self.assertRaises(SnapshotError) as cm:
            snapshot(repo, "no-such-ref")
        self.assertEqual(str(cm.exception), "not a commit: no-such-ref")

    def test_golden_content(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        from bearing.snapshot.tree import snapshot

        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(golden["version"], "snapshot-v1")
        self.assertEqual(golden["ref"], "448fc4dc915289f0b3f0254cf80360b56f48513a")
        self.assertEqual(
            module_lines(golden),
            [
                "app app/__init__.py 1 False",
                "app.a app/a.py 3 False",
                "app.b app/b.py 7 False",
                "app.broken app/broken.py 2 True",
                "app.core app/core.py 253 False",
                "app.crlf app/crlf.py 5 False",
                "app.legacy app/legacy.py 3 False",
                "app.pkg app/pkg/__init__.py 5 False",
                "app.sub app/sub/__init__.py 1 False",
                "app.sub.mod app/sub/mod.py 8 False",
                "lib src/lib/__init__.py 1 False",
                "lib.util src/lib/util.py 13 False",
                "scripts.config scripts/config.py 3 False",
                "scripts.helpers scripts/helpers.py 7 False",
                "scripts.run scripts/run.py 5 False",
            ],
        )
        self.assertEqual(
            golden["imports"],
            [
                ["app", "app.core"],
                ["app.a", "app.b"],
                ["app.b", "app.a"],
                ["app.sub.mod", "app.core"],
                ["app.sub.mod", "app.pkg"],
                ["lib.util", "app.core"],
                ["scripts.helpers", "scripts.config"],
                ["scripts.run", "scripts.helpers"],
            ],
        )
        self.assertEqual(
            snapshot(self.out / "repo", "448fc4dc915289f0b3f0254cf80360b56f48513a"),
            golden,
        )
