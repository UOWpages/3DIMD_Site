#!/usr/bin/env python3
"""Step 1b builder for lect-04b-all-scripting-access-other: converts the
extracted JSON into the standard lecture slide shell, following the
established conventions (see docs/lecture-conversion-playbook.md section 8a):
- heading = first line -> <h2> (later promoted to slide-title, then removed)
- lines ending ":" -> <h3>
- short ALL-CAPS lines -> <p class="section-label">
- bullet lines -> <ul><li>
- "From <url>" attribution lines -> <p class="slide-citation"> with a real link
- all text is HTML-escaped (this deck's C# code uses generics like
  GetComponent<Foo>(), which would otherwise be parsed as HTML tags)
- vertical-tab (\\x0b) soft line breaks from PPTX text runs are normalized to
  real newlines before splitting into per-line paragraphs
"""
import html
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PAGES_DIR = REPO_ROOT / "site" / "pages"
LECTURE_ID = "lect-04b-all-scripting-access-other"
JSON_PATH = PAGES_DIR / f"{LECTURE_ID}-content.json"
OUTPUT_PATH = PAGES_DIR / f"{LECTURE_ID}.html"

MODULE_TITLE = "3D Interactive Media Development"
LECTURE_TITLE = "Lecture 04b - Unity Scripting: Access Other GameObjects and Scripts"

SOFT_HYPHEN = "\u00ad"
ZERO_WIDTH = "\u200b"

CITATION_RE = re.compile(r'^From\s*<?\s*(https?://\S+?)\s*>?\s*$', re.IGNORECASE)


def clean_text(text: str) -> str:
    text = text.replace(SOFT_HYPHEN, "").replace(ZERO_WIDTH, "")
    text = text.replace("\u000b", "\n").replace("\u000c", "\n")
    text = text.replace("\u2010", "-")
    return text


def is_bullet(line: str) -> bool:
    return bool(re.match(r"^[\u2022*\-]\s*\t?\s*", line)) and len(line) > 1


def strip_bullet(line: str) -> str:
    return re.sub(r"^[\u2022*\-]\s*\t?\s*", "", line).strip()


def is_section_label(line: str) -> bool:
    return line.isupper() and len(line) < 50 and len(line.split()) <= 6


def render_lines(lines):
    html_out = []
    bullet_buffer = []

    def flush_bullets():
        if bullet_buffer:
            html_out.append("    <ul>")
            for item in bullet_buffer:
                html_out.append(f"      <li>{item}</li>")
            html_out.append("    </ul>")
            bullet_buffer.clear()

    for line in lines:
        line = line.strip()
        line = re.sub(r"\s+", " ", line)
        if not line:
            continue

        citation_match = CITATION_RE.match(line)
        if citation_match:
            flush_bullets()
            url = html.escape(citation_match.group(1))
            html_out.append(
                f'    <p class="slide-citation">From '
                f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></p>'
            )
            continue

        escaped = html.escape(line)

        if is_bullet(line):
            bullet_buffer.append(html.escape(strip_bullet(line)))
            continue

        flush_bullets()

        if line.endswith(":") and len(line) < 70:
            html_out.append(f"    <h3>{escaped}</h3>")
        elif is_section_label(line):
            html_out.append(f'    <p class="section-label">{escaped}</p>')
        else:
            html_out.append(f"    <p>{escaped}</p>")

    flush_bullets()
    return html_out


def build_slide_html(slide, total_slides):
    slide_num = slide["slide_number"]
    content_blocks = [clean_text(b) for b in slide["content"] if clean_text(b).strip() != MODULE_TITLE]

    content_lines = []
    for block in content_blocks:
        content_lines.extend(block.split("\n"))

    heading = ""
    body_lines = content_lines
    for idx, line in enumerate(content_lines):
        if line.strip():
            heading = re.sub(r"\s+", " ", line.strip())
            body_lines = content_lines[idx + 1:]
            break

    content_html_lines = [f"    <h2>{html.escape(heading)}</h2>"] if heading else []
    content_html_lines.extend(render_lines(body_lines))

    for img in slide["images"]:
        content_html_lines.append(f'    <img src="images/{img["filename"]}" alt="Slide {slide_num} image" />')

    content_html = "\n".join(content_html_lines)

    is_first = slide_num == 1
    is_last = slide_num == total_slides
    active_class = " active" if is_first else ""
    prev_disabled = " disabled" if is_first else ""
    next_disabled = " disabled" if is_last else ""

    return f"""    <!-- Slide {slide_num} -->
    <div class="slide{active_class}">
      <div class="slide-title">{MODULE_TITLE}</div>
      <div class="slide-content">
{content_html}
      </div>
      <div class="slide-controls">
        <button class="slide-button" onclick="changeSlide(-1)"{prev_disabled}> &larr; Previous</button>
        <img src="../images/UOW_Logo_Length_Alpha.png" class="slide-logo" alt="University of Westminster" />
        <button class="slide-button" onclick="changeSlide(1)"{next_disabled}>Next &rarr; </button>
        <div class="slide-counter"><span id="current-slide-{slide_num}">{slide_num}</span> / <span id="total-slides">{total_slides}</span></div>
      </div>
      <div class="keyboard-hint">
        Use <kbd>&rarr;</kbd> <kbd>&larr;</kbd> or click buttons to navigate
      </div>
    </div>
"""


