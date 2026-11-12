"""Reading a branch's area and the paragraph a PR body gives for the changelog."""

import re

HEADING = re.compile(r"^#{1,6} ")
# An end mark counts only before a space, tab, line feed or the end: "app.a" and "1.2" are not ends.
END = re.compile(r"[.!?](?=[ \t\n]|$)")


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
                return _two_sentences(section)
            break
    # No section, or an empty one: fall back to the body's first paragraph, so a PR is never missing.
    return _two_sentences(_paragraph(lines))


def _two_sentences(text):
    # The changelog gets two sentences: the text up to the second end mark; with fewer, all of it.
    ends = list(END.finditer(text))
    if len(ends) < 2:
        return text
    return text[: ends[1].end()].rstrip()


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
