#!/usr/bin/env python3
"""Convert extracted PowerPoint JSON to HTML slideshow using the canonical lecture panel shell."""

import argparse
import html
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


def render_software_lines(content):
  lines = []
  for block in content:
    for line in block.replace("\u000b", "\n").splitlines():
      line = line.strip()
      if not line or line.isdigit() or line == "Links":
        continue
      escaped = html.escape(line)
      if line.endswith(":"):
        lines.append(f"<h3>{escaped}</h3>")
      else:
        lines.append(f"<p>{escaped}</p>")
  return "\n".join(lines)


def build_software_section(slide):
  number = slide["slide_number"]
  images = slide.get("images", [])
  if number == 1:
    title = "3D Interactive Media Development: Software Required for this Module"
    image_html = (
      f'<img class="software-required__backdrop" src="images/{images[0]["filename"]}" '
      'alt="Software required overview" />'
      '<div class="software-required__image-row">'
      + "".join(
        f'<img src="images/{image["filename"]}" alt="Software required example {index + 1}" />'
        for index, image in enumerate(images[1:])
      )
      + "</div>"
    )
    body = f'<div class="software-required__hero">{image_html}</div>'
  elif number == 2:
    sections = [
      (
        "Links",
        ["All software is Free, but needs various accounts. You must set up the accounts and download/ install/ test on your laptop or desktop before tutorials start."],
      ),
      (
        "All University Software and Platforms:",
        [
          "Overview and Links for All University Software and Platforms.",
          "https://www.westminster.ac.uk/current-students/studies/study-skills-and-training/digital-skills/software-and-platforms",
        ],
      ),
      (
        "Apps Anywhere (may require a new install from link – new UI):",
        [
          "Portal for University and Home Software Installs.",
          "https://www.westminster.ac.uk/current-students/studies/study-skills-and-training/digital-skills/appsanywhere-university-software",
        ],
      ),
      (
        "Adobe Creative Cloud for Student Home Install:",
        [
          "Portal for University and Home Software Installs.",
          "https://www.westminster.ac.uk/current-students/studies/study-skills-and-training/digital-skills/adobe-creative-cloud-for-students",
        ],
      ),
      (
        "Splashtop (Log into and Use University PCs and software - Unsupported):",
        [
          "Portal for University and Home Software Installs.",
          "https://www.westminster.ac.uk/current-students/studies/study-skills-and-training/digital-skills/splashtop-remote-access",
        ],
      ),
    ]
    return "".join(
      f'''      <details class="accordion">
        <summary>{html.escape(title)}</summary>
        <div class="accordion-body">{render_software_lines(content)}</div>
      </details>'''
      for title, content in sections
    )
  elif number == 3:
    sections = [
      (
        "Software Links",
        [
          "All software is Free, but needs various accounts, try setting up the accounts and downloading/ installing/ testing on your Laptop or desktop.",
          "Both Macs and PCs are ok to use in this module.",
          "Unity3D and Mecabricks are used in the first 6 weeks and throughout. 3DStudio max and Photoshop in the last 6 weeks.",
        ],
      ),
      (
        "Required: Blender 5.2",
        ["Blender 5.2 is used for 3D modelling and asset preparation.", "https://www.blender.org/download/"],
      ),
      (
        "Required: Unity3D 6000.3.19f1",
        [
          "Unity3D 6000.3.19f1 is the required version for this module.",
          "https://unity.com/releases/editor/archive",
        ],
      ),
      (
        "Required: Visual Studio 2026 Community",
        [
          "Visual Studio 2026 Community is the required development environment for Unity scripting.",
          "https://visualstudio.microsoft.com/vs/unity-tools/",
        ],
      ),
      ("Required: Github", ["GitHub is required for project versioning and collaboration.", "https://github.com/"],),
      ("Required: MecaBricks", ["MecaBricks is used for browser-based 3D modelling.", "https://www.mecabricks.com/en/"],),
      (
        "Useful: Adobe CC and Photoshop",
        [
          "Adobe Creative Cloud and Photoshop are useful for image editing and texture work.",
          "https://www.westminster.ac.uk/current-students/studies/study-skills-and-training/digital-skills/adobe-creative-cloud-for-students",
        ],
      ),
      (
        "Useful: Github CoPilot",
        [
          "GitHub Copilot is useful for assisted coding and development support.",
          "https://github.com/copilot",
          "https://docs.github.com/en/copilot/get-started/plans-for-github-copilot",
          "https://docs.github.com/en/copilot/get-started/best-practices-for-using-github-copilot",
        ],
      ),
    ]
    body = "".join(
      f'''      <details class="accordion">
        <summary>{html.escape(title)}</summary>
        <div class="accordion-body">{render_software_lines(content)}</div>
      </details>'''
      for title, content in sections
    )
    return body
  elif number == 4:
    sections = [
      (
        "First Actions: Unity3D",
        [
          "Allow at least 30 minutes to download, install Unity and the project to be ready to work, depending on your broadband connection.",
          "If you are having trouble with your connection, please contact me or the service desk asap.",
          "The tutorial should take 30-45 minutes.",
          "If you have already installed Visual Studio Code, install the Unity VSCode Extension and check the version of the Visual Studio Editor you have.",
        ],
      ),
      (
        "Unity3D Install: Setup a Unity ID and a Student Account",
        [
          "Setup a Unity ID and a Student Account:",
          "https://id.unity.com/en/conversations/501975b1-9ab1-4599-b9f1-72fa4235b61d01bf",
          "https://unity.com/products/unity-student?currency=EUR",
          "Download Unity Hub by clicking the Unity Hub button at https://store.unity.com/download-nuo",
          "Download Unity version 6000.0.55f1 at: https://unity3d.com/get-unity/download/archive",
        ],
      ),
      (
        "Unity3D Install: Extra: Start some Unity3D Basics Tutorials:",
        [
          "Open Welcome to Unity Essentials from the Unity Learn Tab in Unity Hub, or link directly here: https://learn.unity.com/pathway/unity-essentials",
          "Work the tutorial within the project. Save the project to keep working by closing the project and selecting Keep in the prompt.",
          "Build and share the tutorial game on Unity Play or https://get.simmer.io/",
          "Share link to Padlet: https://uowdigital.padlet.org/fergusj/AIMDUnityLearn",
        ],
      ),
      (
        "Visual Studio 2026 Community Install",
        [
          "Install Visual Studio and update the Visual Studio Editor package for Unity using the links below.",
          "https://visualstudio.microsoft.com/vs/unity-tools/",
          "Make sure Visual Studio Editor in the Unity Package Manager is updated to version 20.0.22.",
        ],
      ),
      (
        "Github/GitHub CoPilot Install",
        [
          "GitHub and Copilot within Visual Studio are used for group project versioning from Week 2 onwards.",
          "Signup: https://docs.github.com/en/education/about-github-education/github-education-for-students/apply-to-github-education-as-a-student",
          "Copilot Signup: https://github.com/copilot",
          "https://docs.github.com/en/copilot/get-started/plans-for-github-copilot",
          "https://docs.github.com/en/copilot/get-started/best-practices-for-using-github-copilot",
        ],
      ),
    ]
    return "".join(
      f'''      <details class="accordion">
        <summary>{html.escape(title)}</summary>
        <div class="accordion-body">{render_software_lines(content)}</div>
      </details>'''
      for title, content in sections
    )
  else:
    title = "Software Required"
    body = render_software_lines(slide.get("content", []))

  return f'''      <details class="accordion">
    <summary>{title}</summary>
    <div class="accordion-body">{body}</div>
    </details>'''

