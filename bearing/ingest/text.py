"""Reading a branch's area and the paragraph a PR body gives for the changelog."""

import re

HEADING = re.compile(r"^#{1,6} ")


def area(branch):
    # The area is the part of the branch name before its first "/"; a branch without one has no area.
    if not branch or "/" not in branch:
        return "other"
    return branch.split("/", 1)[0]


def what_i_built(body):
    # gh and the template write CRLF; rstrip keeps trailing spaces out of the joined text.
    lines = [line.rstrip() for line in (body or "").replace("\r\n", "\n").split("\n")]
    for start, line in enumerate(lines):
        if HEADING.match(line) and HEADING.sub("", line).strip() == "What I built":
            end = next(
                (i for i in range(start + 1, len(lines)) if HEADING.match(lines[i])),
                len(lines),
            )
            section = _paragraph(lines[start + 1 : end])
            if section:
                return section
            break
    # No section, or an empty one: fall back to the body's first paragraph, so a PR is never missing.
    return _paragraph(lines)


def _paragraph(lines):
    # The first run of lines that are neither blank nor headings; "" when there is none.
    run = []
    for line in lines:
        if not line or HEADING.match(line):
            if run:
                break
        else:
            run.append(line)
    return "\n".join(run)
