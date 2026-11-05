"""Reads bearing.toml: the path areas, in file order, the coupling threshold, and the rules."""

import tomllib
from pathlib import Path


class ConfigError(Exception):
    pass


def _is_prefix_list(value):
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(isinstance(p, str) for p in value)
    )


def _read(path):
    # load_config and load_rules read the file the same way, so they give the same messages.
    if not Path(path).is_file():
        raise ConfigError(f"no config at {path}: pass --config FILE")
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from None


def load_config(path):
    data = _read(path)

    areas = data.get("areas")
    if (
        not isinstance(areas, dict)
        or not areas
        or not all(_is_prefix_list(v) for v in areas.values())
    ):
        raise ConfigError(
            f"config {path}: [areas] must map names to lists of path prefixes"
        )
    areas = [(name, tuple(prefixes)) for name, prefixes in areas.items()]

    coupling = data.get("coupling", {})
    min_prs = coupling.get("min_prs", 3) if isinstance(coupling, dict) else None
    # bool is an int in Python, but "min_prs = true" is not a count of pull requests
    if isinstance(min_prs, bool) or not isinstance(min_prs, int) or min_prs < 1:
        raise ConfigError(
            f"config {path}: [coupling] min_prs must be a positive integer"
        )
    return areas, min_prs


def load_rules(path):
    # Only the [rules] table is read here; [areas] and [coupling] are load_config's.
    data = _read(path)

    rules = data.get("rules", {})
    if not isinstance(rules, dict) or not all(
        isinstance(table, dict) for table in rules.values()
    ):
        raise ConfigError(f"config {path}: [rules] must be a table of rule tables")
    found = []
    for rule_id, table in rules.items():
        if rule_id == "outside-area":
            # it takes no paths of its own; a paths key here is ignored
            # shared lists files any area may change, so they are not outside it
            if "shared" not in table:
                found.append((rule_id, ()))
                continue
            shared = table.get("shared")
            if not _is_prefix_list(shared):
                raise ConfigError(
                    f"config {path}: [rules.outside-area] shared must be a list of path prefixes"
                )
            found.append((rule_id, tuple(shared)))
        elif rule_id == "contract-impact":
            paths = table.get("paths")
            if not _is_prefix_list(paths):
                raise ConfigError(
                    f"config {path}: [rules.contract-impact] paths must be a list of path prefixes"
                )
            found.append((rule_id, tuple(paths)))
        else:
            raise ConfigError(
                f"config {path}: unknown rule {rule_id}: the rules are outside-area, contract-impact"
            )
    return found


def area_of(path, areas):
    # The first area in file order wins, even when a later one has a longer prefix.
    for name, prefixes in areas:
        if any(path.startswith(prefix) for prefix in prefixes):
            return name
    return "other"