body_class = "lecture-fullbleed software-required" if args.lecture_id == "software-required" else "lecture-fullbleed"
content_class = "slide-content slide-content-accordion" if args.lecture_id == "software-required" else "slide-content"

html_template = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>3DIMD | __LECTURE_TITLE__</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap\" rel=\"stylesheet\" />
  <link rel=\"stylesheet\" href=\"../assets/css/site.css?v=20260818a" />
    <link rel=\"stylesheet\" href=\"../assets/css/slideshow.css?v=20260818a" />
</head>
<body class=\"__BODY_CLASS__\">
  <div class=\"slideshow-container\">
"""

html_template = html_template.replace("__BODY_CLASS__", body_class)
html_template = html_template.replace("__CONTENT_CLASS__", content_class)

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
    if args.lecture_id == "software-required":
      content_html = (
        f"    <h2>{html.escape(display_title or 'Software Required')}</h2>\n"
        "    <div class=\"accordion-scroll\">\n"
        f"{build_software_section(slide)}\n"
        "    </div>\n"
      )
    elif display_title:
      content_html += f"    <h2>{display_title}</h2>\n"

    if content and args.lecture_id != "software-required":
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

    if args.lecture_id != "software-required":
      for img in images:
        content_html += f"    <img src=\"images/{img['filename']}\" alt=\"Slide {slide_num} image\" />\n"

    html_template += f"""    <!-- Slide {slide_num} -->
    <div class=\"slide{"" if slide_num != 1 else " active"}\">
      <div class=\"slide-title\">{args.module_title}</div>
      <div class=\"{content_class}\">
{content_html}      </div>
      <div class=\"slide-controls\">
        <button class=\"slide-button\" data-slide-step="-1"{"" if slide_num > 1 else " disabled"}> ← Previous</button>
        <img src=\"../images/UOW_Logo_Length_Alpha.png\" class=\"slide-logo\" alt=\"University of Westminster\" />
        <button class=\"slide-button\" data-slide-step="1"{"" if slide_num < len(slides_data) else " disabled"}>Next → </button>
        <div class=\"slide-counter\"><span id=\"current-slide-{slide_num}\">{slide_num}</span> / <span id=\"total-slides\">{len(slides_data)}</span></div>
      </div>
      <div class=\"keyboard-hint\">
        Use <kbd>→</kbd> <kbd>←</kbd> or click buttons to navigate
      </div>
    </div>

