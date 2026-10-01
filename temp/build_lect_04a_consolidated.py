"""Rebuild lect-04a-report.html with consolidated (category-grouped) slides.

Source of truth is lect-04a-report-content.json; the merge map below defines
which source slides/line-ranges become which section of which new slide.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
JSON_PATH = PAGES / "lect-04a-report-content.json"
OUT_PATH = PAGES / "lect-04a-report.html"

SLIDE_TITLE = "3D Interactive Media Development"
TITLE_H2 = "5MMCS001W\t\t\t\tLecture 04"

data = {s["slide_number"]: s for s in json.load(JSON_PATH.open(encoding="utf-8"))}


def lines(num):
    out = []
    for block in data[num]["content"]:
        block = block.replace("\x0b", "\n").replace("\x0c", "\n")
        for ln in block.split("\n"):
            ln = ln.replace("\t", " ").replace("\xa0", " ").strip()
            if ln:
                out.append(ln)
    return out


def image(num, idx):
    return data[num]["images"][idx]["path"]


# new slides: dict(h2=..., sections=[...]) | dict(h2=..., divider=True) | dict(title=True)
# section: dict(s=summary, t=[(slide, start, end)], img=[(slide, index, width)])
PLAN = [
    {"title": True, "sections": [
        {"s": "Scale and Scope — Powers of Ten", "t": [],
         "raw": ['        <p>Charles and Ray Eames — Powers of Ten (1977)</p>'],
         "video": ("0fKBhvDjuy0", "Powers of Ten — Charles and Ray Eames")},
    ]},
    {"h2": "3DUI Interaction Practical examples", "sections": [
        {"s": "100,000 Stars — Google VR Experiment", "t": [(2, 0, 6)]},
        {"s": "3DUI Elements Used", "t": [(2, 6, 15)]},
    ]},
    {"h2": "CW Overview and Recap", "divider": True},
    {"h2": "CW Scope and Framework — Concepts", "sections": [
        {"s": "3D Content Creation/Production Software", "t": [(4, 0, 4)]},
        {"s": "Lego Based Construction", "t": [(5, 0, 14)]},
        {"s": "Elements", "t": [(6, 0, 3)]},
    ]},
    {"h2": "CW Framework — Platform and 3D Interaction", "sections": [
        {"s": "Framework for Module", "t": [(7, 0, 4)]},
        {"s": "So… 2D and 3D Manipulation", "t": [(8, 0, 8)]},
        {"s": "3D UI: 3D interaction Widgets", "t": [(9, 0, 8)]},
    ]},
    {"h2": "CW Framework — HCI Goals and Software", "sections": [
        {"s": "Goals", "t": [(10, 0, 3)]},
        {"s": "Manage Elements to Achieve Goals", "t": [(10, 3, 7)]},
        {"s": "Module Supported Framework", "t": [(11, 0, 13)]},
    ]},
    {"h2": "CW1 Group Report Outline", "divider": True},
    {"h2": "CW1 Report — a. Concept and Design", "sections": [
        {"s": "System Design and Implementation", "t": [(13, 0, 4)]},
        {"s": "a. Concept and Design", "t": [(14, 0, 1)]},
    ]},
    {"h2": "CW1 Report — b. Design Diagrams", "sections": [
        {"s": "b. Design Diagrams", "t": [(15, 0, 1)]},
        {"s": "Model View Controller", "t": [(16, 0, 1)]},
        {"s": "Diagram Types", "t": [(16, 1, 7)]},
        {"s": "Diagrams Reference and Guides", "t": [(32, 0, 7)]},
    ]},
    {"h2": "Design Diagrams — StoryBoard/Flowchart", "sections": [
        {"s": "StoryBoard/Flowchart", "t": [(17, 0, 13)]},
        {"s": "Examples", "img": [(17, 0, "48%"), (18, 0, "48%")]},
    ]},
    {"h2": "Design Diagrams — Use Case Diagram", "sections": [
        {"s": "Tools and Links", "t": [(19, 0, 3)]},
        {"s": "Defines", "t": [(19, 3, 8)]},
        {"s": "Example Diagram", "img": [(20, 0, "100%")]},
        {"s": "Relationship Types", "t": [(21, 0, 7)]},
        {"s": "Include vs Extend", "t": [(22, 0, 10)]},
        {"s": "Use Case Diagram Acupuncture", "t": [(23, 0, 2)], "img": [(23, 0, "100%")]},
        {"s": "Think about an Example for 10000 Stars", "t": [(24, 0, 2)]},
    ]},
    {"h2": "Design Diagrams — Domain Model/Class Diagram", "sections": [
        {"s": "Entities and What You Need", "t": [(25, 0, 10)]},
        {"s": "Domain Model/Class Diagram Murder Riddle", "img": [(30, 0, "100%")]},
        {"s": "Think about an Example for 10000 Stars", "t": [(31, 0, 2)]},
    ]},
    {"h2": "Design Diagrams — Model, View, Controller", "sections": [
        {"s": "What is MVC", "t": [(26, 1, 4)]},
        {"s": "Components", "t": [(27, 1, 9)]},
        {"s": "Interactions", "t": [(28, 1, 9)]},
        {"s": "MVC Diagram", "img": [(29, 0, "100%")]},
    ]},
    {"h2": "CW1 Report — c. Project Management Methodology", "sections": [
        {"s": "c. Project Management Methodology", "t": [(33, 0, 1)]},
        {"s": "Methodology", "t": [(34, 0, 3)]},
        {"s": "Some Examples", "t": [(35, 0, 5)]},
    ]},
    {"h2": "Methodology — Agile", "sections": [
        {"s": "Agile", "t": [(36, 1, 4)]},
        {"s": "Agile Manifesto Values", "t": [(37, 1, 6)]},
        {"s": "Agile Scrum", "t": [(38, 1, 4)]},
        {"s": "Simple Agile", "t": [(39, 1, 8)]},
    ]},
    {"h2": "Methodology — Waterfall", "sections": [
        {"s": "Waterfall", "t": [(40, 1, 2)]},
        {"s": "Origins", "t": [(41, 1, 2)], "img": [(41, 0, "100%")]},
        {"s": "Disadvantages", "t": [(42, 1, 2)]},
    ]},
    {"h2": "Methodology — Incremental", "sections": [
        {"s": "Incremental", "t": [(43, 1, 3)]},
        {"s": "Disadvantages", "t": [(44, 1, 2)]},
    ]},
    {"h2": "Methodology — Incremental, Iterative, Agile", "sections": [
        {"s": "Comparison", "t": [(45, 1, 5)]},
    ]},
    {"h2": "Methodology — Spiral", "sections": [
        {"s": "Spiral", "t": [(46, 1, 2)]},
        {"s": "Boehm lists these assumptions as follows", "t": [(47, 1, 8)]},
        {"s": "Spiral Diagram", "img": [(48, 0, "100%")]},
    ]},
    {"h2": "CW1 Report — d. Commercial Analysis", "sections": [
        {"s": "d. Commercial Analysis", "t": [(49, 0, 1)]},
        {"s": "System/Commercial Analysis", "t": [(50, 0, 4)]},
        {"s": "Commercial Analysis — Example", "t": [(51, 0, 1)], "img": [(51, 0, "100%")]},
        {"s": "Games Experience Questionnaire", "t": [(52, 0, 1)]},
    ]},
    {"h2": "CW1 Report — e, f, g. Navigation, Interactivity, Animation", "sections": [
        {"s": "e. Navigation Framework (with mouse and keyboard)", "t": [(53, 1, 5)]},
        {"s": "f. Interactivity (Selection and Manipulation, Triggers with mouse and keyboard)", "t": [(54, 1, 8)]},
        {"s": "g. Animation, Movement, Narrative", "t": [(54, 9, 13)]},
    ]},
    {"h2": "CW1 Report — g, h. Lighting, Shaders and UI Efficacy", "sections": [
        {"s": "g. Lighting, Shaders, and Texturing", "t": [(55, 1, 3)]},
        {"s": "h. Discuss 3D UI Efficacy", "t": [(55, 4, 7)]},
    ]},
    {"h2": "Remember — CW1 Deliverables", "sections": [
        {"s": "Group Report (3)", "t": [(56, 0, 17)]},
        {"s": "Individual Report (2)", "t": [(57, 0, 5)]},
    ]},
    {"h2": "CW2 Clarification and Group Contributions", "sections": [
        {"s": "Clarification — CW2 is implementation", "t": [(58, 0, 14)]},
        {"s": "4. Group Contributions", "t": [(59, 0, 7)]},
    ]},
    {"h2": "Unity 3D UI", "sections": [
        {"s": "Unity 3D UI", "t": [(60, 0, 4)]},
    ]},
    {"h2": "References", "sections": [
        {"s": "3D User Interfaces: Theory and Practice", "t": [(61, 0, 7)]},
    ]},
]


def render_line(ln, indent):
    # URLs stay plain text: the page's inline script linkifies and embeds videos at runtime.
    return f"{' ' * indent}<p>{html.escape(ln)}</p>"


def render_text(items, indent):
    """Lines ending in ':' open an h3-detail group holding the lines that follow."""
    out = []
    group = None
    for ln in items:
        if ln.endswith(":"):
            if group is not None:
                out.append(" " * indent + "</div>")
            out.append(" " * indent + '<div class="h3-detail">')
            out.append(" " * (indent + 2) + f"<h3>{html.escape(ln)}</h3>")
            group = ln
        else:
            out.append(render_line(ln, indent + 2 if group else indent))
    if group is not None:
        out.append(" " * indent + "</div>")
    return out


def render_images(imgs, indent):
    pad = " " * indent
    out = [f'{pad}<div class="accordion-images--horizontal" style="--accordion-images--horizontal-width: 100%;">']
    for num, idx, width in imgs:
        src = html.escape(image(num, idx), quote=True)
        out.append(
            f'{pad}  <img src="{src}" class="accordion-image" alt="Lecture illustration"'
            f' style="--accordion-image-width: {width};" />'
        )
    out.append(f"{pad}</div>")
    return out


def render_video(video, indent):
    """Inline embed card — avoids the runtime wrapping a bare URL in a nested accordion."""
    vid, title = video
    pad = " " * indent
    esc = html.escape(title, quote=True)
    return [
        f'{pad}<article class="embed-card">',
        f'{pad}  <iframe class="video-embed" src="https://www.youtube.com/embed/{vid}" title="{esc}"'
        ' loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>',
        f'{pad}  <p><a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener noreferrer">Open source link</a></p>',
        f"{pad}</article>",
    ]


def render_section(sec, first):
    text = []
    for num, start, end in sec.get("t", []):
        text.extend(lines(num)[start:end])
    imgs = sec.get("img", [])

    body = []
    if sec.get("raw"):
        body.extend(sec["raw"])
    elif text and imgs:
        body.append('        <div class="accordion-content-images-below">')
        body.extend(render_text(text, 10))
        body.extend(render_images(imgs, 10))
        body.append("        </div>")
    elif text:
        body.extend(render_text(text, 8))
    elif imgs:
        body.extend(render_images(imgs, 8))
    if sec.get("video"):
        body.extend(render_video(sec["video"], 8))

    open_attr = " open" if first else ""
    return [
        f'      <details class="accordion"{open_attr}>',
        f"        <summary>{html.escape(sec['s'])}</summary>",
        '        <div class="accordion-body">',
        *body,
        "        </div>",
        "      </details>",
    ]


def render_slide(spec, number, total):
    active = " active" if number == 1 else ""
    prev_disabled = " disabled" if number == 1 else ""
    out = [
        f"    <!-- Slide {number} -->",
        f'    <div class="slide{active}">',
        f'      <div class="slide-title">{SLIDE_TITLE}</div>',
    ]
    if spec.get("title"):
        out += [
            '      <div class="slide-content slide-content-accordion">',
            f"        <h2>{TITLE_H2}</h2>",
            '        <div class="accordion-scroll">',
        ]
        for i, sec in enumerate(spec["sections"]):
            out.extend(render_section(sec, i == 0))
        out += ["        </div>", "      </div>"]
    elif spec.get("divider"):
        out += ['      <div class="slide-content">', f"        <h2>{html.escape(spec['h2'])}</h2>", "      </div>"]
    else:
        out += [
            '      <div class="slide-content slide-content-accordion">',
            f"        <h2>{html.escape(spec['h2'])}</h2>",
            '        <div class="accordion-scroll">',
        ]
        for i, sec in enumerate(spec["sections"]):
            out.extend(render_section(sec, i == 0))
        out += ["        </div>", "      </div>"]

    out += [
        '      <div class="slide-controls">',
        f'        <button class="slide-button" data-slide-step="-1"{prev_disabled}> ← Previous</button>',
        '        <img src="images/UOW_Logo_Length_Alpha.png" class="slide-logo" alt="University of Westminster" />',
        '        <button class="slide-button" data-slide-step="1">Next → </button>',
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


FOOTER_MARKER = '  <script src="../assets/js/site.js'
original = OUT_PATH.read_text(encoding="utf-8").split("\n")
footer_start = next(i for i, ln in enumerate(original) if ln.startswith(FOOTER_MARKER))
footer = original[footer_start:]

total = len(PLAN)
doc = [
    "<!DOCTYPE html>",
    '<html lang="en">',
    "<head>",
    '  <meta charset="UTF-8" />',
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
    "  <title>3DIMD | Lecture 04a - Report</title>",
    '  <link rel="preconnect" href="https://fonts.googleapis.com" />',
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
    '  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />',
    '  <link rel="stylesheet" href="../assets/css/site.css?v=20261001a" />',
    '  <link rel="stylesheet" href="../assets/css/slideshow.css?v=20261001a" />',
    "</head>",
    '<body class="lecture-fullbleed">',
    '  <div class="slideshow-container">',
]
for i, spec in enumerate(PLAN, 1):
    doc.extend(render_slide(spec, i, total))
doc += ["  </div>", ""] + footer

OUT_PATH.write_text("\n".join(doc), encoding="utf-8")
print(f"wrote {OUT_PATH} with {total} slides")
