"""Build lect-08-input-movement-collision.html with consolidated (theme-grouped) slides.

Text, paragraph levels, tables, hyperlinks and speaker notes are read from the
PPTX directly (the extractor JSON flattens levels and drops tables); images use
the extractor output in lect-08-input-movement-collision-content.json. The PLAN
maps every source slide (1-55) onto a smaller set of themed slides; see
docs/lecture-conversion-playbook.md.
"""
import html
import json
import re
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "site" / "pages"
PPTX_PATH = ROOT / "site" / "source-lecture-pptx" / "3DIMD Lecture 08 Unity All Scripting 03 - Input Movement Collision 01 (4).pptx"
JSON_PATH = PAGES / "lect-08-input-movement-collision-content.json"
OUT_PATH = PAGES / "lect-08-input-movement-collision.html"
FOOTER_SOURCE = PAGES / "lect-04a-report.html"

SLIDE_TITLE = "3D Interactive Media Development"
PAGE_TITLE = "3DIMD | Lecture 08 - Input Manager, Scripted Movement, Collisions"

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
    if kind == "nested":                 # ("nested", summary, [blocks])
        inner = []
        for b in block[2]:
            inner.extend(render_block(b, pad + "    "))
        return r_nested(block[1], inner, pad)
    raise ValueError(kind)


def heading(num, idx=0):
    return lines(num)[idx][1]


CODEPROJECT = "http://www.codeproject.com/Articles/876478/UNITY-D-GAME-PROGRAMMING-PART"
OLD_DOCS = "http://docs.unity3d.com/Documentation/ScriptReference/"
NEW_DOCS = "https://docs.unity3d.com/ScriptReference/"
LERPING_USINGS = ["using System.Collections;", "using System.Collections.Generic;", "using UnityEngine;"]

