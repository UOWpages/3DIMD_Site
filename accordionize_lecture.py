#!/usr/bin/env python3
"""Step 2b of the PPTX->HTML lecture pipeline: accordion-ize a structurally
converted lecture page (output of build_*.py + wrap_code_blocks.py, i.e.
Step 2a) into the lect-01a/01b visual/interaction style.

Usage: python accordionize_lecture.py [site/pages/lect-XX.html]

Step 1 (extract_pptx.py + build_*.py) produces plain slides:
    <div class="slide-content">
      <h2>Heading</h2>
      <h3>Sub heading:</h3>
      <p>...</p>
      ...
    </div>

Step 2 (this script) groups each slide's content into collapsible sections
keyed by its own h2/h3 headings, matching lect-01a/01b:
    <div class="slide-content slide-content-accordion">
      <h2>Heading</h2>
      <div class="accordion-scroll">
        <details class="accordion" open>
          <summary>Sub heading</summary>
          <div class="accordion-body">
            <h3>Sub heading:</h3>
            <p>...</p>
          </div>
        </details>
        ...
      </div>
    </div>

This also gives the slide body the same font sizing as lect-01a/01b for free,
since that sizing lives on `.slide-content .accordion-body p/li/a` in
slideshow.css rather than on plain `.slide-content p`.
"""
import re
import sys
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent / "site" / "pages" / "lect-02b-03b.html"

H2_RE = re.compile(r'<h2>(.*?)</h2>')
H3_RE = re.compile(r'<h3>(.*?)</h3>')


def find_slide_content_blocks(lines):
    """Return list of (start_idx, end_idx) for each top-level
    <div class="slide-content..."> ... </div> block (end_idx is the line
    index of the matching closing </div>), using div-depth balancing so
    nested accordion-body/pseudo-panel divs don't confuse the boundary."""
    blocks = []
    i = 0
    while i < len(lines):
        if re.match(r'^\s*<div class="slide-content[^"]*">\s*$', lines[i]):
            start = i
            depth = 1
            j = i + 1
            while j < len(lines) and depth > 0:
                depth += lines[j].count("<div") - lines[j].count("</div>")
                if depth == 0:
                    break
                j += 1
            blocks.append((start, j))
            i = j + 1
        else:
            i += 1
    return blocks


def parse_nodes(body_lines):
    nodes = []
    i = 0
    n = len(body_lines)
    while i < n:
        stripped = body_lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("<ul>"):
            block = [body_lines[i]]
            i += 1
            while i < n and not body_lines[i].strip().startswith("</ul>"):
                block.append(body_lines[i])
                i += 1
            if i < n:
                block.append(body_lines[i])
                i += 1
            nodes.append({"type": "ul", "lines": block})
        elif stripped.startswith("<details"):
            block = [body_lines[i]]
            depth = stripped.count("<details") - stripped.count("</details>")
            i += 1
            while i < n and depth > 0:
                depth += body_lines[i].count("<details") - body_lines[i].count("</details>")
                block.append(body_lines[i])
                i += 1
            nodes.append({"type": "details", "lines": block})
        elif stripped.startswith("<h2>"):
            nodes.append({"type": "h2", "lines": [body_lines[i]]})
            i += 1
        elif stripped.startswith("<h3>"):
            nodes.append({"type": "h3", "lines": [body_lines[i]]})
            i += 1
        elif stripped.startswith("<img"):
            nodes.append({"type": "img", "lines": [body_lines[i]]})
            i += 1
        else:
            nodes.append({"type": "p", "lines": [body_lines[i]]})
            i += 1
    return nodes


def strip_label(text: str) -> str:
    return text.strip().rstrip(":").strip().strip('"\u201c\u201d')


def infer_label_from_h2(h2_text: str) -> str:
    paren = re.search(r"\(([^)]+)\)\s*$", h2_text)
    if paren:
        return paren.group(1).strip()
    clean = h2_text.rstrip(":").strip()
    if clean and len(clean) <= 40:
        return clean
    return "Overview"


def accordionize_slide(body_lines):
    """Return new list of body lines, or None if there's nothing worth
    wrapping (e.g. a bare title/divider slide)."""
    nodes = parse_nodes(body_lines)
    if not nodes:
        return None

    h2_node = nodes[0] if nodes[0]["type"] == "h2" else None
    rest = nodes[1:] if h2_node else nodes[:]

    citation_node = None
    if rest and rest[0]["type"] == "p" and "slide-citation" in rest[0]["lines"][0]:
        citation_node = rest.pop(0)

    if not rest:
        return None

    sections = []
    current = None
    for node in rest:
        if node["type"] == "h3":
            if current is not None:
                sections.append(current)
            m = H3_RE.search(node["lines"][0])
            label = strip_label(m.group(1)) if m else "Details"
            current = {"label": label, "nodes": [node]}
        else:
            if current is None:
                current = {"label": None, "nodes": []}
            current["nodes"].append(node)
    if current is not None:
        sections.append(current)

    if not sections:
        return None

    if sections[0]["label"] is None:
        h2_text = H2_RE.search(h2_node["lines"][0]).group(1) if h2_node else ""
        sections[0]["label"] = infer_label_from_h2(h2_text)

    out = []
    if h2_node:
        out.extend(h2_node["lines"])
    if citation_node:
        out.extend(citation_node["lines"])

    out.append('    <div class="accordion-scroll">')
    for idx, sec in enumerate(sections):
        open_attr = " open" if idx == 0 else ""
        out.append(f'      <details class="accordion"{open_attr}>')
        out.append(f'        <summary>{sec["label"]}</summary>')
        out.append('        <div class="accordion-body">')
        for node in sec["nodes"]:
            out.extend(node["lines"])
        out.append("        </div>")
        out.append("      </details>")
    out.append("    </div>")
    return out


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    lines = path.read_text(encoding="utf-8").split("\n")

    blocks = find_slide_content_blocks(lines)

    final = []
    prev_end = 0
    converted = 0
    skipped = 0

    for start, end in blocks:
        final.extend(lines[prev_end:start])
        body_lines = lines[start + 1:end]
        new_body = accordionize_slide(body_lines)
        if new_body is None:
            final.extend(lines[start:end + 1])
            skipped += 1
        else:
            final.append('    <div class="slide-content slide-content-accordion">')
            final.extend(new_body)
            final.append(lines[end])
            converted += 1
        prev_end = end + 1

    final.extend(lines[prev_end:])

    path.write_text("\n".join(final), encoding="utf-8")
    print(f"Accordion-ized {converted} slide(s), left {skipped} bare (no body content).")


if __name__ == "__main__":
    main()
