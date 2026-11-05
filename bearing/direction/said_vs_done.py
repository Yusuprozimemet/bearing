"""Checks what a pull request says about contract impact and its area against the files it changed."""

import re

from bearing.ingest.text import area


def says_no_contract_impact(body):
    if not body:
        return False
    lines = [line.strip() for line in body.replace("\r\n", "\n").split("\n")]
    for i, line in enumerate(lines):
        # a heading whose first non-blank line after it starts with "none"
        heading = re.match(r"#{1,6} (.*)$", line)
        if heading and heading.group(1).strip().lower() == "contract impact":
            following = [text for text in lines[i + 1 :] if text]
            if following and re.match(r"none\b", following[0], re.IGNORECASE):
                return True
        if re.match(r"contract impact:\s*none\b", line, re.IGNORECASE):
            return True
    return False


def said_vs_done(prs, areas, rules):
    prefixes_of = dict(areas)
    flags = []
    for number, branch, body, paths in prs:
        for rule_id, prefixes in rules:
            if rule_id == "outside-area":
                # a branch without "/" has no area to be outside of
                if not branch or "/" not in branch:
                    continue
                name = area(branch)
                if name not in prefixes_of:
                    continue
                # read against the branch's own area, not area_of: an earlier area may match too
                files = sorted(p for p in paths if not p.startswith(prefixes_of[name]))
                if files:
                    flags.append((number, rule_id, f"area {name}", files))
            elif rule_id == "contract-impact":
                files = sorted(p for p in paths if p.startswith(prefixes))
                if files and says_no_contract_impact(body):
                    flags.append((number, rule_id, "no contract impact", files))
    return flags
