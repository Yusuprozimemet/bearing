"""The Evidence replay installs what the replayed checks need before it replays them.

The tests run the workflow's own text: the `run:` block of the step "Install what the replayed
checks need" in .github/workflows/evidence.yml, read from the file, in bash (Git's own on Windows,
not WSL's), in a scratch directory, with a stand-in `python` first on PATH that records its
arguments and installs nothing.

    python scripts/test_evidence_workflow.py    # needs PyYAML
"""
import os
import shutil
import subprocess
import tempfile
import unittest

import yaml

from test_diff_limit import BASH

HERE = os.path.dirname(os.path.abspath(__file__))
WORKFLOW = os.path.join(HERE, "..", ".github", "workflows", "evidence.yml")
STEP = "Install what the replayed checks need"
REPLAY = "Replay the closing merge"
REHEARSE = "Rehearse the closing merge"


def step():
    """The step's run: text."""
    with open(WORKFLOW, encoding="utf-8") as f:
        for s in yaml.safe_load(f)["jobs"]["replay"]["steps"]:
            if s.get("name") == STEP:
                return s["run"]
    raise AssertionError(f"no step named {STEP!r} in evidence.yml")


class EvidenceWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        bin_dir = os.path.join(self.dir, "bin")
        os.mkdir(bin_dir)
        self.calls = os.path.join(self.dir, "calls.txt")
        with open(os.path.join(bin_dir, "python"), "w", newline="\n") as f:
            f.write(f'#!/bin/sh\necho "$*" >> "{self.calls.replace(os.sep, "/")}"\n')
        os.chmod(os.path.join(bin_dir, "python"), 0o755)
        self.work = os.path.join(self.dir, "work")
        os.mkdir(self.work)
        self.path = bin_dir.replace(os.sep, "/")

    def run_step(self):
        # Git's bash on Windows wants PATH entries as /c/..., which cygpath gives; elsewhere it is absent
        path = f'export PATH="$(cygpath -u "{self.path}" 2>/dev/null || echo "{self.path}"):$PATH"\n'
        p = subprocess.run([BASH, "-c", path + step()], cwd=self.work, capture_output=True, text=True)
        calls = []
        if os.path.exists(self.calls):
            with open(self.calls) as f:
                calls = f.read().splitlines()
        return p.returncode, p.stdout + p.stderr, calls

    def test_the_install_comes_before_the_replay(self):
        with open(WORKFLOW, encoding="utf-8") as f:
            names = [s.get("name") for s in yaml.safe_load(f)["jobs"]["replay"]["steps"]]
        self.assertIn(STEP, names)
        self.assertLess(names.index(STEP), names.index(REPLAY))

    def test_a_pull_request_rehearses_and_a_push_replays(self):
        with open(WORKFLOW, encoding="utf-8") as f:
            workflow = yaml.safe_load(f)
        triggers = workflow.get("on", workflow.get(True))  # YAML 1.1 reads the key `on` as true
        self.assertIn("pull_request", triggers)
        self.assertIsNone(triggers["pull_request"], "a path or branch filter leaves a required check unreported")
        # the name branch protection requires (docs/kit.md's list in the kit)
        self.assertEqual(workflow["jobs"]["replay"]["name"], "A closed day's evidence replays")
        steps = {s.get("name"): s for s in workflow["jobs"]["replay"]["steps"]}
        self.assertEqual(steps[REPLAY]["if"], "github.event_name != 'pull_request'")
        self.assertEqual(steps[REHEARSE]["if"], "github.event_name == 'pull_request'")
        self.assertLess(list(steps).index(STEP), list(steps).index(REHEARSE))
        # the branch name reaches the command as a variable, not as workflow text
        self.assertEqual(steps[REHEARSE]["run"],
                         'python scripts/close-evidence.py --rehearse "$BRANCH" --base HEAD^1 --head HEAD^2')
        self.assertEqual(steps[REHEARSE]["env"]["BRANCH"], "${{ github.head_ref }}")

    def test_the_package_and_its_dev_tools_are_installed(self):
        # Bearing has no requirements.txt: the replay installs the package editable with its dev
        # tools, as tests.yml does.
        code, out, calls = self.run_step()
        self.assertEqual(code, 0, out)
        self.assertEqual(calls, ["-m pip install -e .[dev]"])


if __name__ == "__main__":
    unittest.main()
