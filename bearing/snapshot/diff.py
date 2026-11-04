"""Structure events between two snapshot-v1 dicts: modules added, removed or renamed, import edges added or removed, import cycles added or removed, and modules that grew past GREW_LINES lines."""

# A module longer than this is reported as grown when it was not longer before.
GREW_LINES = 200


def _names_by_path(snapshot):
    return {module["path"]: module["name"] for module in snapshot["modules"]}


def _cycles(edges):
    """Return the elementary cycles of the edges as tuples, each starting at its least name."""
    nodes = sorted({name for edge in edges for name in edge})
    graph = {node: set() for node in nodes}
    reverse = {node: set() for node in nodes}
    for a, b in edges:
        if a != b:
            graph[a].add(b)
            reverse[b].add(a)
    cycles = set()
    for start in nodes:
        # Only start and the names after it take part, so each cycle is found once, from its least name.
        part = {node for node in nodes if node >= start}
        # Keep only the names that can get back to start: a long acyclic graph then has nothing to walk.
        back = {start}
        stack = [start]
        while stack:
            for prev in reverse[stack.pop()]:
                if prev in part and prev not in back:
                    back.add(prev)
                    stack.append(prev)
        _walk(graph, back, start, [start], cycles)
    return cycles


def _walk(graph, back, start, path, cycles):
    for nxt in sorted(graph[path[-1]]):
        if nxt == start:
            cycles.add(tuple(path))
        elif nxt in back and nxt not in path:
            _walk(graph, back, start, path + [nxt], cycles)


def _cycle_text(cycle):
    return " > ".join(cycle + (cycle[0],))


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
    # The old cycles are the cycles of old_edges, which already carry the renames.
    old_cycles = _cycles(old_edges)
    new_cycles = _cycles(new_edges)
    events += sorted(f"cycle+ {_cycle_text(c)}" for c in new_cycles - old_cycles)
    events += sorted(f"cycle- {_cycle_text(c)}" for c in old_cycles - new_cycles)
    # A grown module is compared with its old self, found through the rename when it has one.
    came_from = {b: a for a, b in pairs}
    old_lines = {module["name"]: module["lines"] for module in old["modules"]}
    grew = []
    for module in new["modules"]:
        old_length = old_lines.get(came_from.get(module["name"], module["name"]))
        # A module added in new has no old length, so it is no growth.
        if (
            module["lines"] > GREW_LINES
            and old_length is not None
            and old_length <= GREW_LINES
        ):
            grew.append(f"grew {module['name']} {module['lines']}")
    events += sorted(grew)
    return events
