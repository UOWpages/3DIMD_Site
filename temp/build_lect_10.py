"""Build lect-10-pivots-animation.html with consolidated (theme-grouped) slides.

Text, paragraph levels, tables, hyperlinks and speaker notes are read from the
PPTX directly (the extractor JSON flattens levels and drops tables); images use
the extractor output in lect-10-pivots-animation-content.json. The PLAN
maps every source slide (1-46) onto a smaller set of themed slides; see
docs/lecture-conversion-playbook.md.
"""
import html
import json
import re
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
PPTX_PATH = ROOT / "site" / "source-lecture-pptx" / "3DIMD Lecture 10 Pivots and Animation.pptx"
JSON_PATH = PAGES / "lect-10-pivots-animation-content.json"
OUT_PATH = PAGES / "lect-10-pivots-animation.html"
FOOTER_SOURCE = PAGES / "lect-04a-report.html"

SLIDE_TITLE = "3D Interactive Media Development"
PAGE_TITLE = "3DIMD | Lecture 10 - Units, Scale, Pivots and Animation"

images = {s["slide_number"]: s["images"] for s in json.load(JSON_PATH.open(encoding="utf-8"))}
prs = Presentation(str(PPTX_PATH))
SLIDES = {i: s for i, s in enumerate(prs.slides, 1)}


def _collect_lines(slide):
    out = []

    def walk(shapes):
        for shape in shapes:
            if shape.shape_type == 6:
                walk(shape.shapes)
                continue
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for seg in para.text.replace("\x0b", "\n").replace("\r", "\n").split("\n"):
                    lead = re.match(r"^[\t\u2003\xa0 ]*", seg).group(0)
                    text = re.sub(r"\s+", " ", seg.replace("\xa0", " ")).strip()
                    if text and text != SLIDE_TITLE:
                        out.append((para.level + lead.count("\t"), text))

    walk(slide.shapes)
    return out


LINES = {n: _collect_lines(s) for n, s in SLIDES.items()}


def lines(num):
    return LINES[num]


def esc(text):
    return html.escape(text, quote=False)


def link(url, label):
    return f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


# ---------- block renderers (each returns list of lines at given indent) ----------

def r_paras(num, start, end, pad):
    return [f"{pad}<p>{esc(t)}</p>" for _, t in lines(num)[start:end]]


def r_joined(num, start, end, pad):
    """One paragraph from source lines that split a single sentence across lines."""
    return [f"{pad}<p>{esc(' '.join(t for _, t in lines(num)[start:end]))}</p>"]


def r_list(items, pad):
    """Nested <ul> from (depth, text) pairs."""
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
        out.append(f"{pad}{'  ' * level}<li>{esc(text)}")
        prev = level
    for closing in range(prev, -1, -1):
        out.append(f"{pad}{'  ' * closing}</li></ul>")
    return out


STATEMENT_RE = re.compile(r"^(using |public |private |protected |class |void |if\b|if\(|else\b|for\b|for\(|while\b|return\b)")
BRACELESS_RE = re.compile(r"^(if|for|while|else)\b.*[^{;]$|^(if|for|while)\(.*[^{;]$")


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
    pending = False
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
        shown = min(6, level + (1 if pending and not text.startswith("{") else 0))
        out.append(f'{pad}    <div class="code-panel__line code-panel__line--{tone} indent-level-{shown}">{esc(text)}</div>')
        if text.endswith("{"):
            level += 1
        pending = bool(BRACELESS_RE.match(text))
    out += [f"{pad}  </div>", f"{pad}</section>"]
    return out


def r_images(imgs, pad):
    out = [f'{pad}<div class="accordion-images--horizontal" style="--accordion-images--horizontal-width: 100%;">']
    for num, idx, width, alt in imgs:
        src = html.escape(images[num][idx]["path"], quote=True)
        out.append(
            f'{pad}  <img src="{src}" class="accordion-image" alt="{html.escape(alt, quote=True)}"'
            f' style="--accordion-image-width: {width};" />'
        )
    out.append(f"{pad}</div>")
    return out


