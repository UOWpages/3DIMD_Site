#!/usr/bin/env python3
"""Unwrap pseudocode `<details class="accordion...">` sections in tutorial
pages so the pseudo-panel (built at runtime by site.js's
`enhancePseudoPanels`) renders inline instead of being hidden behind an extra
collapsible click. Where the removed wrapper had a `<summary>` naming the
section (e.g. a filename or task name), that name is appended to the
"Pseudo Code:" trigger heading so it carries over into the resulting panel's
title.

Usage: python unwrap_pseudocode_panels.py <site/pages/tut-XX.html> [...]
"""
import re
import sys
from pathlib import Path

DEFAULT_PATHS = [
    "site/pages/tut-00-01-student-version.html",
    "site/pages/tut-02-03-lecturer.html",
    "site/pages/tut-02-03-students.html",
    "site/pages/tut-04-students.html",
]

TRIGGER_RE = re.compile(r'^(pseudo\s*code:?|//\s*pseudo\s*code:?)', re.IGNORECASE)
TAG_TEXT_RE = re.compile(r'<(h2|h3|p)[^>]*>(.*?)</\1>', re.DOTALL)


def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def find_balanced(lines, start, open_tok, close_tok, first_line_depth=1):
    """Given lines[start] already contains one `open_tok`, find the index of
    the line where depth returns to 0 (counting open/close tokens per line,
    starting from `first_line_depth` after counting line[start] itself is
    assumed already applied by caller for cases where the opening line may
    also contain closes)."""
    depth = first_line_depth
    j = start + 1
    while j < len(lines) and depth > 0:
        depth += lines[j].count(open_tok) - lines[j].count(close_tok)
        if depth == 0:
            break
        j += 1
    return j


def extract_tag_span(lines, start_idx, open_re, close_literal):
    """Find a `<div ...>`-like opening at/after start_idx on a line matching
    open_re, then balance to its closing `close_literal` (e.g. '</div>').
    Returns (open_idx, close_idx) or None."""
    for i in range(start_idx, len(lines)):
        if open_re.search(lines[i]):
            depth = lines[i].count('<div') - lines[i].count('</div>')
            if depth <= 0:
                # opened and closed on the same line
                return (i, i)
            j = i + 1
            while j < len(lines) and depth > 0:
                depth += lines[j].count('<div') - lines[j].count('</div>')
                if depth == 0:
                    break
                j += 1
            return (i, j)
    return None


def get_first_tag_text(lines):
    joined = "\n".join(lines)
    m = TAG_TEXT_RE.search(joined)
    if not m:
        return ""
    return normalize(m.group(2))


def process_lines(lines):
    """Recursively unwrap qualifying pseudocode <details> blocks. Returns a
    new list of lines."""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if '<details' in line:
            depth = line.count('<details') - line.count('</details>')
            if depth <= 0:
                out.append(line)
                i += 1
                continue

            j = i + 1
            while j < n and depth > 0:
                depth += lines[j].count('<details') - lines[j].count('</details>')
                if depth == 0:
                    break
                j += 1

            block = lines[i:j + 1]

            # locate <summary>...</summary> within the block
            summary_text = ""
            summary_start = None
            for k, bl in enumerate(block):
                if '<summary>' in bl:
                    summary_start = k
                    break
            if summary_start is not None:
                summary_lines = []
                if '</summary>' in block[summary_start]:
                    summary_lines.append(block[summary_start])
                else:
                    k = summary_start
                    while k < len(block):
                        summary_lines.append(block[k])
                        if '</summary>' in block[k]:
                            break
                        k += 1
                joined = " ".join(summary_lines)
                m = re.search(r'<summary>(.*?)</summary>', joined, re.DOTALL)
                if m:
                    summary_text = normalize(m.group(1))

            # locate the accordion-body div and its inner content
            body_open_re = re.compile(r'<div class="accordion-body[^"]*">')
            span = extract_tag_span(block, 0, body_open_re, '</div>')

            if span is None:
                # not a plain accordion-body details block; recurse into it as-is
                out.extend([block[0]] + process_lines(block[1:-1]) + [block[-1]])
                i = j + 1
                continue

            body_open, body_close = span
            inner_before = block[:body_open + 1]
            inner_lines = block[body_open + 1:body_close]
            inner_after = block[body_close:]

            # recurse first so nested pseudocode details are handled too
            inner_lines = process_lines(inner_lines)

            first_text = get_first_tag_text(inner_lines)
            qualifies = bool(TRIGGER_RE.match(first_text))

            if not qualifies:
                out.extend(inner_before + inner_lines + inner_after)
                i = j + 1
                continue

            # append the section name to the trigger heading, if meaningful
            clean_name = TRIGGER_RE.sub("", summary_text).strip(" :")
            trigger_norm = normalize(first_text).rstrip(':').strip().lower()
            name_norm = clean_name.rstrip(':').strip().lower()
            should_append = bool(clean_name) and name_norm != trigger_norm and \
                name_norm not in trigger_norm

            if should_append:
                for idx, bl in enumerate(inner_lines):
                    m = re.search(r'^(\s*)<h3>(.*?)</h3>\s*$', bl)
                    if m and TRIGGER_RE.match(normalize(m.group(2))):
                        new_text = f"{m.group(2).rstrip(':').strip()}: {clean_name}"
                        inner_lines[idx] = f"{m.group(1)}<h3>{new_text}</h3>"
                        break

            out.extend(inner_lines)
            i = j + 1
            continue

        out.append(line)
        i += 1
    return out


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_PATHS
    repo_root = Path(__file__).parent

    for arg in args:
        path = Path(arg)
        if not path.is_absolute():
            path = repo_root / path
        lines = path.read_text(encoding="utf-8").split("\n")
        new_lines = process_lines(lines)
        path.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"Processed {path}")


if __name__ == "__main__":
    main()
