"""Reads bearing.toml: the path areas, in file order, and the coupling threshold."""

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


def load_config(path):
    if not Path(path).is_file():
        raise ConfigError(f"no config at {path}: pass --config FILE")
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from None

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


def area_of(path, areas):
    # The first area in file order wins, even when a later one has a longer prefix.
    for name, prefixes in areas:
        if any(path.startswith(prefix) for prefix in prefixes):
            return name
    return "other"
