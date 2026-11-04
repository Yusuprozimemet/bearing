"""Structure events between two snapshot-v1 dicts: modules added, removed or renamed, and import edges added or removed."""


def _names_by_path(snapshot):
    return {module["path"]: module["name"] for module in snapshot["modules"]}


def structure_events(old, new, renames):
    """Return the events from old to new as sorted strings, in the order of their groups."""
    old_by_path = _names_by_path(old)
    new_by_path = _names_by_path(new)
    old_names = set(old_by_path.values())
    new_names = set(new_by_path.values())
    # A pair is a rename only when neither name survives on the other side. That also makes the
    # two names differ: a moved file that keeps its name has its old name in new, so is no event.
    # Sorted and de-duplicated, so the order of renames never changes the result.
    pairs = sorted(
        {
            (old_by_path[old_path], new_by_path[new_path])
            for old_path, new_path in renames
            if old_path in old_by_path
            and new_path in new_by_path
            and old_by_path[old_path] not in new_names
            and new_by_path[new_path] not in old_names
        }
    )
    moved = dict(pairs)
    gone = {a for a, _ in pairs}
    came = {b for _, b in pairs}
    # An old edge is compared after renaming, so an edge that only changed its end name is no event.
    old_edges = {(moved.get(a, a), moved.get(b, b)) for a, b in old["imports"]}
    new_edges = {(a, b) for a, b in new["imports"]}
    events = [f"+module {name}" for name in sorted(new_names - old_names - came)]
    events += [f"-module {name}" for name in sorted(old_names - new_names - gone)]
    events += [f"renamed {a} -> {b}" for a, b in pairs]
    events += [f"+import {a} -> {b}" for a, b in sorted(new_edges - old_edges)]
    events += [f"-import {a} -> {b}" for a, b in sorted(old_edges - new_edges)]
    return events
