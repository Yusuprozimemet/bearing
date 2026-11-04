"""The files a commit changed and how many lines each gained and lost, from git's numstat."""

from bearing.snapshot.tree import SnapshotError, _git


def _count(field):
    # git prints "-" for a binary file, which has no line counts
    return 0 if field == b"-" else int(field)


def parse_numstat(raw):
    fields = raw.split(b"\x00")
    end = len(fields) - 1  # the last field is what follows the final NUL
    rows = []
    i = 0
    while i < end:
        added, deleted, path = fields[i].split(b"\t", 2)
        i += 1
        if path == b"":
            # a rename: an empty path, then the old path and the new one, each NUL-ended
            path = fields[i + 1]
            i += 2
        rows.append(
            (
                path.decode("utf-8", errors="surrogateescape"),
                _count(added),
                _count(deleted),
            )
        )
    return sorted(rows)


def changed_files(repo, sha):
    done = _git(repo, "diff", "--no-ext-diff", "--numstat", "-z", "-M", f"{sha}^1", sha)
    if done.returncode != 0:
        raise SnapshotError(done.stderr.decode().strip())
    return parse_numstat(done.stdout)
