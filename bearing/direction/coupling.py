"""The pairs of files that change in the same pull requests, and the pull requests they changed in."""

from bearing.direction.config import area_of


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