def r_video(video_id, summary, watch_url, pad, start=None):
    s = esc(summary)
    query = f"?start={start}" if start else ""
    return [
        f'{pad}<details class="accordion accordion--nested embed-accordion">',
        f"{pad}  <summary>Video: {s}</summary>",
        f'{pad}  <div class="accordion-body">',
        f'{pad}    <article class="embed-card">',
        f'{pad}      <iframe class="video-embed" src="https://www.youtube.com/embed/{video_id}{query}" title="{html.escape(summary)} video"'
        ' loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>',
        f'{pad}      <p><a href="{html.escape(watch_url)}" target="_blank" rel="noopener noreferrer">Open source link</a></p>',
        f"{pad}    </article>",
        f"{pad}  </div>",
        f"{pad}</details>",
    ]


def r_table(num, pad):
    table = next(sh.table for sh in SLIDES[num].shapes if getattr(sh, "has_table", False) and sh.has_table)
    rows = [[re.sub(r"\s+", " ", c.text).strip() for c in row.cells] for row in table.rows]
    out = [f'{pad}<div class="assessment-table-wrap">', f'{pad}  <table class="assessment-table">', f"{pad}    <thead>", f"{pad}      <tr>"]
    out += [f"{pad}        <th>{esc(c)}</th>" for c in rows[0]]
    out += [f"{pad}      </tr>", f"{pad}    </thead>", f"{pad}    <tbody>"]
    for row in rows[1:]:
        out.append(f"{pad}      <tr>")
        out += [f"{pad}        <td>{esc(c)}</td>" for c in row]
        out.append(f"{pad}      </tr>")
    out += [f"{pad}    </tbody>", f"{pad}  </table>", f"{pad}</div>"]
    return out


def r_nested(summary, inner, pad):
    return [
        f'{pad}<details class="accordion accordion--nested">',
        f"{pad}  <summary>{esc(summary)}</summary>",
        f'{pad}  <div class="accordion-body">',
        *inner,
        f"{pad}  </div>",
        f"{pad}</details>",
    ]


def render_block(block, pad):
    kind = block[0]
    if kind == "p":                      # ("p", slide, start, end)
        return r_paras(block[1], block[2], block[3], pad)
    if kind == "pj":                     # ("pj", slide, start, end) -> one joined paragraph
        return r_joined(block[1], block[2], block[3], pad)
    if kind == "text":                   # ("text", literal text)
        return [f"{pad}<p>{esc(block[1])}</p>"]
    if kind == "label":                  # ("label", slide, index) -> h3 from source line
        return [f"{pad}<h3>{esc(lines(block[1])[block[2]][1])}</h3>"]
    if kind == "tree":                   # ("tree", slide, start, end) -> source paragraph levels
        return r_list(lines(block[1])[block[2]:block[3]], pad)
    if kind == "treed":                  # ("treed", slide, [(index, depth), ...]) -> explicit depths
        return r_list([(d, lines(block[1])[i][1]) for i, d in block[2]], pad)
    if kind == "code":                   # ("code", slide, start, end, title[, prefix lines])
        prefix = list(block[5]) if len(block) > 5 else []
        return r_code(prefix + [t for _, t in lines(block[1])[block[2]:block[3]]], pad, block[4])
    if kind == "img":                    # ("img", [(slide, idx, width, alt), ...])
        return r_images(block[1], pad)
    if kind == "video":                  # ("video", id, summary, watch_url[, start])
        return r_video(block[1], block[2], block[3], pad, *(block[4:5] or [None]))
    if kind == "table":                  # ("table", slide)
        return r_table(block[1], pad)
    if kind == "link":                   # ("link", label, url)
        return [f"{pad}<p>{link(block[2], block[1])}</p>"]
    if kind == "refs":                   # ("refs", summary, [(label, url), ...])
        items = [f"{pad}    <ul>"] + [f"{pad}      <li>{link(u, l)}</li>" for l, u in block[2]] + [f"{pad}    </ul>"]
        return r_nested(block[1], items, pad)
    if kind == "tut":                    # ("tut", page, label)
        return [f'{pad}<p><a href="../index.html?page=pages/{block[1]}" target="_top">{esc(block[2])}</a></p>']
    if kind == "from":                   # ("from", slide, index) -> "From <url>" with url isolated for linkify
        m = re.fullmatch(r"(.*?<)(https?://\S+?)(>)", lines(block[1])[block[2]][1])
        return [f"{pad}<p>{esc(m.group(1))}<span>{esc(m.group(2))}</span>{esc(m.group(3))}</p>"]
    if kind == "notes":                  # ("notes", slide[, start, end]) -> speaker notes accordion
        paras = [re.sub(r"\s+", " ", t).strip() for t in SLIDES[block[1]].notes_slide.notes_text_frame.text.split("\n")]
        paras = [t for t in paras if t][(block[2] if len(block) > 2 else None):(block[3] if len(block) > 3 else None)]
        return r_nested("Speaker notes", [f"{pad}    <p>{esc(t)}</p>" for t in paras], pad)
    if kind == "nested":                 # ("nested", summary, [blocks])
        inner = []
        for b in block[2]:
            inner.extend(render_block(b, pad + "    "))
        return r_nested(block[1], inner, pad)
    raise ValueError(kind)


