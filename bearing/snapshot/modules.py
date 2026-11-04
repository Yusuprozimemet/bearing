"""Module names, line counts and import edges, from paths and bytes alone: no git, no files read here."""

import ast
import warnings


def _dotted(parts):
    # __init__.py is named by its package, so its last part goes.
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def module_names(paths):
    # A src/ path is named from src/ and, when that name is another path's outside src/, from the repository root.
    named = []
    for path in paths:
        parts = path.split("/")
        parts[-1] = parts[-1][:-3]
        under_src = parts[0] == "src" and len(parts) > 1
        name = _dotted(parts[1:] if under_src else parts)
        # A name that is empty (__init__.py, src/__init__.py) names no module, so it takes no part in a collision.
        if name:
            named.append((path, under_src, name, _dotted(parts)))
    outside = {name for _, under_src, name, _ in named if not under_src}
    return {
        path: root if under_src and name in outside else name
        for path, under_src, name, root in named
    }


def count_lines(data):
    # A lone \r is not a line end, so only b"\n" counts; a last line without one still counts.
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def parse_imports(data):
    # The warnings are silenced here so that a SyntaxWarning in a file never becomes a parse error under -W error.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            tree = ast.parse(data)
        except (SyntaxError, ValueError, RecursionError, MemoryError):
            return None
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((0, alias.name, ()) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.append(
                (node.level, node.module or "", tuple(a.name for a in node.names))
            )
    return sorted(found)


def _targets(base, members, known):
    # A plain import names its module; a from-import names each member's module, or the base when the member is not one.
    if not members:
        return {base} if base in known else set()
    found = set()
    for member in members:
        if base and base + "." + member in known:
            found.add(base + "." + member)
        elif base in known:
            found.add(base)
    return found


def import_edges(imports, names):
    known = set(names.values())
    tree = set(names) | set(imports)
    edges = set()
    for path, found in imports.items():
        if found is None or path not in names:
            continue
        importer = names[path]
        package = (
            importer.split(".")
            if path.endswith("__init__.py")
            else importer.split(".")[:-1]
        )
        # A file in a folder with no __init__.py may import its siblings by bare name, as a script does.
        folder, _, _ = path.rpartition("/")
        init = (folder + "/" if folder else "") + "__init__.py"
        prefix = ".".join(importer.split(".")[:-1])
        for level, module, members in found:
            targets = set()
            if level > 0:
                if level - 1 < len(package):
                    base = ".".join(package[: len(package) - (level - 1)])
                    if module:
                        base = base + "." + module if base else module
                    targets = _targets(base, members, known)
            else:
                targets = _targets(module, members, known)
                if not targets and init not in tree and prefix:
                    targets = _targets(prefix + "." + module, members, known)
            edges.update((importer, target) for target in targets if target != importer)
    return sorted([list(edge) for edge in edges])