"""

html_template += """  </div>

  <script src=\"../assets/js/site.js?v=20260818a"></script>
  <script>
    const isLecturePage = /\\/(?:lect-[^/]+|software-required)\\.html$/i.test(window.location.pathname);
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
      const youtubePattern = /^https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([^\s&?]+)(.*)$/i;
      const panoptoPattern = /^https?:\/\/([^\s/]+\.panopto\.eu)\/Panopto\/Pages\/Viewer\.aspx\?id=([^\s&]+)/i;
      slide.querySelectorAll('.accordion-body > p').forEach((paragraph) => {
        const sourceUrl = paragraph.textContent.trim();
        const youtubeMatch = sourceUrl.match(youtubePattern);
        const panoptoMatch = sourceUrl.match(panoptoPattern);
        if (!youtubeMatch && !panoptoMatch) return;

        const previous = paragraph.previousElementSibling;
        const context = previous ? previous.textContent.replace(/\s+/g, ' ').trim() : '';
        const host = panoptoMatch ? panoptoMatch[1] : '';
        const videoId = youtubeMatch ? youtubeMatch[1] : panoptoMatch[2];
        const query = youtubeMatch ? (youtubeMatch[2] || '') : '';
        const embedUrl = youtubeMatch
          ? `https://www.youtube.com/embed/${videoId}${query}`
          : `https://${host}/Panopto/Pages/Embed.aspx?pid=${videoId}`;
        const iframeClass = youtubeMatch ? 'video-embed' : 'panopto-embed';
        const authNote = panoptoMatch
          ? '<p class="video-auth-note">Student Panopto login may be required. If the embedded player does not refresh after sign-in, open the source link in a new or incognito window.</p>'
          : '';
        const details = document.createElement('details');
        details.className = 'accordion accordion--nested video-accordion';
        details.innerHTML = `
          <summary>${context || 'Video'}</summary>
          <div class="accordion-body">
            <article class="embed-card">
              <iframe class="${iframeClass}" src="${embedUrl}" title="${context || 'Video'}" loading="lazy" allowfullscreen></iframe>
              ${authNote}
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
