"""One step's import graph as an inline SVG: a box per module, an arrow per import."""

import html
from collections import Counter

from bearing.page.layout import components, layers

BOX_HEIGHT = 32
WRAP = 960
MARGIN = 16

ARROW = (
    '<defs><marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" '
    'markerWidth="8" markerHeight="8" orient="auto">'
    '<path d="M0,0 L10,5 L0,10 z"/></marker></defs>'
)


def draw(old, new, events):
    # old is not read: what the step removed is named by its events, and new holds the rest.
    added_modules = _names(events, "+module ")
    removed_modules = _names(events, "-module ")
    added_imports = _pairs(events, "+import ")
    removed_imports = _pairs(events, "-import ")

    modules = {module["name"] for module in new["modules"]} | removed_modules
    imports = {tuple(pair) for pair in new["imports"]} | removed_imports
    imports = sorted(p for p in imports if p[0] in modules and p[1] in modules)

    comp = components([module["name"] for module in new["modules"]], new["imports"])
    size = Counter(comp.values())

    def in_cycle(name):
        return name in comp and size[comp[name]] > 1

    rows = layers(sorted(modules), imports)
    boxes = _place(rows)
    where = {name: (x, y, width) for name, x, y, width in boxes}
    if boxes:
        width = max(x + w for _, x, _, w in boxes) + MARGIN
        height = max(y + BOX_HEIGHT for _, _, y, _ in boxes) + MARGIN
    else:
        width = height = BOX_HEIGHT

    head = (
        f'<svg class="graph" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    lines = [head, ARROW]
    for importer, imported in imports:
        x1, y1, w1 = where[importer]
        x2, y2, w2 = where[imported]
        both = in_cycle(importer) and in_cycle(imported)
        cls = _classes(
            "import",
            (importer, imported),
            added_imports,
            removed_imports,
            both and comp[importer] == comp[imported],
        )
        start = f"{_num(x1 + w1 / 2)},{_num(y1 + BOX_HEIGHT)}"
        end = f"{_num(x2 + w2 / 2)},{_num(y2)}"
        lines.append(
            f'<g class="{cls}" data-from="{html.escape(importer)}" '
            f'data-to="{html.escape(imported)}">'
            f'<path d="M{start} L{end}" marker-end="url(#arrow)"/></g>'
        )
    for name, x, y, w in boxes:
        cls = _classes("module", name, added_modules, removed_modules, in_cycle(name))
        escaped = html.escape(name)
        lines.append(
            f'<g class="{cls}" data-name="{escaped}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{BOX_HEIGHT}" rx="5" ry="5"/>'
            f'<text x="{_num(x + w / 2)}" y="{y + 21}" text-anchor="middle">{escaped}</text>'
            "</g>"
        )
    lines.append("</svg>")
    return "\n".join(lines)


def _place(rows):
    # Boxes in drawing order, as (name, x, y, width). A row wraps before a box whose right
    # edge would pass WRAP, unless the box would start the row.
    boxes = []
    y = MARGIN
    for index, layer in enumerate(rows):
        if index:
            y += BOX_HEIGHT + 48
        x = MARGIN
        count = 0
        for name in layer:
            width = 8 * len(name) + 24
            if count and x + width > WRAP:
                x = MARGIN
                y += BOX_HEIGHT + 24
                count = 0
            boxes.append((name, x, y, width))
            x += width + 16
            count += 1
    return boxes


def _classes(base, key, added, removed, cycled):
    names = [base]
    if key in added:
        names.append("added")
    if key in removed:
        names.append("removed")
    if cycled and key not in removed:
        names.append("cycle")
    return " ".join(names)


def _names(events, prefix):
    return {line[len(prefix) :] for line in events if line.startswith(prefix)}


def _pairs(events, prefix):
    lines = [line[len(prefix) :] for line in events if line.startswith(prefix)]
    return {tuple(line.split(" -> ")) for line in lines}


def _num(value):
    return f"{value:g}"
