"""The page's HTML: a shell around the data, which sits in one JSON element, and one section per step."""

import html
import json

NOTE = (
    "Flags are unverified: their rules have not been judged on a history they were "
    "not fitted to."
)

# The graph's classes come from svg.py; the colours are the flowchart defaults of the
# Mermaid look the timeline page follows.
CSS = """
body { font-family: sans-serif; max-width: 60em; margin: 1em auto; padding: 0 1em; }
nav { margin: 1em 0; }
nav button { margin-right: 0.5em; }
.note { color: #555; }
.module rect { fill: #ECECFF; stroke: #9370DB; stroke-width: 1; }
.module text { fill: #333; font-family: "trebuchet ms", verdana, arial, sans-serif; font-size: 14px; }
.import path { stroke: #333333; stroke-width: 1; fill: none; }
#arrow path { fill: #333333; }
.module.added rect { fill: #D4F7D4; stroke: #2E8B57; }
.removed { opacity: 0.4; }
.module.removed rect, .import.removed path { stroke-dasharray: 4 3; }
.module.cycle rect, .import.cycle path { stroke: #D33; stroke-width: 2; }
"""

# Plain script, no src and no link: the page has to open from disk with nothing fetched.
SCRIPT = """
var sections = document.querySelectorAll("section.step");
var counter = document.getElementById("counter");
var index = 0;
function show(i) {
  if (sections.length === 0) return;
  index = Math.max(0, Math.min(i, sections.length - 1));
  sections.forEach(function (s, j) { s.hidden = (j !== index); });
  counter.textContent = (index + 1) + " / " + sections.length;
}
document.getElementById("prev").addEventListener("click", function () { show(index - 1); });
document.getElementById("next").addEventListener("click", function () { show(index + 1); });
document.addEventListener("keydown", function (e) {
  if (e.key === "ArrowLeft") show(index - 1);
  if (e.key === "ArrowRight") show(index + 1);
});
"""


def esc(value):
    # PR titles and bodies are not trusted markup, so every text value is escaped.
    return html.escape(str(value))


def render(data, graphs=None):
    # PR text could otherwise end the script element, or open an HTML comment inside it.
    text = json.dumps(data, sort_keys=True, indent=2).replace("<", "\\u003c") + "\n"
    steps = data["steps"]
    n = len(steps)
    nav = (
        '<nav><button id="prev" type="button">Previous</button>'
        '<button id="next" type="button">Next</button>'
        f'<span id="counter">{min(1, n)} / {n}</span></nav>\n'
    )
    parts = [
        "<!doctype html>\n<html>\n<head>\n",
        '<meta charset="utf-8">\n<title>Bearing</title>\n',
        "<style>" + CSS + "</style>\n",
        "</head>\n<body>\n",
        '<script id="bearing-data" type="application/json">',
        text,
        "</script>\n",
        '<p class="note">' + NOTE + "</p>\n",
        nav,
    ]
    for i, step in enumerate(steps, 1):
        # Only the first step is shown until the script runs; the rest wait in the file.
        hidden = "" if i == 1 else " hidden"
        heading = [f"Step {i} of {n}", esc(step["date"])]
        if step["number"] is not None:
            heading.append(f"#{esc(step['number'])}")
        heading.append(esc(step["title"]))
        parts.append(f'<section class="step" data-sha="{esc(step["sha"])}"{hidden}>\n')
        parts.append("<h2>" + " · ".join(heading) + "</h2>\n")
        if step["paragraph"]:
            parts.append(f"<p>{esc(step['paragraph'])}</p>\n")
        if step["events"]:
            items = "".join(f"<li>{esc(event)}</li>" for event in step["events"])
            parts.append(f'<ul class="events">{items}</ul>\n')
        if step["flags"]:
            # Flags are shown as claims to check, never as verdicts.
            items = "".join(
                '<li class="flag">'
                + esc(
                    f"unverified: {flag['rule']}: {flag['claim']} "
                    f"({', '.join(flag['files'])})"
                )
                + "</li>"
                for flag in step["flags"]
            )
            parts.append(f'<ul class="flags">{items}</ul>\n')
        if graphs is not None:
            # The graph is SVG markup from svg.py, so it is inserted as it is.
            parts.append(graphs[i - 1])
        parts.append("</section>\n")
    parts.append("<script>" + SCRIPT + "</script>\n")
    parts.append("</body>\n</html>\n")
    return "".join(parts)
