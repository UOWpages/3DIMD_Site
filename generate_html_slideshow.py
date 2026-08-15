#!/usr/bin/env python3
"""Convert extracted PowerPoint JSON to HTML slideshow using the canonical lecture panel shell."""

import argparse
import json
from pathlib import Path


def build_args():
    parser = argparse.ArgumentParser(description="Generate lecture slideshow HTML from extracted lecture JSON.")
    parser.add_argument(
        "--lecture-id",
        default="lect-01a",
        help="Lecture id used for input/output naming, e.g. lect-01b",
    )
    parser.add_argument(
        "--lecture-title",
        default="Lecture 01a - Module Info",
        help="Text used in the HTML document title.",
    )
    parser.add_argument(
        "--module-title",
        default="3D Interactive Media Development",
        help="Default per-slide title text.",
    )
    parser.add_argument(
        "--pages-dir",
        default="site/pages",
        help="Directory containing lecture JSON and HTML outputs.",
    )
    return parser.parse_args()


args = build_args()
pages_dir = Path(__file__).parent / Path(args.pages_dir)

json_path = pages_dir / f"{args.lecture_id}-content.json"
with open(json_path, "r", encoding="utf-8") as f:
    slides_data = json.load(f)

html_template = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>3DIMD | __LECTURE_TITLE__</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap\" rel=\"stylesheet\" />
  <link rel=\"stylesheet\" href=\"../assets/css/site.css?v=20260805m\" />
    <link rel=\"stylesheet\" href=\"../assets/css/slideshow.css?v=20260814e\" />
  <style>
    body.lecture-fullbleed .slideshow-container {
      visibility: hidden;
    }

    body.lecture-fullbleed.lecture-ready .slideshow-container {
      visibility: visible;
    }

    body.lecture-fullbleed .slide-title {
      display: none !important;
    }

    body.lecture-fullbleed .slide-content > h2 {
      display: none !important;
    }
  </style>
</head>
<body class=\"lecture-fullbleed\">
  <div class=\"slideshow-container\">
"""

for slide in slides_data:
    slide_num = slide["slide_number"]
    content = slide["content"]
    images = slide["images"]
    parent_title = (slide.get("title") or "").strip()
    section_title = (slide.get("section_title") or "").strip()
    if section_title and parent_title and parent_title != args.module_title:
        display_title = f"{parent_title} - {section_title}"
    else:
        display_title = section_title or parent_title

    content_html = ""
    if display_title:
        content_html += f"    <h2>{display_title}</h2>\n"

    if content:
        for text in content:
            if text.strip() == args.module_title:
                continue

            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if line.endswith(":"):
                    content_html += f"    <h3>{line}</h3>\n"
                elif line.startswith("LO"):
                    content_html += f"    <p class=\"learning-outcome\"><strong>{line}</strong></p>\n"
                elif line.startswith("L5-"):
                    content_html += f"    <p class=\"module-aim\"><strong>{line}</strong></p>\n"
                elif line.isupper() and len(line) < 50 and len(line.split()) <= 3:
                    content_html += f"    <p class=\"section-label\">{line}</p>\n"
                else:
                    content_html += f"    <p>{line}</p>\n"

    for img in images:
        content_html += f"    <img src=\"images/{img['filename']}\" alt=\"Slide {slide_num} image\" />\n"

    html_template += f"""    <!-- Slide {slide_num} -->
    <div class=\"slide{"" if slide_num != 1 else " active"}\">
      <div class=\"slide-title\">{args.module_title}</div>
      <div class=\"slide-content\">
{content_html}      </div>
      <div class=\"slide-controls\">
        <button class=\"slide-button\" onclick=\"changeSlide(-1)\"{"" if slide_num > 1 else " disabled"}> ← Previous</button>
        <img src=\"../images/UOW_Logo_Length_Alpha.png\" class=\"slide-logo\" alt=\"University of Westminster\" />
        <button class=\"slide-button\" onclick=\"changeSlide(1)\"{"" if slide_num < len(slides_data) else " disabled"}>Next → </button>
        <div class=\"slide-counter\"><span id=\"current-slide-{slide_num}\">{slide_num}</span> / <span id=\"total-slides\">{len(slides_data)}</span></div>
      </div>
      <div class=\"keyboard-hint\">
        Use <kbd>→</kbd> <kbd>←</kbd> or click buttons to navigate
      </div>
    </div>

