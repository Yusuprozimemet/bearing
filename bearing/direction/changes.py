"""The files a commit changed and how many lines each gained and lost, from git's numstat."""

from bearing.snapshot.tree import SnapshotError, _git, check_commit


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


def _numstat(repo, sha):
    done = _git(repo, "diff", "--no-ext-diff", "--numstat", "-z", "-M", f"{sha}^1", sha)
    if done.returncode != 0:
        # a bad repository or ref gets the same lines as snapshot; any other failure keeps git's own text
        check_commit(repo, sha)
        raise SnapshotError(done.stderr.decode().strip())
    return done.stdout


def changed_files(repo, sha):
    return parse_numstat(_numstat(repo, sha))


def parse_renames(raw):
    # the same fields as parse_numstat: a rename row has an empty path, then the old and new paths
    fields = raw.split(b"\x00")
    end = len(fields) - 1
    renames = []
    i = 0
    while i < end:
        path = fields[i].split(b"\t", 2)[2]
        i += 1
        if path == b"":
            renames.append(
                (
                    fields[i].decode("utf-8", errors="surrogateescape"),
                    fields[i + 1].decode("utf-8", errors="surrogateescape"),
                )
            )
            i += 2
    return renames


def commit_changes(repo, sha):
    raw = _numstat(repo, sha)
    return parse_numstat(raw), parse_renames(raw)
