"""Rebuild lect-03a-3DUI-theory-practice.html with consolidated (concept-grouped) slides.

Source of truth is lect-03a-3DUI-theory-practice-content.json; the merge map below
defines which source slides/line-ranges become which section of which new slide.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
JSON_PATH = PAGES / "lect-03a-3DUI-theory-practice-content.json"
OUT_PATH = PAGES / "lect-03a-3DUI-theory-practice.html"

SLIDE_TITLE = "3D Interactive Media Development"
TITLE_H2 = "5MMCS001W\t\t\t\tLecture 03a"

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


MOUSE_ORBIT_BODY = """\
        <p>3D Mouse Orbit Examples</p>
        <details class="accordion accordion--nested video-accordion">
          <summary>Video: 3D Mouse Orbit Parallax Menu</summary>
          <div class="accordion-body">
            <article class="embed-card">
              <iframe class="video-embed" src="https://www.youtube.com/embed/B40xBPXK97A" title="3D Mouse Orbit Parallax Menu" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
              <p><a href="https://www.youtube.com/watch?v=B40xBPXK97A" target="_blank" rel="noopener noreferrer">Open source link</a></p>
            </article>
          </div>
        </details>
        <details class="accordion accordion--nested video-accordion">
          <summary>Link: 3D Mouse Orbit Trading Card</summary>
          <div class="accordion-body">
            <article class="embed-card">
              <iframe class="video-embed" src="https://ameye.dev/notes/holographic-card-shader/" title="Holographic Card Shader" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
              <p><a href="https://ameye.dev/notes/holographic-card-shader/" target="_blank" rel="noopener noreferrer">Open source link</a></p>
            </article>
          </div>
        </details>
        <details class="accordion accordion--nested video-accordion">
          <summary>Video: 3D Mouse Object Follow Cursor</summary>
          <div class="accordion-body">
            <article class="embed-card">
              <iframe class="video-embed" src="https://www.youtube.com/embed/AN786yWavTY" title="3D Mouse Object Follow Cursor" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
              <p><a href="https://www.youtube.com/watch?v=AN786yWavTY" target="_blank" rel="noopener noreferrer">Open source link</a></p>
            </article>
          </div>
        </details>
        <div class="h3-detail">
          <h3>Mouse Look vs Mouse Orbit</h3>
          <h3>Mouse Orbit - "Outside In"</h3>
            <p>Mouse rotates around Selected object</p>
            <p>Camera Pivot is at Objects Pivot</p>
          <h3>Mouse Look - "Inside Out"</h3>
            <p>From the perspective of the camera</p>
            <p>Also known as "Fishbowl" view</p>
            <p>Typical of VR applications and First Person Games</p>
          <h3>Exploded View example</h3>
            <p>Mouse/Camera Raycast Select</p>
            <p>Mouse or Camera view Raycast Selection of 3D object in 3D VE from 2D Screen</p>
            <p>Animations can be triggered by Object Selection, resulting in an Exploded view of all objects</p>
            <p>Objects selected from MouseLook - Triggers Camera Waypoint Animation to Selected Object</p>
            <p>Mouse Orbit around Selected Object, or switch to Fishbowl for an overall view and selecting another Waypoint jump</p>
          <p>Lowest level of selection frames and plays media</p>
        </div>""".split("\n")


def nested_embed(label, embed_url, watch_url, title, frame=True):
    """Nested video-accordion block; frame=False omits the iframe for un-framable sources."""
    esc = html.escape(title, quote=True)
    out = [
        '        <details class="accordion accordion--nested video-accordion">',
        f"          <summary>{html.escape(label)}</summary>",
        '          <div class="accordion-body">',
        '            <article class="embed-card">',
    ]
    if frame:
        out.append(
            f'              <iframe class="video-embed" src="{html.escape(embed_url, quote=True)}" title="{esc}"'
            ' loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
        )
    out += [
        f'              <p><a href="{html.escape(watch_url, quote=True)}" target="_blank" rel="noopener noreferrer">Open source link</a></p>',
        "            </article>",
        "          </div>",
        "        </details>",
    ]
    return out


def nested_video(label, vid):
    return nested_embed(label, f"https://www.youtube.com/embed/{vid}",
                        f"https://www.youtube.com/watch?v={vid}", label)


def nested_site(label, url, frame=True):
    return nested_embed(label, url, url, label, frame=frame)


QUAKE_BODY = (
    ["        <p>Quake 3 Web (js)</p>"]
    + nested_site("Link: Quake 3 Web (js) demo", "https://media.tojicode.com/q3bsp/")
    + [
        "        <p>Mouse Look - Cursor Lock</p>",
        "        <p>Mouse Selection  - State Switch from Cursor Lock</p>",
        "        <p>WASD Keyboard Navigation</p>",
        "        <p>Keyboard Interaction \u2013 State Changes</p>",
    ]
)

# rleonardi.com has an invalid TLS certificate, so it is linked rather than framed.
CV_BODY = (
    [
        "        <p>3DUI Interaction Practical examples - extras</p>",
        "        <p>Interactive 2D CV</p>",
    ]
    + nested_site("Link: Interactive 2D CV", "http://www.rleonardi.com/interactive-resume/", frame=False)
    + [
        "        <p>Narrative controlled by Mouse or Keyboard \u2013 Camera timeline</p>",
        "        <p>2D Diorama/Game Level</p>",
        "        <p>Collisions/timeline trigger animations</p>",
        "        <p>Web Links</p>",
        "        <p>Could be 3D with camera controls, object selection</p>",
    ]
)

PRACTICAL_BODY = (
    [
        '        <div class="h3-detail">',
        "          <h3>Practical Examples:</h3>",
        "        </div>",
        "        <p>Exploded view</p>",
    ]
    + nested_site("Link: Exploded View (paper, PDF)", "https://www.wilmotli.com/pubs/li08exview3D.pdf")
    + nested_video("Video: Exploded View", "NL2QFLiM_mY")
    + ["        <p>Exploded View \u2013 Car (Advanced)</p>"]
    + nested_video("Video: Exploded View \u2013 Car (Advanced)", "_i5RkAxGiwQ")
    + ["        <p>Diorama Fragments</p>"]
    + [
        line
        for i, vid in enumerate(
            ["Ty_hqTtvHdI", "5zmqZZshdfs", "U09hwnsUkY8", "iPEfHOCUVMI",
             "XmTRQml4Js0", "ErqpzWrQHAY", "meieYpHYTVU"], start=1
        )
        for line in nested_video(f"Video: Diorama Fragments {i}", vid)
    ]
)


# new slide: dict(h2=..., sections=[...], cls=optional extra .slide class, empty=True)
# section: dict(s=summary, t=[(slide, start, end)], img=[(slide, index, width)], raw=[html lines])
PLAN = [
    {"title": True, "h2": TITLE_H2, "sections": [
        {"s": "Example of an immersive 3D UI", "t": [(1, 0, 1)],
         "video": ("gwYjnWCcw18", "Example of an immersive 3D UI")},
    ]},
    {"h2": "3DUI Interaction Practical Examples", "sections": [
        {"s": "Quake 3 Web (js)", "raw": QUAKE_BODY},
        {"s": "3D Mouse Orbit Example", "raw": MOUSE_ORBIT_BODY},
        {"s": "Extras — Interactive 2D CV", "raw": CV_BODY},
        {"s": "Practical Examples", "raw": PRACTICAL_BODY},
    ]},
    {"h2": "Terminology — IVR, VR/VE, AR", "sections": [
        {"s": "IVR", "t": [(6, 0, 3)]},
        {"s": "VR, VE", "t": [(7, 0, 4)]},
        {"s": "AR", "t": [(8, 0, 2)]},
    ]},
    {"h2": "3DUI Applications", "sections": [
        {"s": "Simulation, Training, Education", "t": [(9, 0, 6)]},
    ]},
    {"h2": "Historical GUI and Platform Development", "sections": [
        {"s": "GUI", "t": [(10, 0, 7)]},
        {"s": "1940s", "t": [(11, 0, 2)], "img": [(11, 0, "48%"), (11, 1, "48%")]},
        {"s": "1960s", "t": [(12, 0, 1)], "img": [(12, 0, "48%"), (12, 1, "48%")]},
        {"s": "1980s on…", "t": [(13, 0, 4)]},
        {"s": "1990s on…", "t": [(14, 0, 7)], "img": [(14, 0, "48%"), (14, 1, "48%")]},
        {"s": "2000s on…", "t": [(15, 0, 5)], "img": [(15, 0, "48%"), (15, 1, "48%")]},
        {"s": "Current", "t": [(22, 0, 10)]},
    ]},
    {"h2": "Inputs and Outputs", "sections": [
        {"s": "2D GUI", "t": [(16, 0, 6)]},
        {"s": "3D Motion Tracking", "t": [(17, 0, 12)], "img": [(17, 0, "100%")]},
        {"s": "3D Sensors", "t": [(18, 0, 9)]},
        {"s": "Output/Displays…", "t": [(19, 0, 6)]},
        {"s": "Tablet/Smartphone", "t": [(23, 0, 12)]},
    ]},
    {"h2": "3DUI Interaction Practical Considerations", "sections": [
        {"s": "Coordinate Spaces and Ranges", "t": [(20, 0, 8)], "img": [(20, 0, "100%")]},
        {"s": "Issues with Extra Dimension", "t": [(21, 0, 13)]},
        {"s": "3DUI Framework Chart", "img": [(24, 0, "100%")]},
        {"s": "Basic Elements to consider and Plan", "t": [(25, 0, 9)]},
    ]},
    {"h2": "3DUI — Navigation", "sections": [
        {"s": "Navigation Classes", "img": [(28, 0, "100%")]},
        {"s": "Navigation — Travel and Wayfinding", "t": [(26, 0, 4)]},
        {"s": "Travel and Point of View", "t": [(27, 0, 3)]},
        {"s": "Examples", "t": [(27, 3, 10)]},
        {"s": "Travel should be simple", "t": [(29, 0, 8)]},
        {"s": "Reverie", "t": [(30, 0, 3)], "img": [(30, 0, "48%"), (30, 1, "48%")]},
    ]},
    {"h2": "3DUI — Interaction: Selection and Manipulation", "sections": [
        {"s": "Basic Elements to consider and Plan", "t": [(31, 0, 6)]},
    ]},
    {"h2": "3DUI — Selection Techniques", "sections": [
        {"s": "Selection", "img": [(32, 0, "100%")]},
        {"s": "Virtual Hand", "t": [(33, 0, 2)]},
        {"s": "Simple Virtual Hand", "t": [(34, 0, 7)], "img": [(34, 0, "100%")]},
        {"s": "RayCasting", "t": [(35, 0, 9)],
         "img": [(35, 0, "32%"), (35, 1, "32%"), (35, 2, "32%")]},
        {"s": "Occlusion", "t": [(36, 0, 4)],
         "img": [(36, 0, "32%"), (36, 1, "32%"), (36, 2, "32%")]},
        {"s": "Go Go Arm Extension", "t": [(37, 0, 3)], "img": [(37, 0, "100%")]},
        {"s": "Increase selection area", "t": [(38, 0, 3)]},
        {"s": "Other", "t": [(39, 0, 2)]},
    ]},
    {"h2": "3DUI — Manipulation", "sections": [
        {"s": "Manipulation", "img": [(40, 0, "100%")]},
        {"s": "Exocentric and Egocentric Metaphors", "t": [(41, 0, 12)]},
        {"s": "HOMER", "t": [(42, 0, 1)], "img": [(42, 0, "100%")]},
        {"s": "Go-Go (Indirect Go-Go)", "t": [(43, 0, 2)], "img": [(43, 0, "100%")]},
        {"s": "Scaled World Grab", "t": [(44, 0, 2)], "img": [(44, 0, "100%")]},
        {"s": "WIM", "t": [(45, 0, 3)], "img": [(45, 0, "100%")]},
        {"s": "Manipulation Tips — Match Interaction Technique to Device", "t": [(50, 0, 8)]},
    ]},
    {"h2": "3DUI — Widgets and Interaction for this Project", "sections": [
        {"s": "Typical for this project", "t": [(46, 0, 3)]},
        {"s": "Look at Vizor.io", "t": [(46, 3, 5)]},
        {"s": "3D UI: Menus and 3D interaction Widgets in Vizor.io", "t": [(47, 0, 8)]},
        {"s": "3DUI Interaction Widget examples", "t": [(48, 0, 3)], "img": [(48, 0, "100%")]},
        {"s": "Multimodal Example", "t": [(49, 0, 3)]},
    ]},
    {"h2": "3DUI Interaction — System Control", "sections": [
        {"s": "Basic Elements to consider and Plan", "t": [(51, 0, 3)]},
        {"s": "Examples", "t": [(51, 3, 9)]},
        {"s": "System Control Techniques", "t": [(52, 0, 9)]},
        {"s": "Unity 3D UI", "t": [(53, 0, 4)]},
        {"s": "System Control Tips", "t": [(54, 0, 5)]},
    ]},
    {"h2": "3DUI Unity — Next Steps", "sections": [
        {"s": "Screen Capture Software", "t": [(56, 0, 5)]},
    ]},
]


def render_line(ln, indent):
    # URLs stay plain text: the page's inline script linkifies and embeds videos at runtime.
    cls = ""
    if len(ln) <= 5 and ln.upper() == ln and any(c.isalpha() for c in ln):
        cls = ' class="section-label"'
    return f"{' ' * indent}<p{cls}>{html.escape(ln)}</p>"


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
    next_disabled = " disabled" if number == total else ""
    out = [
        f"    <!-- Slide {number} -->",
        f'    <div class="slide{active}{spec.get("cls", "")}">',
        f'      <div class="slide-title">{SLIDE_TITLE}</div>',
    ]
    if spec.get("empty"):
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
        f'        <button class="slide-button" data-slide-step="1"{next_disabled}>Next → </button>',
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
    "  <title>3DIMD | Lecture 03a - 3DUI Theory and Practice</title>",
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