HEAD = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>3DIMD | {LECTURE_TITLE}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../assets/css/site.css?v=20260805m" />
  <link rel="stylesheet" href="../assets/css/slideshow.css?v=20260814b" />
  <style>
    body.lecture-fullbleed .slideshow-container {{
      visibility: hidden;
    }}

    body.lecture-fullbleed.lecture-ready .slideshow-container {{
      visibility: visible;
    }}

    body.lecture-fullbleed .slide-title {{
      display: none !important;
    }}

    body.lecture-fullbleed .slide-content > h2 {{
      display: none !important;
    }}
  </style>
</head>
<body class="lecture-fullbleed">
  <div class="slideshow-container">
"""

TAIL = """  </div>

  <script src="../assets/js/site.js?v=20260805f"></script>
  <script>
    const isLecturePage = /\\/lect-[^/]+\\.html$/i.test(window.location.pathname);
    if (isLecturePage && document.body) {
      document.body.classList.add('lecture-fullbleed');
    }

    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;

    function normalizeSlideStructure(slide) {
      if (slide.querySelector('.slide-frame')) return;

      const title = slide.querySelector('.slide-title');
      const controls = slide.querySelector('.slide-controls');
      const body = slide.querySelector('.slide-content');
      if (!title || !controls || !body) return;

      const frame = document.createElement('div');
      frame.className = 'slide-frame';
      frame.appendChild(title);
      frame.appendChild(body);
      frame.appendChild(controls);
      slide.appendChild(frame);
    }

    function linkifyText(element) {
      const urlPattern = /(https?:\\/\\/[^\\s]+)/g;
      const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
      );

      const nodesToReplace = [];
      let node;

      while (node = walker.nextNode()) {
        if (urlPattern.test(node.textContent)) {
          nodesToReplace.push(node);
        }
      }

      urlPattern.lastIndex = 0;

      nodesToReplace.forEach((textNode) => {
        const span = document.createElement('span');
        span.innerHTML = textNode.textContent.replace(
          /(https?:\\/\\/[^\\s]+)/g,
          '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        textNode.parentNode.replaceChild(span, textNode);
      });
    }

    function syncSlideTitles() {
      slides.forEach((slide) => {
        const title = slide.querySelector('.slide-title');
        const heading = slide.querySelector('.slide-content h2');
        if (!title || !heading) return;

        const headingText = (heading.textContent || '').replace(/\\s+/g, ' ').trim();
        if (headingText) {
          title.textContent = headingText;
          heading.remove();
        }
      });
    }

    function announceActiveSlideTitle() {
      const activeSlide = slides[currentSlide];
      if (!activeSlide) return;

      const titleNode = activeSlide.querySelector('.slide-title');
      const titleText = (titleNode ? titleNode.textContent : '').replace(/\\s+/g, ' ').trim();
      if (!titleText) return;

      if (window.parent && window.parent !== window) {
        window.parent.postMessage({
          type: 'lecture-slide-title',
          title: titleText
        }, '*');
      }
    }

    slides.forEach((slide) => {
      normalizeSlideStructure(slide);
      linkifyText(slide.querySelector('.slide-content') || slide);
    });

    syncSlideTitles();

    function updateCounters() {
      slides.forEach((slide, index) => {
        const counter = slide.querySelector('.slide-counter');
        if (counter) {
          counter.textContent = `${index + 1} / ${totalSlides}`;
        }
      });
    }

    function showSlide(n) {
      slides.forEach((slide) => slide.classList.remove('active'));
      slides[currentSlide].classList.add('active');

      const allButtons = document.querySelectorAll('.slide-button');
      const isFirstSlide = currentSlide === 0;
      const isLastSlide = currentSlide === totalSlides - 1;

      allButtons.forEach((btn) => {
        if (btn.textContent.includes('Previous')) {
          btn.disabled = isFirstSlide;
        } else if (btn.textContent.includes('Next')) {
          btn.disabled = isLastSlide;
        }
      });

      updateCounters();
      announceActiveSlideTitle();
    }

    function changeSlide(n) {
      currentSlide += n;
      if (currentSlide >= totalSlides) currentSlide = totalSlides - 1;
      if (currentSlide < 0) currentSlide = 0;
      showSlide(currentSlide);
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') changeSlide(1);
      if (e.key === 'ArrowLeft') changeSlide(-1);
    });

    showSlide(currentSlide);
    document.body.classList.add('lecture-ready');
  </script>
</body>
</html>
"""


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        slides_data = json.load(f)

    total = len(slides_data)
    parts = [HEAD]
    for slide in slides_data:
        parts.append(build_slide_html(slide, total))
        parts.append("\n")
    parts.append(TAIL)

    OUTPUT_PATH.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({total} slides)")


if __name__ == "__main__":
    main()
