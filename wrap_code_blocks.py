#!/usr/bin/env python3
"""Step 2a of the PPTX->HTML lecture pipeline: replace contiguous C# code
paragraphs in a lecture HTML page with an inline `.pseudo-panel` (not wrapped
in a collapsible <details>), styled exactly like the tutorial pseudocode
panels (site.js `enhancePseudoPanels` output / .pseudo-panel CSS in
site.css), instead of relying on the runtime auto-detection (which only
triggers on literal "pseudo code:" headings).

Usage: python wrap_code_blocks.py [site/pages/lect-XX.html]
"""
import re
import sys
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent / "site" / "pages" / "lect-02b-03b.html"

P_RE = re.compile(r'^\s*<p>(.*)</p>\s*$')

CALL_RE = re.compile(r'\w+\s*\([^)]*\)\s*;')
FUNC_SIG_RE = re.compile(r'^\w+\s*\([^)]*\)\s*$')
KEYWORD_RE = re.compile(r'^(class|public|private|static|void|using)\b')
CONTROL_RE = re.compile(r'^(for|foreach|while|if|else|switch|case)\b', re.IGNORECASE)
STATEMENT_RE = re.compile(
    r'^(using |public |private |protected |internal |class |void |if\b|else\b|for\b|while\b|return\b)',
    re.IGNORECASE,
)


def is_code(text: str) -> bool:
    t = text.strip()
    if t in ("{", "}"):
        return True
    if t.startswith("//"):
        return True
    if re.search(r'MessageBox\.Show|Console\.Write', t):
        return True
    if CALL_RE.search(t) or FUNC_SIG_RE.match(t):
        return True
    if KEYWORD_RE.match(t) or CONTROL_RE.match(t):
        if len(t) > 70 and ";" not in t and "{" not in t and "}" not in t:
            return False
        return True
    if t.endswith(";"):
        return True
    return False


def build_pseudo_panel(run):
    """Render `run` (list of raw line texts) as a .pseudo-panel matching
    site.js's enhancePseudoPanels output structure."""
    out = [
        '    <section class="pseudo-panel pseudo-panel--compact">',
        '      <div class="pseudo-panel__chrome">',
        '        <div class="pseudo-panel__dots">',
        '          <span class="pseudo-panel__dot"></span>',
        '          <span class="pseudo-panel__dot"></span>',
        '          <span class="pseudo-panel__dot"></span>',
        '        </div>',
        '        <div class="pseudo-panel__title">Code Example</div>',
        '      </div>',
        '      <div class="pseudo-panel__body" role="region" aria-label="Code Example">',
    ]

    indent_level = 0
    for raw in run:
        text = raw.strip()

        if text.startswith("}"):
            indent_level = max(0, indent_level - 1)

        if text.startswith("//"):
            tone = "comment"
        elif re.match(r'^[{}]+$', text):
            tone = "brace"
        elif STATEMENT_RE.match(text):
            tone = "statement"
        else:
            tone = "code"

        out.append(
            f'        <div class="pseudo-panel__line pseudo-panel__line--{tone}" '
            f'style="--pseudo-indent-level: {indent_level}">{text}</div>'
        )

        if text.endswith("{"):
            indent_level += 1

    out.append('      </div>')
    out.append('    </section>')
    return out


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    lines = path.read_text(encoding="utf-8").split("\n")
    out = []
    i = 0
    wrapped_count = 0

    while i < len(lines):
        m = P_RE.match(lines[i])
        if m and is_code(m.group(1)):
            run = []
            while i < len(lines):
                m2 = P_RE.match(lines[i])
                if m2 and is_code(m2.group(1)):
                    run.append(m2.group(1))
                    i += 1
                else:
                    break

            out.extend(build_pseudo_panel(run))
            wrapped_count += 1
            continue

        out.append(lines[i])
        i += 1

    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrapped {wrapped_count} code block(s) in {path}.")


if __name__ == "__main__":
    main()
