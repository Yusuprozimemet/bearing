"""The pairs of files that change in the same pull requests, and the pull requests they changed in."""

from bearing.direction.config import area_of


def latest_names(commits):
    # commits are (paths, renames) in first-parent order; a file is an id, and current maps
    # each name it has now to its id. A rename moves the id, so a chain ends at the last name.
    current = {}
    name = {}

    def new_file(path):
        file_id = len(name)
        name[file_id] = path
        return file_id

    ids_by_commit = []
    for paths, renames in commits:
        # every old name is taken before any new name is set, so the renames of one commit do not chain
        moved = []
        for old, _ in renames:
            if old not in current:
                current[old] = new_file(old)
            moved.append(current.pop(old))
        for (_, new), file_id in zip(renames, moved):
            current[new] = file_id
            name[file_id] = new
        ids = []
        for path in paths:
            if path not in current:
                current[path] = new_file(path)
            ids.append(current[path])
        ids_by_commit.append(ids)
    return [[name[file_id] for file_id in ids] for ids in ids_by_commit]


def coupling(prs, areas, min_prs):
    # A PR listed twice, or with a path twice, counts once: its paths are one set.
    paths_by_pr = {}
    for number, paths in prs:
        paths_by_pr.setdefault(number, set()).update(paths)
    numbers_by_pair = {}
    for number, paths in paths_by_pr.items():
        ordered = sorted(paths)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1 :]:
                numbers_by_pair.setdefault((a, b), set()).add(number)
    return sorted(
        (a, b, sorted(numbers), area_of(a, areas), area_of(b, areas))
        for (a, b), numbers in numbers_by_pair.items()
        if len(numbers) >= min_prs
    )
