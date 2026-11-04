CREATE TABLE commits (
    sha TEXT PRIMARY KEY,
    position INTEGER NOT NULL UNIQUE,
    parent_count INTEGER NOT NULL,
    subject TEXT NOT NULL,
    committed_at TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('merge', 'direct')),
    pr_number INTEGER NULL,
    subject_number INTEGER NULL,
    subject_owner TEXT NULL,
    subject_branch TEXT NULL
);

CREATE TABLE prs (
    number INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    head_ref TEXT NOT NULL,
    base_ref TEXT NOT NULL,
    merge_oid TEXT NULL,
    merged_at TEXT NULL
);
