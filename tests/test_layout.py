"""The layers: the cycle example, the fixture's snapshots, and the same output under two hash seeds."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from bearing.snapshot.tree import snapshot

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
GOLDEN = REPO / "tests" / "fixtures" / "expected" / "page-v1.json"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
MODULES = ["a", "b", "c", "d"]
IMPORTS = [("a", "b"), ("b", "a"), ("c", "a"), ("a", "x"), ("d", "d")]
CHILD = """
import json, sys
from pathlib import Path
from bearing.page.layout import layers
from bearing.snapshot.tree import snapshot
repo = Path(sys.argv[1])
# The page's steps: the squash merge #6 is one, the side branch's #7 is not.
steps = json.loads(Path(sys.argv[2]).read_bytes())["steps"]
for sha in [step["sha"] for step in steps]:
    snap = snapshot(repo, sha)
    print(json.dumps(layers([m["name"] for m in snap["modules"]], snap["imports"])))
"""


def layers(modules, imports):
    # Imported here, so on the code before the track the test fails, not the module's import.
    from bearing.page.layout import layers

    return layers(modules, imports)


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=ENV,
    )


class LayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.repo = cls.out / "repo"
        cls.result = run(BUILDER, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_cycle_is_one_node(self):
        expected = [["c", "d"], ["a", "b"]]
        self.assertEqual(layers(MODULES, IMPORTS), expected)
        self.assertEqual(layers(MODULES, list(reversed(IMPORTS))), expected)

    def test_fixture_layers(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        cases = {
            "00394fb": [
                [
                    "app",
                    "app.a",
                    "app.b",
                    "app.crlf",
                    "app.legacy",
                    "app.sub",
                    "app.sub.mod",
                    "lib",
                    "lib.util",
                    "scripts.run",
                ],
                ["app.core", "app.pkg", "scripts.helpers"],
                ["scripts.config"],
            ],
            "e5fa51f": [
                [
                    "app",
                    "app.a",
                    "app.broken",
                    "app.crlf",
                    "app.extra",
                    "app.sub",
                    "app.sub.mod",
                    "lib",
                    "lib.util",
                    "scripts.run",
                    "tests.contract.test_api",
                ],
                ["app.b", "app.core", "app.pkg", "scripts.tools"],
                ["scripts.config"],
            ],
        }
        for ref, expected in cases.items():
            with self.subTest(ref=ref):
                snap = snapshot(self.repo, ref)
                names = [m["name"] for m in snap["modules"]]
                self.assertEqual(layers(names, snap["imports"]), expected)

    def test_same_under_two_hash_seeds(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        outputs = []
        for seed in ("0", "1"):
            env = dict(ENV, PYTHONHASHSEED=seed)
            proc = subprocess.run(
                [sys.executable, "-c", CHILD, str(self.repo), str(GOLDEN)],
                check=False,
                cwd=REPO,
                capture_output=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            outputs.append(proc.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(len(outputs[0].decode().splitlines()), 10)
