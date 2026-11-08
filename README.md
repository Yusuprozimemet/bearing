# Bearing

Bearing is a Python command-line tool that reads a repository's merge history and the text of its
pull requests, and shows where the code is heading: how its structure changed merge by merge,
where the work goes, and where what a PR said differs from what it changed.

It runs locally, writes nothing to the repository it reads, and makes no GitHub write calls. It
uses no LLM, so the same history gives the same output every time.

It is also the first product built with the
[agentic workflow kit](https://github.com/Yusuprozimemet/agentic-workflow-kit): every change began
as a spec, and the work was measured as it went.
[The live dashboard](https://yusuprozimemet.github.io/bearing/) shows that record.

## What it gives you

| Command | Output |
| --- | --- |
| `bearing ingest <repo>` | Stores the merges and PRs, and reports any it could not match |
| `bearing changelog` | A changelog written from the PRs |
| `bearing snapshot <repo> <ref>` | The Python modules and imports at one commit, as JSON |
| `bearing timeline <repo>` | What each merge changed in the structure |
| `bearing direction <repo>` | Churn by area and week, files that change together, and "said vs done" flags |
| `bearing page <repo> --out <file>` | One HTML file to step through the history, with an import graph per merge; it opens offline |

The "said vs done" flags are prompts to go and look, not verdicts. The page marks each one
"unverified".

Import graphs cover Python only.

## Try it

You need Python 3.12 or later and Git. Reading PRs needs the
[GitHub CLI](https://cli.github.com/), signed in, unless you pass them as a file with `--prs`.

```bash
git clone https://github.com/Yusuprozimemet/bearing.git
cd bearing
python -m pip install -e .

cp bearing.toml.example ../bearing.toml   # edit its [areas] to match the repository you read

bearing ingest .
bearing changelog
bearing timeline .
bearing direction . --config ../bearing.toml
bearing page . --config ../bearing.toml --out ../bearing.html
```

These commands read Bearing's own history. To read another repository, pass its path instead of
`.`. The history is stored in `.bearing` in the current folder; `--data <folder>` changes that.

Run on its own repository at PR #85, `bearing ingest` reports 85 merges, all 85 matched to their
PRs, and `bearing page` writes a page of 85 steps.

## How it is built

The hard part is not reading Git. It is getting right answers on real, messy histories: squash
merges, PRs merged out of order, renamed files, files that will not parse, and PR text that does
not follow a template. [plan.md](plan.md) lists each of these and how it is handled.

The tool was built in 12 day specs, 85 merged pull requests in all. Output formats are pinned by
golden-file tests.

- [plan.md](plan.md): the goal, the phases and the course corrections
- [specs/](specs/): the day specs and their acceptance criteria
- [docs/lab-notebook.md](docs/lab-notebook.md): what each day delivered and which defects it found
- [docs/workflow.md](docs/workflow.md): the working order
- [CLAUDE.md](CLAUDE.md): the rules for agent sessions

For the workflow itself and how to start a project from it, see the
[kit's README](https://github.com/Yusuprozimemet/agentic-workflow-kit#readme).

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check . && ruff format --check .
```
