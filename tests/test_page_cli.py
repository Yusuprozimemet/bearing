"""The page command on the fixture: a merge without a PR record, and its flags against direction's."""

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "tests" / "fixtures" / "make_repo.py"
TOML = REPO / "tests" / "fixtures" / "bearing.toml"
ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}
OPEN = '<script id="bearing-data" type="application/json">'


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        check=False,
        cwd=REPO,
        capture_output=True,
        env=ENV,
    )


def bearing(*args):
    return run("-m", "bearing", *args)


def element(raw):
    text = raw.replace(b"\r\n", b"\n").decode()
    return text.split(OPEN, 1)[1].split("</script>", 1)[0]


class PageCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.out = Path(cls.tmp.name) / "out"
        cls.repo = cls.out / "repo"
        cls.result = run(BUILDER, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def ingest(self, name):
        data = Path(self.tmp.name) / name
        result = bearing(
            "ingest", self.repo, "--prs", self.out / "prs.json", "--data", data
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return data

    def no_ci(self):
        raw = TOML.read_bytes().replace(b"\r\n", b"\n")
        old = b'tooling = ["scripts/", "ci.txt"]'
        self.assertIn(old, raw)
        config = Path(self.tmp.name) / "no-ci.toml"
        config.write_bytes(raw.replace(old, b'tooling = ["scripts/"]'))
        return config

    def page(self, data, config):
        out = Path(self.tmp.name) / f"{data.name}.html"
        result = bearing(
            "page", self.repo, "--data", data, "--config", config, "--out", out
        )
        raw = out.read_bytes()
        return result, json.loads(element(raw)), raw

    def test_merge_without_number(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = self.ingest("subject")
        with closing(sqlite3.connect(data / "bearing.db")) as conn:
            cur = conn.execute(
                "UPDATE commits SET subject_number = NULL, subject = 'Merge branch x'"
                " WHERE sha LIKE '8c1b9f1%'"
            )
            self.assertEqual(cur.rowcount, 1)
            conn.commit()
        result, page, raw = self.page(data, self.no_ci())
        self.assertEqual(result.returncode, 0, result.stderr)
        step = page["steps"][9]
        self.assertTrue(step["sha"].startswith("8c1b9f1"))
        self.assertIsNone(step["number"])
        self.assertEqual(step["title"], "Merge branch x")
        self.assertEqual(step["paragraph"], "")
        self.assertEqual(step["flags"], [])
        self.assertNotIn(b"\r", raw)

    def test_flags_match_direction(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        data = self.ingest("flags")
        config = self.no_ci()
        result, page, _ = self.page(data, config)
        self.assertEqual(result.returncode, 0, result.stderr)
        direction = bearing("direction", self.repo, "--data", data, "--config", config)
        self.assertEqual(direction.returncode, 0, direction.stderr)
        lines = direction.stdout.replace(b"\r\n", b"\n").decode().splitlines()
        i = lines.index("## Said vs done")
        built = [
            f"- #{s['number']} {f['rule']}: {f['claim']} | {', '.join(f['files'])}"
            for s in page["steps"]
            for f in s["flags"]
        ]
        self.assertEqual(lines[i + 1 :], [""] + built)
        flags = [{"rule": "outside-area", "claim": "area tooling", "files": ["ci.txt"]}]
        self.assertEqual(page["steps"][9]["flags"], flags)
