"""Build lect-07-unity-ui.html with consolidated (theme-grouped) slides.

Source of truth is lect-07-unity-ui-content.json (extract_pptx.py output) plus
the PPTX run-level hyperlinks and speaker notes, which the extractor does not
capture and are recorded below. The PLAN maps every source slide (1-34) onto
a smaller set of themed slides; see docs/lecture-conversion-playbook.md.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
JSON_PATH = PAGES / "lect-07-unity-ui-content.json"
OUT_PATH = PAGES / "lect-07-unity-ui.html"
FOOTER_SOURCE = PAGES / "lect-04a-report.html"

SLIDE_TITLE = "3D Interactive Media Development"
PAGE_TITLE = "3DIMD | Lecture 07 - Unity UI"

data = {s["slide_number"]: s for s in json.load(JSON_PATH.open(encoding="utf-8"))}

# Noorcon PDFs: Parts 4/6/9 use the replacement links curated in lect-05a;
# Parts 2/3 use the hyperlinks embedded in the Lecture 07 PPTX.
SP = "https://universityofwestminster-my.sharepoint.com/:b:/g/personal/fergusj_westminster_ac_uk/"
NOORCON_PDF = {
    "2": SP + "EccvkNJwsmRJr1UxMpOKrDkBvF-AdAUJgRe0-Jk1PuvHpw?e=CEqGU7",
    "3": SP + "Ea-HT389bR5ApI4Hvry5xwUBuf3kgrrejueN-yHc8XhFMA?e=58N7AI",
    "4": SP + "IQDlfyn-TwZlSrtdyrZwVWk6AaUZfBaI8mAqxAwrV2yWUY0?e=BPtDrb",
    "6": SP + "IQDL7ziFEPxRRbOrjE77YOwsAYFjqNQw-kV8MTRphxhgToA?e=YwNsEk",
    "9": SP + "IQDyd8ffCVnBRZq2D95pOVReAVhNyLORYnrS7k9CuQzQYW8?e=oR4KtY",
}
STRING_FORMAT_NOTE = "String format shows P for position, R for rotation, and 3 values to 2 floating point value…."


def lines(num):
    """Cleaned (depth, text) lines for a source slide; depth = tab/em-space indent."""
    out = []
    for block in data[num]["content"]:
        for ln in block.replace("\x0b", "\n").split("\n"):
            lead = re.match(r"^[\t\u2003\xa0 ]*", ln).group(0)
            depth = lead.count("\t") + lead.count("\u2003")
            text = re.sub(r"\s+", " ", ln.replace("\xa0", " ").replace("\u2003", " ").replace("\t", " ")).strip()
            if text:
                out.append((depth, text))
    return out


def esc(text):
    return html.escape(text, quote=False)


def pdf_link(part):
    label = f"Noorcon Inc. - Unity 3D Game Programming Part {part} - Vahe Karamian (PDF)"
    return f'<a href="{html.escape(NOORCON_PDF[part])}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


NOORCON_RE = re.compile(r"Noorcon Inc\. - Unity 3D Game Programming Part (\d) - Vahe Karamian\.pdf")


def inline(text):
    """Escape a source line, turning Noorcon PDF titles into their document links."""
    parts = []
    last = 0
    for m in NOORCON_RE.finditer(text):
        parts.append(esc(text[last:m.start()]))
        parts.append(pdf_link(m.group(1)))
        last = m.end()
    parts.append(esc(text[last:]))
    return "".join(parts)


# ---------- block renderers (each returns list of lines at given indent) ----------

def r_paras(num, start, end, pad):
    return [f"{pad}<p>{inline(t)}</p>" for _, t in lines(num)[start:end]]


def r_tree(num, start, end, pad):
    """Nested <ul> from source indent depth (relative to the first line)."""
    items = lines(num)[start:end]
    base = min(d for d, _ in items)
    out, prev = [], -1
    for depth, text in items:
        level = max(0, min(depth - base, prev + 1))
        if level > prev:
            out.append(f"{pad}{'  ' * level}<ul>")
        else:
            if level < prev:
                for closing in range(prev, level, -1):
                    out.append(f"{pad}{'  ' * closing}</li></ul>")
            out.append(f"{pad}{'  ' * level}</li>")
        out.append(f"{pad}{'  ' * level}<li>{inline(text)}")
        prev = level
    for closing in range(prev, -1, -1):
        out.append(f"{pad}{'  ' * closing}</li></ul>")
    return out


STATEMENT_RE = re.compile(r"^(using |public |private |protected |class |void |if\b|else\b|for\b|while\b|return\b)")


def r_code(code_lines, pad, title="Code Example"):
    out = [
        f'{pad}<section class="code-panel code-panel--compact" data-code-type="code">',
        f'{pad}  <div class="code-panel__chrome">',
        f'{pad}    <div class="code-panel__dots">',
        f'{pad}      <span class="code-panel__dot"></span>',
        f'{pad}      <span class="code-panel__dot"></span>',
        f'{pad}      <span class="code-panel__dot"></span>',
        f"{pad}    </div>",
        f'{pad}    <div class="code-panel__title">{esc(title)}</div>',
        f"{pad}  </div>",
        f'{pad}  <div class="code-panel__body" role="region" aria-label="{html.escape(title)}">',
    ]
    level = 0
    continuation = False
    for text in code_lines:
        if text.startswith("}"):
            level = max(0, level - 1)
        if text.startswith("//"):
            tone = "comment"
        elif re.fullmatch(r"[{}]+", text):
            tone = "brace"
        elif STATEMENT_RE.match(text):
            tone = "statement"
        else:
            tone = "code"
        shown = min(6, level + (1 if continuation else 0))
        out.append(f'{pad}    <div class="code-panel__line code-panel__line--{tone} indent-level-{shown}">{esc(text)}</div>')
        if text.endswith("{"):
            level += 1
        continuation = text.endswith(",")
    out += [f"{pad}  </div>", f"{pad}</section>"]
    return out


def code_from(num, start, end):
    return [t for _, t in lines(num)[start:end]]


def r_images(imgs, pad):
    out = [f'{pad}<div class="accordion-images--horizontal" style="--accordion-images--horizontal-width: 100%;">']
    for num, idx, width, alt in imgs:
        src = html.escape(data[num]["images"][idx]["path"], quote=True)
        out.append(
            f'{pad}  <img src="{src}" class="accordion-image" alt="{html.escape(alt, quote=True)}"'
            f' style="--accordion-image-width: {width};" />'
        )
    out.append(f"{pad}</div>")
    return out


def r_video(video_id, summary, watch_url, pad):
    s = esc(summary)
    return [
        f'{pad}<details class="accordion accordion--nested embed-accordion">',
        f"{pad}  <summary>Video: {s}</summary>",
        f'{pad}  <div class="accordion-body">',
        f'{pad}    <article class="embed-card">',
        f'{pad}      <iframe class="video-embed" src="https://www.youtube.com/embed/{video_id}" title="{html.escape(summary)} video"'
        ' loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>',
        f'{pad}      <p><a href="{html.escape(watch_url)}" target="_blank" rel="noopener noreferrer">Open source link</a></p>',
        f"{pad}    </article>",
        f"{pad}  </div>",
        f"{pad}</details>",
    ]


def r_nested(summary, inner, pad):
    return [
        f'{pad}<details class="accordion accordion--nested">',
        f"{pad}  <summary>{esc(summary)}</summary>",
        f'{pad}  <div class="accordion-body">',
        *inner,
        f"{pad}  </div>",
        f"{pad}</details>",
    ]


def r_tutlink(page, label, pad):
    return [f'{pad}<p><a href="../index.html?page=pages/{page}" target="_top">{esc(label)}</a></p>']


def render_block(block, pad):
    kind = block[0]
    if kind == "p":                      # ("p", slide, start, end)
        return r_paras(block[1], block[2], block[3], pad)
    if kind == "text":                   # ("text", literal html-safe text)
        return [f"{pad}<p>{inline(block[1])}</p>"]
    if kind == "label":                  # ("label", heading text) -> h3
        return [f"{pad}<h3>{esc(block[1])}</h3>"]
    if kind == "tree":                   # ("tree", slide, start, end)
        return r_tree(block[1], block[2], block[3], pad)
    if kind == "code":                   # ("code", slide, start, end[, title])
        return r_code(code_from(block[1], block[2], block[3]), pad, *(block[4:5] or ["Code Example"]))
    if kind == "img":                    # ("img", [(slide, idx, width, alt), ...])
        return r_images(block[1], pad)
    if kind == "video":                  # ("video", id, summary, watch_url)
        return r_video(block[1], block[2], block[3], pad)
    if kind == "pdf":                    # ("pdf", part)
        return [f"{pad}<p>{pdf_link(block[1])}</p>"]
    if kind == "tut":                    # ("tut", page, label)
        return r_tutlink(block[1], block[2], pad)
    if kind == "nested":                 # ("nested", summary, [blocks])
        inner = []
        for b in block[2]:
            inner.extend(render_block(b, pad + "    "))
        return r_nested(block[1], inner, pad)
    raise ValueError(kind)


# ---------- consolidation plan: 34 source slides -> 10 themed slides ----------
# section: dict(s=summary, src=[source slides], b=[blocks])
PLAN = [
    {"h2": "5MMCS001W Lecture 07 - Unity UI", "src": "1-2", "sections": [
        {"s": "Interactive 3D Web Example — Blend4Web Dairy Plant", "src": [1], "b": [
            ("p", 1, 0, 1),
        ]},
        {"s": "Troubleshooting", "src": [2], "b": [
            ("tree", 2, 0, 2),
            ("tut", "tut-02-unity-packages.html", "Tutorial 02: Unity Packages"),
        ]},
    ]},
    {"h2": "Unity Input Manager", "src": "3-5", "sections": [
        {"s": "Inputs, Outputs and the Input Manager", "src": [3], "b": [
            ("p", 3, 0, 3),
            ("tree", 3, 3, 6),
            ("p", 3, 6, 7),
        ]},
        {"s": "Input Manager - Also Tutorial 2-3", "src": [4], "b": [
            ("img", [(4, 0, "32%", "Unity Inspector showing the InputManager Axes list"),
                     (4, 1, "32%", "Unity InputManager axis configuration screenshot"),
                     (4, 2, "32%", "Unity InputManager axis configuration screenshot")]),
        ]},
        {"s": "Horizontal Axis Properties – Tut 7.1", "src": [5], "b": [
            ("p", 5, 0, 2),
            ("tree", 5, 2, 9),
            ("img", [(5, 0, "40%", "InputManager Horizontal axis expanded with its properties highlighted")]),
        ]},
        {"s": "Related Tutorials", "src": [], "b": [
            ("tut", "tut-02-03-students.html", "Tutorials 02–03: Input concepts, exercises and stretch tasks"),
        ]},
    ]},
    {"h2": "Input Scripting - Rotation, Movement and Animator", "src": "6-8", "sections": [
        {"s": "Keyboard Rotation of Primitives – Tut 7.1", "src": [6], "b": [
            ("p", 6, 1, 2),
            ("tree", 6, 2, 5),
            ("p", 6, 5, 8),
        ]},
        {"s": "Unity Input Manager/Movement Scripting – Tut 7.1", "src": [7], "b": [
            ("p", 7, 1, 2),
            ("code", 7, 2, 13, "CreatePrimitivesFromImport.cs"),
            ("pdf", "4"),
        ]},
        {"s": "Unity Animator Scripting - Tut 5", "src": [8], "b": [
            ("tree", 8, 1, 6),
            ("video", "H9Ptme4fYR0", "Tutorial 08 01 — Animator scripting walkthrough", "https://www.youtube.com/watch?v=H9Ptme4fYR0"),
            ("tut", "tut-05.html", "Tutorial 05: Animator and input-triggered animation"),
        ]},
    ]},
    {"h2": "Unity UI Architecture - Namespace and Canvas", "src": "9-11", "sections": [
        {"s": "UnityEngine.UI Namespace", "src": [9, 10], "b": [
            ("p", 10, 0, 1),
            ("tree", 10, 1, 7),
        ]},
        {"s": "Canvas – Base component of UI", "src": [11], "b": [
            ("code", 11, 0, 1, "Namespace"),
            ("tree", 11, 1, 11),
        ]},
    ]},
    {"h2": "Unity UI Architecture - Event System and Event Firing", "src": "12-13", "sections": [
        {"s": "Event System - Game Object", "src": [12], "b": [
            ("p", 12, 0, 1),
            ("code", 12, 1, 2, "Namespace"),
            ("tree", 12, 2, 8),
        ]},
        {"s": "Determine Event Firing for UI", "src": [12, 13], "b": [
            ("tree", 12, 8, 13),
            ("p", 12, 13, 15),
        ]},
        {"s": "Wiring Functions to Events – Tut 7.1b (extra)", "src": [13], "b": [
            ("tree", 13, 8, 13),
        ]},
    ]},
    {"h2": "Unity UI Architecture - Text and Button Elements", "src": "14-16", "sections": [
        {"s": "Text – most fundamental UI element", "src": [14], "b": [
            ("p", 14, 0, 1),
            ("tree", 14, 1, 9),
            ("p", 14, 9, 10),
        ]},
        {"s": "Button – most Common UI element", "src": [15], "b": [
            ("p", 15, 0, 1),
            ("tree", 15, 1, 14),
        ]},
        {"s": "Basics", "src": [16], "b": [
            ("p", 16, 0, 1),
            ("label", "HUD Text Readout from Script Public Variable"),
            ("p", 16, 3, 4),
            ("label", "Button OnClick Event Handling (Associated Functions must be public and void)"),
            ("p", 16, 5, 6),
            ("label", "Button Runtime text feedback"),
            ("p", 16, 7, 8),
        ]},
    ]},
    {"h2": "Tutorial 7 Unity UI HUD - Overview and Scene Setup", "src": "17-19", "sections": [
        {"s": "Tutorial 1. Unity UI HUD", "src": [17], "b": [
            ("label", "Initialize Cubes (with rotation)"),
            ("p", 17, 1, 2),
            ("label", "Initialize more Cubes from Button (4.2)"),
            ("p", 17, 3, 5),
            ("label", "Animate rotation from key"),
            ("p", 17, 6, 8),
            ("label", "HUD Text Readouts in Unity UI Text and Panels (from Script Public Variable)"),
            ("p", 17, 9, 10),
        ]},
        {"s": "Tutorial 7 Unity UI HUD — Contents", "src": [18], "b": [
            ("p", 18, 0, 2),
            ("tree", 18, 2, 12),
        ]},
        {"s": "Tutorial 7.1 Unity UI HUD — Scene Setup", "src": [19], "b": [
            ("tree", 19, 0, 13),
        ]},
        {"s": "Related Tutorial", "src": [], "b": [
            ("tut", "tut-07-ui-overview.html", "Tutorial 07: Unity UI overview"),
        ]},
    ]},
    {"h2": "Tutorial 7.1 Unity UI HUD - Initialize Game Objects and Text Readouts", "src": "20-21", "sections": [
        {"s": "Tutorial 7.1 Unity UI Initialize Game Objects", "src": [20], "b": [
            ("p", 20, 0, 1),
            ("label", "Button (OnClick event and public void function)"),
            ("tree", 20, 3, 5),
            ("code", 20, 5, 19, "CreateMyPrimitives()"),
            ("img", [(20, 0, "100%", "Unity editor with butCreatePrimitives button OnClick wired to CreateMyPrimitives")]),
        ]},
        {"s": "Text Readouts on Panels- Basic", "src": [21], "b": [
            ("text", "Tutorial 7.1 Unity UI HUD Noorcon Inc. - Unity 3D Game Programming Part 4 - Vahe Karamian.pdf"),
            ("code", 21, 2, 29, "cube1Rotate.cs"),
            ("img", [(21, 0, "100%", "Unity HUD panels showing live cube position and rotation readouts")]),
            ("nested", "Notes", [
                ("text", STRING_FORMAT_NOTE),
                ("text", "Noorcon Inc. - Unity 3D Game Programming Introduction - Vahe Karamian.pdf"),
            ]),
        ]},
    ]},
    {"h2": "Tutorial 7 Extras - 7.1a to 7.4", "src": "22-30", "sections": [
        {"s": "Tutorial 7.1 Extras", "src": [22, 23, 24, 25, 26], "b": [
            ("label", "7.1a Initialize (Spawn) Cubes from key"),
            ("p", 23, 2, 3),
            ("label", "7.1b Button Event Handling (rather than Week 5 – OnClick)"),
            ("p", 24, 2, 3),
            ("label", "7.1c Button Event Handling on Instantiated Cube (both above combined)"),
            ("label", "7.1d Instantiate Prefab"),
        ]},
        {"s": "Extra - Tutorial 7.2 Unity UI HUD Text Readout Score – Simplified", "src": [28], "b": [
            ("p", 28, 1, 5),
            ("code", 28, 5, 7, "Variables"),
            ("p", 28, 7, 8),
            ("code", 28, 8, 12, "Start()"),
            ("p", 28, 12, 13),
            ("code", 28, 13, 17, "addPoints()"),
            ("p", 28, 17, 18),
            ("code", 28, 18, 21, "updateScoreCounter()"),
            ("nested", "Notes", [
                ("text", "Score:"),
                ("pdf", "6"),
            ]),
        ]},
        {"s": "Extra - Tutorial 7.3 / 7.4 Animate UI Button (Legacy and TextMeshPro)", "src": [29, 30], "b": [
            ("p", 29, 0, 1),
            ("p", 30, 0, 1),
            ("video", "mgaUKk8hfjg", "Animate UI Button", "https://youtu.be/mgaUKk8hfjg"),
            ("img", [(29, 0, "100%", "Unity Animator for a UI Button with Normal, Highlighted, Pressed and Disabled states")]),
            ("nested", "Notes", [
                ("text", "https://www.assetstore.unity3d.com/en/#!/content/25468"),
                ("video", "lNdhNHNwpjI", "Slider – control and display", "https://www.youtube.com/watch?v=lNdhNHNwpjI"),
                ("video", "OD-p1eMsyrU", "Layouts and Spaces", "https://www.youtube.com/watch?v=OD-p1eMsyrU"),
                ("text", "Animated Buttons"),
            ]),
        ]},
        {"s": "Next Steps", "src": [27], "b": [
            ("text", "We can continue with Unity UI with extra features in the next tutorials >>>"),
        ]},
    ]},
    {"h2": "Unity UI Tutorials, Menus, Levels and Widgets", "src": "31-34", "sections": [
        {"s": "Unity UI Tutorials General Interface", "src": [31], "b": [
            ("label", "Official Unity"),
            ("p", 31, 1, 3),
        ]},
        {"s": "Unity UI Menu Various (Games)", "src": [32], "b": [
            ("label", "Readouts"),
            ("pdf", "4"),
            ("label", "Health Bar"),
            ("pdf", "9"),
            ("p", 32, 2, 3),
            ("label", "Timer"),
            ("pdf", "6"),
            ("p", 32, 4, 5),
            ("label", "Collection Bar"),
            ("pdf", "6"),
            ("label", "Score/Info"),
            ("pdf", "6"),
            ("p", 32, 7, 8),
        ]},
        {"s": "Unity UI Menu and Levels", "src": [33], "b": [
            ("label", "Scene/Level Switching (Scene manager):"),
            ("video", "xyC_flufHwg", "Scene/Level Switching (Scene manager)", "https://www.youtube.com/watch?v=xyC_flufHwg"),
            ("nested", "Notes", [
                ("video", "FIa7qxGaRZo", "Scene/Level selection", "https://www.youtube.com/watch?v=FIa7qxGaRZo&index=86&list=PLX2vGYjWbI0Tg4eS9w29PPqg0Fx4sIL7p"),
                ("label", "Minimaps"),
                ("text", "https://www.packtpub.com/mapt/book/Game%20Development/9781785885822"),
                ("text", "https://www.packtpub.com/mapt#collapse10"),
            ]),
        ]},
        {"s": "Unity UI Widgets", "src": [34], "b": [
            ("label", "Player Control"),
            ("video", "nGYObojmkO4", "Player Control", "https://www.youtube.com/watch?v=nGYObojmkO4"),
            ("label", "Shop UI with ScrollLists"),
            ("video", "TAJCr3_kfEc", "Shop UI with ScrollLists", "https://www.youtube.com/watch?v=TAJCr3_kfEc"),
        ]},
    ]},
]


def render_section(sec, number, sub, first):
    pad = "          "
    body = []
    for block in sec["b"]:
        body.extend(render_block(block, pad))
    src = ", ".join(str(n) for n in sec["src"]) or "added cross-reference"
    return [
        f"      <!-- Section {number}.{sub}: {sec['s']} (source slide {src}) -->",
        f'      <details class="accordion"{" open" if first else ""}>',
        f"        <summary>{esc(sec['s'])}</summary>",
        '        <div class="accordion-body">',
        *body,
        "        </div>",
        "      </details>",
    ]


def render_slide(spec, number, total):
    first = number == 1
    out = [
        f"    <!-- Slide {number}: {spec['h2']} (source slides {spec['src']}) -->",
        f'    <div class="slide{" active" if first else ""}">',
        f'      <div class="slide-title">{SLIDE_TITLE}</div>',
        '      <div class="slide-content slide-content-accordion">',
        f"        <h2>{esc(spec['h2'])}</h2>",
        '        <div class="accordion-scroll">',
    ]
    for i, sec in enumerate(spec["sections"]):
        out.extend(render_section(sec, number, i + 1, i == 0))
    out += [
        "        </div>",
        "      </div>",
        '      <div class="slide-controls">',
        f'        <button class="slide-button" data-slide-step="-1"{" disabled" if first else ""}> ← Previous</button>',
        '        <img src="images/UOW_Logo_Length_Alpha.png" class="slide-logo" alt="University of Westminster" />',
        f'        <button class="slide-button" data-slide-step="1"{" disabled" if number == total else ""}>Next → </button>',
        f'        <div class="slide-counter"><span id="current-slide-{number}">{number}</span>'
        f' / <span id="total-slides">{total}</span></div>',
        "      </div>",
        '      <div class="keyboard-hint">',
        "        Use <kbd>→</kbd> <kbd>←</kbd> or click buttons to navigate",
        "      </div>",
        "    </div>",
        "",
    ]
    return out


def main():
    covered = {n for spec in PLAN for sec in spec["sections"] for n in sec["src"]}
    # 27 is a title-only transition slide; 9 is the "Unity UI" section divider.
    missing = set(data) - covered
    if missing:
        raise SystemExit(f"Source slides not mapped: {sorted(missing)}")

    original = FOOTER_SOURCE.read_text(encoding="utf-8").split("\n")
    marker = '  <script src="../assets/js/site.js'
    footer = original[next(i for i, ln in enumerate(original) if ln.startswith(marker)):]

    total = len(PLAN)
    doc = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="UTF-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        f"  <title>{PAGE_TITLE}</title>",
        '  <link rel="preconnect" href="https://fonts.googleapis.com" />',
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
        '  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />',
        '  <link rel="stylesheet" href="../assets/css/site.css?v=20261007a" />',
        '  <link rel="stylesheet" href="../assets/css/slideshow.css?v=20261007a" />',
        "</head>",
        '<body class="lecture-fullbleed">',
        '  <div class="slideshow-container">',
    ]
    for i, spec in enumerate(PLAN, 1):
        doc.extend(render_slide(spec, i, total))
    doc += ["  </div>", ""] + footer

    OUT_PATH.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT_PATH} with {total} slides from {len(data)} source slides")


if __name__ == "__main__":
    main()
