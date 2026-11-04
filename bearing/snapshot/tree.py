"""The Python files of one commit, read from git's object store: names, line counts and import edges, and the renames between two commits."""

import subprocess

from bearing.snapshot.modules import (
    count_lines,
    import_edges,
    module_names,
    parse_imports,
)


class SnapshotError(Exception):
    pass


def _git(repo, *args):
    # Every call is read-only and takes a list, so no shell ever sees a ref or a path.
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        raise SnapshotError(f"cannot run git in {repo}: {exc.strerror or exc}") from exc


def _read_blob(repo, objsha):
    blob = _git(repo, "cat-file", "blob", objsha)
    if blob.returncode != 0:
        raise SnapshotError(blob.stderr.decode().strip())
    return blob.stdout


def snapshot(repo, ref, cache=None):
    if _git(repo, "rev-parse", "--git-dir").returncode != 0:
        raise SnapshotError(f"not a git repository: {repo}")
    done = _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if done.returncode != 0:
        raise SnapshotError(f"not a commit: {ref}")
    sha = done.stdout.decode().strip()
    listed = _git(repo, "ls-tree", "-r", "-z", "--full-tree", sha)
    if listed.returncode != 0:
        raise SnapshotError(listed.stderr.decode().strip())
    # Only regular files count: a symlink (120000) or a submodule (commit) is not Python source here.
    kept = []
    for entry in listed.stdout.split(b"\0"):
        if not entry:
            continue
        meta, _, raw_path = entry.partition(b"\t")
        mode, kind, objsha = meta.decode().split(" ")
        path = raw_path.decode("utf-8", errors="surrogateescape")
        if kind == "blob" and mode in ("100644", "100755") and path.endswith(".py"):
            kept.append((path, objsha))
    paths = [path for path, _ in kept]
    names = module_names(paths)
    modules = []
    imports = {}
    for path, objsha in kept:
        if cache is None:
            data = _read_blob(repo, objsha)
            if path not in names:
                continue
            lines, found = count_lines(data), parse_imports(data)
        else:
            if path not in names:
                continue
            lines, found = cache.get(
                objsha, lambda objsha=objsha: _read_blob(repo, objsha)
            )
        imports[path] = found
        modules.append(
            {
                "name": names[path],
                "path": path,
                "lines": lines,
                "parse_error": found is None,
            }
        )
    modules.sort(key=lambda m: (m["name"], m["path"]))
    return {
        "version": "snapshot-v1",
        "ref": sha,
        "modules": modules,
        "imports": import_edges(imports, names),
    }


def renamed_paths(repo, old_sha, new_sha):
    # Read-only, as snapshot is. -M finds the renames; -z keeps a path with odd bytes unquoted.
    done = _git(
        repo, "diff", "--no-ext-diff", "-M", "--name-status", "-z", old_sha, new_sha
    )
    if done.returncode != 0:
        raise SnapshotError(done.stderr.decode().strip())
    # Each entry is a status, then one path, or two for an R or C entry; empty fields are the ends.
    fields = [field for field in done.stdout.split(b"\0") if field]
    pairs = []
    index = 0
    while index < len(fields):
        status = fields[index][:1]
        if status in (b"R", b"C"):
            old, new = fields[index + 1], fields[index + 2]
            index += 3
            if status == b"R":
                pairs.append(
                    (
                        old.decode("utf-8", errors="surrogateescape"),
                        new.decode("utf-8", errors="surrogateescape"),
                    )
                )
        else:
            index += 2
    return sorted(pairs)