def heading(num, idx=0):
    return lines(num)[idx][1]


YT = "https://www.youtube.com/watch?v="
CLOCKWORK = "http://www.aclockworkberry.com/world-coordinate-systems-in-3ds-max-unity-and-unreal-engine/"
LYNDA = "https://www.lynda.com/3ds-Max-tutorials/Animating-Unity-3D-3ds-Max/143342-2.html?utm_campaign=qHrsgt79cg0&utm_medium=viral&utm_source=youtube"
AUTODESK = "https://knowledge.autodesk.com/support/3ds-max/learn-explore/caas/CloudHelp/cloudhelp/{}/ENU/3DSMax/files/GUID-4115DE9B-D636-4A42-904E-71259A843E0A-htm.html"


def img(num, idx, width, alt):
    return (num, idx, width, alt)


# ---------- consolidation plan: 46 source slides -> 13 themed slides ----------
# section: dict(s=summary, src=[source slides], b=[blocks])
PLAN = [
    {"h2": "5MMCS001W Lecture 10 - Units, Scale, Pivots, Groups, Working with Assets", "src": "1-2", "sections": [
        {"s": "Lecture Overview", "src": [1], "b": [
            ("p", 1, 0, 3),
        ]},
        {"s": heading(2), "src": [2], "b": [
            ("treed", 2, [(1, 0), (2, 1), (3, 1), (4, 1), (5, 1), (6, 0), (7, 1), (8, 1)]),
            ("p", 2, 9, 10),
        ]},
        {"s": "Related Tutorials", "src": [], "b": [
            ("tut", "tut-09-10-0-blender-origins-and-pivots-cheatsheet.html", "Tutorial 09-10: Blender - Origins & Pivot Points"),
            ("tut", "tut-09-10-02-blender-lego-minifig-tutorial-startup-and-reference-images.html", "Tutorials 09-10: Blender Lego Minifig series"),
            ("tut", "tut-11-02-blender-pivots-and-animation-sheet.html", "Tutorial 11-02: Prepare & Animate a LEGO Minifigure in Blender"),
            ("tut", "tut-04-students.html", "Tutorial 04: Unity Animation and Animation Import Overview"),
        ]},
    ]},
    {"h2": "Units and Scale", "src": "3-5", "sections": [
        {"s": heading(3, 1), "src": [3], "b": [
            ("pj", 3, 2, 4),
            ("p", 3, 4, 7),
        ]},
        {"s": "Units Setup and Export to Unity", "src": [4], "b": [
            ("tree", 4, 1, 12),
            ("p", 4, 12, 13),
        ]},
        {"s": heading(5), "src": [5], "b": [
            ("tree", 5, 1, 5),
        ]},
    ]},
    {"h2": "Pivots in Objects - World Coordinate Systems", "src": "6-9", "sections": [
        {"s": "Pivot Offsets in Unity", "src": [6], "b": [
            ("p", 6, 1, 2),
            ("img", [img(6, 0, "32%", "Unity scene with a Lego brick and a cube"),
                     img(6, 1, "32%", "Unity scene showing the cube's pivot gizmo at an offset position"),
                     img(6, 2, "32%", "Unity scene showing the Lego brick's pivot gizmo"),
                     img(6, 3, "48%", "3ds Max viewport with the Lego brick selected and its pivot shown"),
                     img(6, 4, "48%", "Unity scene with a second Lego brick added beside the cube")]),
        ]},
        {"s": heading(7, 1), "src": [7], "b": [
            ("p", 7, 2, 3),
            ("img", [img(7, 0, "50%", "3ds Max test scene with teapot and textured quad, pivot shown in world coordinates")]),
        ]},
        {"s": heading(8, 1), "src": [8], "b": [
            ("p", 8, 2, 3),
            ("img", [img(8, 0, "60%", "Teapot and quad in 3ds Max compared with the rotated import in Unity 3D")]),
        ]},
        {"s": "Unity 3D Axis Conventions", "src": [9], "b": [
            ("p", 9, 1, 2),
            ("tree", 9, 2, 5),
            ("img", [img(9, 0, "50%", "Teapot in Unity showing Up (Y), Right (X) and Forward (Z) axes")]),
        ]},
    ]},
    {"h2": "Fixing Orientation from 3ds Max to Unity 3D", "src": "10-12", "sections": [
        {"s": heading(10, 1), "src": [10], "b": [
            ("p", 10, 2, 5),
            ("img", [img(10, 0, "50%", "Teapot in Unity showing Up (Y), Right (X) and Forward (Z) axes")]),
        ]},
        {"s": "Result: Reoriented Pivot", "src": [11], "b": [
            ("p", 11, 2, 3),
            ("img", [img(11, 0, "50%", "3ds Max reoriented pivot on the teapot and the correctly oriented import in Unity 3D")]),
            ("p", 11, 3, 4),
        ]},
        {"s": heading(12), "src": [12], "b": [
            ("p", 12, 1, 2),
            ("link", "Lynda.com: Animating for Unity 3D in 3ds Max", LYNDA),
            ("pj", 12, 4, 6),
            ("tree", 12, 6, 12),
        ]},
    ]},
    {"h2": "Pivots - Blender and Unity Strategies", "src": "13-15", "sections": [
        {"s": heading(13), "src": [13], "b": [
            ("p", 13, 1, 5),
            ("img", [img(13, 0, "40%", "Blender Edit Mode with a cube's vertices selected before rotation"),
                     img(13, 1, "40%", "Blender Edit Mode with the cube mesh rotated 90 degrees on the X axis")]),
        ]},
        {"s": heading(14), "src": [14], "b": [
            ("p", 14, 1, 6),
            ("img", [img(14, 0, "25%", "Blender cube with the origin moved using the 3D Cursor pivot point"),
                     img(14, 1, "25%", "Blender cube with the origin at its centre, shown in an orthographic view")]),
        ]},
        {"s": heading(15), "src": [15], "b": [
            ("p", 15, 1, 2),
            ("treed", 15, [(i, 0 if i in (2, 5, 6, 14, 16) else 1) for i in range(2, 17)]),
        ]},
    ]},
    {"h2": "Pivots - Max and Unity Strategies, Normalizing", "src": "16-18", "sections": [
        {"s": heading(16), "src": [16], "b": [
            ("p", 16, 1, 4),
            ("img", [img(16, 0, "50%", "Cubes in 3ds Max with coloured faces showing the +Z, -Y and +X sides")]),
        ]},
        {"s": heading(17), "src": [17], "b": [
            ("p", 17, 1, 2),
            ("img", [img(17, 0, "45%", "3ds Max Hierarchy tab Affect Pivot Only with the pivot moved on a cube")]),
        ]},
        {"s": heading(18), "src": [18], "b": [
            ("p", 18, 1, 3),
            ("img", [img(18, 0, "28%", "3ds Max Hierarchy Pivot panel with Reset Transform and Scale for a Lego minifig"),
                     img(18, 1, "60%", "Blender Object > Apply menu with All Transforms highlighted")]),
        ]},
    ]},
    {"h2": "Pivots, Grouping, Linking, Hierarchy", "src": "19-20", "sections": [
        {"s": heading(19, 1), "src": [19], "b": [
            ("p", 19, 2, 5),
            ("link", "Autodesk 3ds Max 2015 Help: Linking objects into hierarchies", AUTODESK.format(2015)),
            ("p", 19, 7, 9),
            ("label", 19, 9),
            ("link", "My Video: Lego Minifig with Animation, Grouping, Hierarchy (YouTube, speaker notes)", YT + "dKFv7J7-0ps"),
        ]},
        {"s": heading(20, 1), "src": [20], "b": [
            ("p", 20, 2, 5),
        ]},
        {"s": heading(20, 5), "src": [20], "b": [
            ("p", 20, 6, 7),
            ("link", "Autodesk 3ds Max 2016 Help: Linking objects into hierarchies", AUTODESK.format(2016)),
            ("p", 20, 9, 11),
            ("link", "Fix for a scaled model (YouTube, speaker notes)", YT + "kPMshbMrGDw"),
        ]},
    ]},
    {"h2": "Max/Blender To Unity Basic Minifig Procedure and Online Game Assets", "src": "21-23", "sections": [
        {"s": heading(21), "src": [21], "b": [
            ("label", 21, 1),
            ("p", 21, 2, 4),
            ("label", 21, 4),
            ("p", 21, 5, 7),
        ]},
        {"s": "Minifig Pivots and Hierarchy", "src": [22], "b": [
            ("treed", 22, [(1, 0), (2, 0), (3, 0), (4, 1), (5, 1), (6, 1), (7, 1)]),
            ("img", [img(22, 0, "45%", "3ds Max minifig hierarchy with a root arrow between the feet and the body as parent")]),
        ]},
        {"s": heading(23), "src": [23], "b": [
            ("label", 23, 1),
            ("p", 23, 2, 6),
        ]},
    ]},
    {"h2": "Animation: The Animation Principles", "src": "24-26", "sections": [
        {"s": heading(25), "src": [24, 25], "b": [
            ("p", 25, 1, 6),
        ]},
        {"s": "Animation Principles (continued)", "src": [26], "b": [
            ("p", 26, 1, 7),
        ]},
    ]},
    {"h2": "Animation Principles 1-5", "src": "27-31", "sections": [
        {"s": "1. Squash and Stretch", "src": [27], "b": [
            ("p", 27, 0, 1),
            ("img", [img(27, 0, "70%", "Bouncing ball drawings squashing on contact with the ground")]),
            ("notes", 27),
        ]},
        {"s": "2. Timing and Motion", "src": [28], "b": [
            ("p", 28, 0, 1),
            ("img", [img(28, 0, "48%", "Bouncing ball arcs with frame spacing"),
                     img(28, 1, "48%", "Bouncing ball path losing height with each bounce")]),
            ("notes", 28),
        ]},
        {"s": "3. Anticipation", "src": [29], "b": [
            ("p", 29, 0, 2),
            ("tree", 29, 2, 5),
            ("p", 29, 5, 6),
            ("img", [img(29, 0, "70%", "Pendulum sequence: start at A, draw-back, move, go past B, back to B")]),
            ("notes", 29, 4),
        ]},
        {"s": "4. Staging", "src": [30], "b": [
            ("p", 30, 0, 2),
            ("img", [img(30, 0, "45%", "Character kicking shown in colour and in silhouette, side and front views"),
                     img(30, 1, "30%", "Luxo Jr. desk lamps from Pixar")]),
            ("notes", 30, 0, -1),
        ]},
        {"s": "5. Follow Through and Overlapping Action", "src": [31], "b": [
            ("p", 31, 0, 3),
            ("img", [img(31, 0, "70%", "Double pendulum swing sequence from A to B")]),
            ("notes", 31),
        ]},
    ]},
    {"h2": "Animation Principles 6-10", "src": "32-37", "sections": [
        {"s": "6. Straight Ahead Action and Pose-to-Pose Action", "src": [32, 33], "b": [
            ("p", 32, 0, 2),
            ("img", [img(32, 0, "70%", "Pose-to-pose sequence of a mouse character waking and stretching")]),
            ("p", 33, 1, 2),
        ]},
        {"s": "7. Slow In and Out", "src": [35], "b": [
            ("p", 35, 0, 1),
            ("img", [img(35, 0, "48%", "Ball spacing chart with closer spacing at the holds and wider spacing in the middle"),
                     img(35, 1, "48%", "Ball spacing chart with ease out of the first pose and ease into the last")]),
            ("notes", 35),
        ]},
        {"s": "8. Arcs", "src": [34], "b": [
            ("p", 34, 0, 1),
            ("img", [img(34, 0, "45%", "Walk cycle with the head following an arc (idleworm.com)")]),
            ("notes", 34),
        ]},
        {"s": "9. Exaggeration", "src": [36], "b": [
            ("p", 36, 0, 1),
            ("img", [img(36, 0, "32%", "Cartoon wolf exaggerated reaction to a showgirl"),
                     img(36, 1, "32%", "Cartoon character's face stretched into a cone in an exaggerated take"),
                     img(36, 2, "16%", "Frame sequence of an exaggerated cartoon take")]),
            ("notes", 36),
        ]},
        {"s": "10. Secondary Action", "src": [37], "b": [
            ("p", 37, 0, 1),
            ("img", [img(37, 0, "48%", "Arcs of a tail or whip and hand drawings showing delayed follow-through"),
                     img(37, 1, "48%", "Double pendulum swing sequence from A to B")]),
            ("notes", 37),
        ]},
    ]},
    {"h2": "Solid Drawing and Animation Tips", "src": "38-44", "sections": [
        {"s": "12. Solid Drawing - Body Breakdown", "src": [38, 39], "b": [
            ("p", 38, 0, 1),
            ("img", [img(38, 0, "30%", "Mannequin and hero figure with a line of action through the body"),
                     img(38, 1, "36%", "Duck character built from spheres and cylinders beside the finished drawing"),
                     img(39, 0, "50%", "Sketches of a figure broken down into spheres and boxes")]),
        ]},
        {"s": "12. Solid Drawing - Skeleton Rigs", "src": [40], "b": [
            ("p", 40, 0, 1),
            ("img", [img(40, 0, "45%", "Elephant drawing with a skeleton rig and body masses"),
                     img(40, 1, "45%", "Bull drawing with a skeleton rig and body masses")]),
        ]},
        {"s": heading(41), "src": [41], "b": [
            ("tree", 41, 1, 8),
            ("label", 41, 8),
            ("tree", 41, 9, 10),
        ]},
        {"s": "Tips: " + heading(42, 1), "src": [42], "b": [
            ("img", [img(42, 0, "60%", "Cat sketches with a curved line of action")]),
        ]},
        {"s": "Tips: " + heading(43, 1), "src": [43], "b": [
            ("img", [img(43, 0, "60%", "Insect character poses showing balance and mass")]),
        ]},
        {"s": "Tips: " + heading(44, 1), "src": [44], "b": [
            ("img", [img(44, 0, "60%", "Character poses showing tilt and asymmetry")]),
        ]},
    ]},
    {"h2": "Tutorial Demos and Unity Animation", "src": "45-46", "sections": [
        {"s": heading(45), "src": [45], "b": [
            ("tree", 45, 1, 5),
        ]},
        {"s": heading(46), "src": [46], "b": [
            ("video", "ts24UWC0mY4", "Animation 101 - Intro to Animation in Unity", YT + "ts24UWC0mY4"),
            ("video", "QN3joSQyzQQ", "Animation 102 - Animating 2D Characters", YT + "QN3joSQyzQQ"),
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
    missing = set(SLIDES) - covered
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
    print(f"wrote {OUT_PATH} with {total} slides from {len(SLIDES)} source slides")


if __name__ == "__main__":
    main()
