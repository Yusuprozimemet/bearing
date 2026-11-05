"""The layers of an import graph: each module sits one layer below the modules that import it."""


def layers(modules, imports):
    names = sorted(set(modules))
    succ = _succ(names, imports)
    comp = _components(names, succ)
    nodes = sorted(set(comp.values()))
    out = {node: set() for node in nodes}
    indeg = {node: 0 for node in nodes}
    for name in names:
        for target in succ[name]:
            a, b = comp[name], comp[target]
            if a != b and b not in out[a]:
                out[a].add(b)
                indeg[b] += 1
    # Kahn's order: a node's layer is final once every node above it has been counted.
    depth = {node: 0 for node in nodes}
    ready = [node for node in nodes if indeg[node] == 0]
    while ready:
        node = ready.pop()
        for target in sorted(out[node]):
            depth[target] = max(depth[target], depth[node] + 1)
            indeg[target] -= 1
            if indeg[target] == 0:
                ready.append(target)
    if not names:
        return []
    result = [[] for _ in range(max(depth[comp[name]] for name in names) + 1)]
    for name in names:
        result[depth[comp[name]]].append(name)
    return result


def components(modules, imports):
    # Each module maps to the smallest name in its strongly connected component.
    names = sorted(set(modules))
    return _components(names, _succ(names, imports))


def _succ(names, imports):
    known = set(names)
    succ = {name: set() for name in names}
    for importer, imported in imports:
        if importer in known and imported in known and importer != imported:
            succ[importer].add(imported)
    return {name: sorted(targets) for name, targets in succ.items()}


def _components(names, succ):
    # Tarjan's algorithm with an explicit stack of (node, next child) frames, so a long
    # import chain cannot reach Python's recursion limit. Each component is labelled with
    # its smallest name, which does not depend on the order the walk found it in.
    index = {}
    low = {}
    stack = []
    on_stack = set()
    comp = {}
    for root in names:
        if root in index:
            continue
        index[root] = low[root] = len(index)
        stack.append(root)
        on_stack.add(root)
        frames = [(root, 0)]
        while frames:
            node, pos = frames[-1]
            if pos < len(succ[node]):
                frames[-1] = (node, pos + 1)
                child = succ[node][pos]
                if child not in index:
                    index[child] = low[child] = len(index)
                    stack.append(child)
                    on_stack.add(child)
                    frames.append((child, 0))
                elif child in on_stack:
                    low[node] = min(low[node], index[child])
                continue
            frames.pop()
            if frames:
                parent = frames[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                members = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    members.append(member)
                    if member == node:
                        break
                label = min(members)
                for member in members:
                    comp[member] = label
    return comp
