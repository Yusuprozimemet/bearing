"""A cache of each blob's line count and imports, kept in the store so that a blob is parsed once for all snapshots."""

import json

from bearing.snapshot.modules import count_lines, parse_imports


class BlobCache:
    def __init__(self, conn):
        self.conn = conn
        self.parsed = 0
        self.hits = 0
        # A blob counts as parsed or as a hit once per cache, however many snapshots ask for it.
        self._seen = set()

    def get(self, sha, read):
        row = self.conn.execute(
            "SELECT lines, imports FROM blobs WHERE sha = ?", (sha,)
        ).fetchone()
        if row is None:
            data = read()
            lines = count_lines(data)
            imports = parse_imports(data)
            self.conn.execute(
                "INSERT INTO blobs (sha, lines, imports) VALUES (?, ?, ?)",
                (sha, lines, None if imports is None else json.dumps(imports)),
            )
            if sha not in self._seen:
                self.parsed += 1
        else:
            lines, text = row
            if sha not in self._seen:
                self.hits += 1
            # JSON has no tuples: the rows are rebuilt as the parser returns them.
            imports = (
                None
                if text is None
                else [
                    (level, module, tuple(names))
                    for level, module, names in json.loads(text)
                ]
            )
        self._seen.add(sha)
        return lines, imports