# ---------- consolidation plan: 55 source slides -> 14 themed slides ----------
# section: dict(s=summary, src=[source slides], b=[blocks])
PLAN = [
    {"h2": "5MMCS001W Lecture 08 - Input Manager (Again), Scripted Movement, Collisions", "src": "1-2", "sections": [
        {"s": "Lecture Overview", "src": [1, 2], "b": [
            ("p", 1, 0, 2),
            ("p", 2, 0, 1),
        ]},
        {"s": "Related Tutorials", "src": [], "b": [
            ("tut", "tut-02-03-students.html", "Tutorials 02–03: Input, movement and collision exercises"),
            ("tut", "tut-08-character-troubleshooting-bb.html", "Tutorial 08: Character controllers and troubleshooting"),
            ("tut", "tut-08-physics-quiz-rbct.html", "Tutorial 08 Quiz: Rigidbodies, colliders and triggers"),
        ]},
    ]},
    {"h2": "Unity Input Manager", "src": "3, 8-9", "sections": [
        {"s": heading(3), "src": [3], "b": [
            ("p", 3, 1, 3),
            ("tree", 3, 3, 6),
            ("p", 3, 6, 7),
        ]},
        {"s": heading(8), "src": [8], "b": [
            ("img", [(8, 0, "32%", "Unity Project Settings Input Manager axes list"),
                     (8, 1, "32%", "Input Manager Horizontal axis expanded with its properties"),
                     (8, 2, "32%", "Input Manager axis configuration screenshot")]),
        ]},
        {"s": "Input Manager - Horizontal Axis Properties", "src": [9], "b": [
            ("p", 9, 1, 2),
            ("tree", 9, 2, 9),
            ("img", [(9, 0, "40%", "Input Manager Horizontal axis expanded with its properties highlighted")]),
        ]},
    ]},
    {"h2": "Input Movement Scripting - Rotate and Get Axis", "src": "4-7, 10", "sections": [
        {"s": heading(4), "src": [4], "b": [
            ("p", 4, 1, 3),
            ("label", 4, 3),
        ]},
        {"s": heading(5), "src": [5], "b": [
            ("p", 5, 1, 2),
            ("tree", 5, 2, 5),
            ("p", 5, 5, 7),
        ]},
        {"s": heading(6), "src": [6], "b": [
            ("p", 6, 1, 2),
            ("label", 6, 2),
            ("code", 6, 3, 14, "CreatePrimitivesFromImport.cs"),
        ]},
        {"s": heading(7), "src": [7], "b": [
            ("p", 7, 1, 2),
            ("label", 7, 2),
            ("tree", 7, 3, 8),
        ]},
        {"s": heading(10), "src": [10], "b": [
            ("p", 10, 1, 2),
            ("code", 10, 2, 5, "Direct Input"),
            ("label", 10, 5),
            ("tree", 10, 6, 8),
            ("p", 10, 8, 10),
        ]},
    ]},
    {"h2": "Scalars, Points, Vectors and Vector3", "src": "11-14", "sections": [
        {"s": heading(11), "src": [11], "b": [
            ("label", 11, 1),
            ("tree", 11, 2, 4),
        ]},
        {"s": "Points", "src": [12], "b": [
            ("p", 12, 0, 1),
            ("tree", 12, 2, 5),
        ]},
        {"s": "Vectors (Lines) and Vector3", "src": [13], "b": [
            ("p", 13, 0, 1),
            ("label", 13, 1),
            ("tree", 13, 2, 5),
            ("label", 13, 5),
            ("tree", 13, 6, 8),
        ]},
        {"s": "Vector3 in Scripted Movement", "src": [14], "b": [
            ("p", 14, 0, 2),
            ("label", 14, 2),
            ("p", 14, 3, 5),
            ("code", 14, 5, 10, "Instantiate a row of blocks"),
        ]},
    ]},
    {"h2": "Transform and Rigidbody Basics", "src": "15-18, 21", "sections": [
        {"s": "Transform and Rigid Body", "src": [15], "b": [
            ("p", 15, 0, 2),
            ("label", 15, 2),
            ("p", 15, 3, 6),
            ("label", 15, 6),
            ("p", 15, 7, 8),
        ]},
        {"s": "Mesh, Collider, RigidBody, Kinematic and Triggers", "src": [16], "b": [
            ("p", 16, 0, 2),
            ("treed", 16, [(2, 0), (3, 1), (4, 0), (5, 1), (6, 0), (7, 1), (8, 1), (9, 1),
                           (10, 0), (11, 1), (12, 1), (13, 0), (14, 1)]),
            ("video", "rXYjB0kdf-U", "Rigidbody and Collisions | Unity Tutorial", "https://www.youtube.com/watch?v=rXYjB0kdf-U"),
        ]},
        {"s": "RigidBody", "src": [17], "b": [
            ("p", 17, 0, 2),
            ("label", 17, 2),
            ("pj", 17, 3, 5),
            ("p", 17, 5, 6),
        ]},
        {"s": "Rigidbody Body Type", "src": [18], "b": [
            ("p", 18, 0, 2),
            ("label", 18, 2),
            ("treed", 18, [(3, 0), (4, 1), (5, 0), (6, 1), (7, 0), (8, 0)]),
            ("p", 18, 9, 10),
        ]},
        {"s": "isKinematic", "src": [21], "b": [
            ("p", 21, 0, 2),
            ("p", 21, 3, 5),
        ]},
        {"s": "Further Reading (speaker notes)", "src": [15, 18, 19, 20, 21], "b": [
            ("text", CODEPROJECT),
        ]},
    ]},
    {"h2": "Kinematic vs Dynamic Rigidbodies and Controllers", "src": "19-20, 28-29", "sections": [
        {"s": "Kinematic vs Non-Kinematic (Dynamic) Transform", "src": [19], "b": [
            ("p", 19, 0, 1),
            ("table", 19),
        ]},
        {"s": "Controller Chart – non-RB, RB vs Dynamic, Kinematic and Static", "src": [20], "b": [
            ("p", 20, 0, 1),
            ("link", lines(20)[1][1], "https://github.com/Module-Code/Controllers/tree/main"),
            ("img", [(20, 0, "48%", "Controller chart part 1: controller types, movement approaches and rules of thumb"),
                     (20, 1, "48%", "Controller chart part 2: kinematic and dynamic rigidbody movement approaches and rules of thumb")]),
        ]},
        {"s": "Controller Types", "src": [28], "b": [
            ("label", 28, 0),
            ("p", 28, 1, 2),
            ("label", 28, 2),
            ("p", 28, 3, 4),
            ("label", 28, 4),
            ("p", 28, 5, 6),
        ]},
        {"s": heading(29), "src": [29], "b": [
            ("label", 29, 1),
            ("p", 29, 2, 4),
            ("label", 29, 4),
            ("p", 29, 5, 7),
            ("label", 29, 7),
            ("p", 29, 8, 10),
            ("label", 29, 10),
            ("p", 29, 11, 12),
        ]},
    ]},
    {"h2": "Translate, Rotate, Update vs FixedUpdate and Time.deltaTime", "src": "22-25", "sections": [
        {"s": "Tutorial 02-03: Translate, Rotate to move", "src": [22], "b": [
            ("p", 22, 0, 1),
            ("code", 22, 1, 19, "TransformFunctions.cs"),
            ("refs", "Unity Scripting API references", [
                ("Input.GetKey", OLD_DOCS + "Input.GetKey.html"),
                ("KeyCode.UpArrow", OLD_DOCS + "KeyCode.UpArrow.html"),
                ("KeyCode.DownArrow", OLD_DOCS + "KeyCode.DownArrow.html"),
                ("KeyCode.LeftArrow", OLD_DOCS + "KeyCode.LeftArrow.html"),
                ("KeyCode.RightArrow", OLD_DOCS + "KeyCode.RightArrow.html"),
                ("Vector3.forward", OLD_DOCS + "Vector3-forward.html"),
                ("Vector3.up", OLD_DOCS + "Vector3-up.html"),
                ("Time.deltaTime", OLD_DOCS + "Time-deltaTime.html"),
            ]),
        ]},
        {"s": "Time Delta Time", "src": [23], "b": [
            ("p", 23, 0, 2),
            ("p", 23, 3, 5),
            ("label", 23, 5),
            ("tree", 23, 6, 8),
            ("code", 23, 8, 12, "Frames vs seconds"),
            ("p", 23, 12, 13),
        ]},
        {"s": "Update vs FixedUpdate", "src": [24], "b": [
            ("p", 24, 0, 2),
            ("label", 24, 2),
            ("p", 24, 3, 4),
            ("pj", 24, 4, 6),
            ("tree", 24, 6, 9),
            ("label", 24, 9),
            ("pj", 24, 10, 12),
            ("p", 24, 12, 13),
        ]},
        {"s": heading(25), "src": [25], "b": [
            ("label", 25, 1),
            ("p", 25, 2, 3),
            ("code", 25, 3, 6, "Time.deltaTime"),
            ("p", 25, 6, 9),
            ("label", 25, 9),
            ("code", 25, 10, 11, "Velocity"),
        ]},
    ]},
    {"h2": "Forces and Physics - MovePosition, AddForce and Best Practice", "src": "26-27, 41", "sections": [
        {"s": "Rigidbody.MovePosition", "src": [26], "b": [
            ("p", 26, 0, 2),
            ("label", 26, 2),
            ("p", 26, 3, 7),
            ("code", 26, 7, 8, "MovePosition"),
            ("p", 26, 8, 9),
        ]},
        {"s": "AddForce", "src": [26], "b": [
            ("label", 26, 9),
            ("p", 26, 10, 13),
        ]},
        {"s": "Forces and Physics: With a Character", "src": [27], "b": [
            ("label", 27, 2),
            ("p", 27, 3, 8),
        ]},
        {"s": heading(41), "src": [41], "b": [
            ("p", 41, 1, 3),
            ("tree", 41, 3, 6),
            ("p", 41, 6, 7),
        ]},
    ]},
    {"h2": "Collider Interactions and Collision Tables", "src": "30-33, 35", "sections": [
        {"s": "Collider Interactions", "src": [30], "b": [
            ("p", 30, 0, 2),
            ("label", 30, 2),
            ("p", 30, 3, 4),
            ("label", 30, 4),
            ("p", 30, 5, 6),
            ("label", 30, 6),
            ("p", 30, 7, 8),
            ("label", 30, 8),
            ("p", 30, 9, 10),
        ]},
        {"s": "Collider, Kinematic Rigidbody, Transform - Sliding Door Example", "src": [31], "b": [
            ("p", 31, 0, 2),
            ("label", 31, 2),
            ("p", 31, 3, 4),
            ("pj", 31, 4, 7),
            ("pj", 31, 7, 9),
            ("p", 31, 9, 10),
            ("pj", 31, 10, 12),
            ("p", 31, 12, 13),
        ]},
        {"s": heading(32), "src": [32, 33], "b": [
            ("img", [(32, 0, "100%", "Unity collision action matrix: when collision detection and trigger messages are sent for each collider type pair")]),
            ("img", [(33, 0, "80%", "Collision matrix of Static, Rigidbody, Kinematic Rigidbody and Trigger colliders with Yes/No results")]),
        ]},
        {"s": "Collider, non-Kinematic Rigidbody - AddForce, MovePosition, MoveRotation", "src": [35], "b": [
            ("p", 35, 0, 2),
            ("label", 35, 2),
            ("p", 35, 3, 4),
            ("p", 35, 5, 6),
            ("tree", 35, 6, 9),
            ("tree", 35, 10, 12),
        ]},
    ]},
    {"h2": "Unity Collisions and Triggers", "src": "34, 36-39", "sections": [
        {"s": "Triggers - Script Actions on Collision", "src": [34], "b": [
            ("p", 34, 0, 2),
            ("label", 34, 2),
            ("p", 34, 3, 6),
            ("pj", 34, 6, 8),
            ("video", "-osaSS9L-fs", "Detecting Collisions on Kinematic Rigidbodies", "https://www.youtube.com/watch?v=-osaSS9L-fs"),
        ]},
        {"s": "Collision and Physics: OnCollisonEnter(Collision col)", "src": [36, 37], "b": [
            ("p", 36, 0, 1),
            ("label", 37, 1),
            ("p", 37, 2, 4),
            ("tree", 37, 4, 8),
        ]},
        {"s": "RigidBody, Collision - Gravity and IsKinematic", "src": [38], "b": [
            ("p", 38, 3, 4),
            ("tree", 38, 4, 15),
        ]},
        {"s": "Collision and Physics: SHORTCUT", "src": [39], "b": [
            ("p", 39, 2, 3),
            ("label", 39, 4),
            ("tree", 39, 5, 7),
            ("p", 39, 7, 8),
        ]},
    ]},
    {"h2": "Collisions and Triggers - Unity Test Project and Demo", "src": "40, 42-43", "sections": [
        {"s": heading(42), "src": [40, 42], "b": [
            ("video", "WFkbqdo2OI4", "Unity 3d: Collisions, Triggers, Rigidbodies, and Kinematics", "https://www.youtube.com/watch?v=WFkbqdo2OI4"),
            ("img", [(42, 0, "80%", "CollisionTester script with OnCollisionEnter, OnTriggerEnter and FixedUpdate movement")]),
        ]},
        {"s": "Demo", "src": [43], "b": [
            ("label", 43, 2),
            ("tree", 43, 3, 13),
        ]},
    ]},
    {"h2": "Raycasting and Input Widgets", "src": "44, 47-48", "sections": [
        {"s": heading(47), "src": [47], "b": [
            ("label", 47, 1),
            ("p", 47, 2, 3),
        ]},
        {"s": heading(48), "src": [48], "b": [
            ("p", 48, 1, 3),
            ("pj", 48, 3, 5),
            ("pj", 48, 5, 7),
            ("code", 48, 7, 17, "ExampleClass.cs"),
            ("p", 48, 17, 18),
            ("refs", "Unity Scripting API references", [
                ("LayerMask", NEW_DOCS + "LayerMask.html"),
                ("MonoBehaviour", NEW_DOCS + "MonoBehaviour.html"),
                ("Vector3", NEW_DOCS + "Vector3.html"),
                ("Vector3.forward", NEW_DOCS + "Vector3-forward.html"),
                ("Physics.Raycast", NEW_DOCS + "Physics.Raycast.html"),
            ]),
        ]},
        {"s": heading(44), "src": [44], "b": [
            ("label", 44, 1),
            ("p", 44, 2, 5),
            ("label", 44, 5),
            ("video", "nGYObojmkO4", "Unity 5 Mobile Joysticks Tutorial - Touch Input 2D Spaceship Controller", "https://www.youtube.com/watch?v=nGYObojmkO4&t=3s", 3),
            ("label", 44, 7),
            ("p", 44, 8, 9),
            ("img", [(44, 0, "60%", "Unity 4.6 touch joystick widget demo")]),
        ]},
    ]},
    {"h2": "Lerp, MoveTowards and LookAt", "src": "49-54", "sections": [
        {"s": "Lerps, Eases and MoveTowards", "src": [49], "b": [
            ("p", 49, 0, 1),
            ("label", 49, 1),
            ("p", 49, 2, 3),
            ("p", 49, 3, 4),
            ("p", 49, 4, 5),
            ("label", 49, 5),
            ("video", "oXKyqAltCgI", "Unity: Input, Simple Player Movement, and LookAt/MoveTowards", "https://www.youtube.com/watch?v=oXKyqAltCgI"),
            ("tree", 49, 7, 10),
        ]},
        {"s": "Lerp", "src": [50], "b": [
            ("label", 50, 1),
            ("p", 50, 2, 6),
        ]},
        {"s": heading(51, 1), "src": [51], "b": [
            ("label", 51, 2),
            ("code", 51, 3, 7, "Vector3.Lerp"),
            ("refs", "References", [
                ("Vector3.Lerp", OLD_DOCS + "Vector3.Lerp.html"),
            ]),
            ("nested", "Notes", [
                ("text", "http://www.thegamecontriver.com/2014/10/move-to-mouse-click-touch-position-unity.html"),
            ]),
        ]},
        {"s": "Lerping Script", "src": [49, 52], "b": [
            ("code", 52, 0, 30, "Lerping.cs", LERPING_USINGS),
        ]},
        {"s": "MoveTowards", "src": [53], "b": [
            ("p", 53, 2, 4),
            ("p", 53, 5, 6),
        ]},
        {"s": "Look At", "src": [54], "b": [
            ("p", 54, 2, 7),
        ]},
    ]},
    {"h2": "CW1 and Next Steps", "src": "45-46, 55", "sections": [
        {"s": "CW1", "src": [45, 46], "b": [
            ("tree", 45, 1, 8),
            ("label", 45, 8),
            ("tree", 45, 9, 12),
        ]},
        {"s": heading(55), "src": [55], "b": [
            ("p", 55, 1, 2),
            ("label", 55, 2),
            ("tree", 55, 3, 12),
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