"""

html_template += """  </div>

  <script src=\"../assets/js/site.js?v=20260805f\"></script>
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

    function enhanceLectureVideos(slide) {
      const videoPattern = /^https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([^\s&?]+)(.*)$/i;
      slide.querySelectorAll('.accordion-body > p').forEach((paragraph) => {
        const match = paragraph.textContent.trim().match(videoPattern);
        if (!match) return;

        const sourceUrl = match[0];
        const videoId = match[1];
        const query = match[2] || '';
        const previous = paragraph.previousElementSibling;
        const context = previous ? previous.textContent.replace(/\s+/g, ' ').trim() : '';
        const details = document.createElement('details');
        details.className = 'accordion accordion--nested video-accordion';
        details.innerHTML = `
          <summary>${context || 'Video'}</summary>
          <div class="accordion-body">
            <article class="embed-card">
              <iframe class="video-embed" src="https://www.youtube.com/embed/${videoId}${query}" title="${context || 'Video'}" loading="lazy" allowfullscreen></iframe>
              <p><a href="${sourceUrl}" target="_blank" rel="noopener noreferrer">Open source link</a></p>
            </article>
          </div>`;
        paragraph.replaceWith(details);
      });
    }

    function enhanceLectureImageLayouts(slide) {
      slide.querySelectorAll('.accordion-body').forEach((body) => {
        const images = Array.from(body.children).filter((child) => child.tagName === 'IMG');
        if (!images.length || body.querySelector(':scope > .slide-media-layout')) return;

        const layout = document.createElement('div');
        layout.className = 'slide-media-layout';
        const textColumn = document.createElement('div');
        textColumn.className = 'slide-text-column';
        const imageColumn = document.createElement('div');
        imageColumn.className = 'slide-image-column';

        Array.from(body.children).forEach((child) => {
          if (child.tagName === 'IMG') imageColumn.appendChild(child);
          else textColumn.appendChild(child);
        });

        layout.append(textColumn, imageColumn);
        body.appendChild(layout);
      });
    }

    function getAccordionLabels(titleText) {
      const title = (titleText || '').toLowerCase();

      if (title.includes('workflow')) {
        return { overview: 'Workflow Steps', resources: 'Diagrams and Media' };
      }

      if (title.includes('references') || title.includes('reading')) {
        return { overview: 'Reading Notes', resources: 'References and Media' };
      }

      if (title.includes('group') || title.includes('activity')) {
        return { overview: 'Guidance', resources: 'Resources' };
      }

      return { overview: 'Overview', resources: 'Resources and Media' };
    }

    function normalizeAccordionLabel(text) {
      const cleaned = (text || '').replace(/\s+/g, ' ').replace(/[:\-]+$/, '').trim();
      if (!cleaned) return '';

      const lowered = cleaned.toLowerCase();
      if (lowered === 'overview' || lowered === 'resources' || lowered === 'resources and media') {
        return '';
      }

      return cleaned;
    }

    function inferOverviewLabel(body, h2) {
      const headingCandidates = Array.from(body.querySelectorAll(':scope > h3, :scope > .section-label'));
      for (const node of headingCandidates) {
        const candidate = normalizeAccordionLabel(node.textContent);
        if (candidate) return candidate;
      }

      const headingText = (h2 ? h2.textContent : '').replace(/\s+/g, ' ').trim();
      const parenthetical = headingText.match(/\(([^)]+)\)/);
      if (parenthetical) {
        const candidate = normalizeAccordionLabel(parenthetical[1]);
        if (candidate) return candidate;
      }

      const firstParagraph = body.querySelector(':scope > p');
      if (firstParagraph) {
        const paragraphText = (firstParagraph.textContent || '').replace(/\s+/g, ' ').trim();
        const wordCount = paragraphText.split(/\s+/).filter(Boolean).length;
        const looksLikeLabel = !/[.!?]$/.test(paragraphText) && !/^https?:\/\//i.test(paragraphText);
        if (wordCount > 0 && wordCount <= 6 && looksLikeLabel) {
          const candidate = normalizeAccordionLabel(paragraphText);
          if (candidate) return candidate;
        }
      }

      return '';
    }

    function convertLegacySlideToAccordion(slide) {
      const body = slide.querySelector('.slide-content');
      if (!body || body.classList.contains('slide-content-accordion')) return;

      const h2 = body.querySelector(':scope > h2');
      const labels = getAccordionLabels(h2 ? h2.textContent : '');
      const inferredOverviewLabel = inferOverviewLabel(body, h2);
      const customOverviewLabel = body.getAttribute('data-overview-label');
      const customResourcesLabel = body.getAttribute('data-resources-label');
      if (inferredOverviewLabel) {
        labels.overview = inferredOverviewLabel;
      }
      if (customOverviewLabel) {
        labels.overview = customOverviewLabel;
      }
      if (customResourcesLabel) {
        labels.resources = customResourcesLabel;
      }
      const children = Array.from(body.children).filter((node) => node !== h2);
      if (!children.length) return;

      const overviewItems = [];
      const resourcesItems = [];

      children.forEach((node) => {
        const tag = node.tagName ? node.tagName.toLowerCase() : '';
        const text = (node.textContent || '').trim();
        const hasUrl = /https?:\\/\\//i.test(text);
        const isImage = tag === 'img';
        const hasLink = Boolean(node.querySelector && node.querySelector('a'));

        if (isImage || hasUrl || hasLink) {
          resourcesItems.push(node);
        } else {
          overviewItems.push(node);
        }
      });

      body.classList.add('slide-content-accordion');
      body.innerHTML = '';
      if (h2) body.appendChild(h2);

      const scroll = document.createElement('div');
      scroll.className = 'accordion-scroll';

      if (overviewItems.length) {
        const overview = document.createElement('details');
        overview.className = 'accordion';
        overview.open = true;

        const summary = document.createElement('summary');
        summary.textContent = labels.overview;

        const content = document.createElement('div');
        content.className = 'accordion-body';
        overviewItems.forEach((node) => content.appendChild(node));

        overview.appendChild(summary);
        overview.appendChild(content);
        scroll.appendChild(overview);
      }

      if (resourcesItems.length) {
        const resources = document.createElement('details');
        resources.className = 'accordion';

        const summary = document.createElement('summary');
        summary.textContent = labels.resources;

        const content = document.createElement('div');
        content.className = 'accordion-body';
        resourcesItems.forEach((node) => content.appendChild(node));

        resources.appendChild(summary);
        resources.appendChild(content);
        scroll.appendChild(resources);
      }

      body.appendChild(scroll);
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

    slides.forEach((slide, index) => {
      normalizeSlideStructure(slide);
      if (index >= 3) {
        convertLegacySlideToAccordion(slide);
      }
      enhanceLectureVideos(slide);
      enhanceLectureImageLayouts(slide);
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
</html>"""

html_template = html_template.replace("__LECTURE_TITLE__", args.lecture_title)

output_file = pages_dir / f"{args.lecture_id}.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Generated slideshow with {len(slides_data)} slides")
print(f"Saved to: {output_file}")
