#!/usr/bin/env python3
"""Convert extracted PowerPoint JSON to HTML slideshow"""

import json
from pathlib import Path

# Load the extracted content
json_path = Path(__file__).parent / "site" / "lectures" / "lect-01a-content.json"
with open(json_path, 'r', encoding='utf-8') as f:
    slides_data = json.load(f)

# Generate HTML
html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>3DIMD | Lecture 01a - Module Info</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../assets/css/site.css?v=20260805l" />
  <link rel="stylesheet" href="../assets/css/slideshow.css" />
  <style>
    .slide h1 {
      font-family: "Archivo Black", "Space Grotesk", sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      font-size: clamp(1.8rem, 5vw, 3rem);
      margin: 0 0 var(--space-3) 0;
      line-height: 1.2;
      color: var(--ink);
    }

    .slide h2 {
      font-family: "Archivo Black", "Space Grotesk", sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      font-size: clamp(1.4rem, 3vw, 2rem);
      margin: var(--space-3) 0;
      color: var(--ink);
    }

    .slide h3 {
      font-family: "Space Grotesk", sans-serif;
      font-weight: 700;
      font-size: 1.1rem;
      margin: var(--space-3) 0 var(--space-2) 0;
      color: var(--ink);
      text-transform: uppercase;
      letter-spacing: 0.01em;
    }

    .slide p {
      font-size: 0.95rem;
      line-height: 1.6;
      margin: var(--space-2) 0;
      color: var(--muted);
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .learning-outcome {
      font-size: 0.9rem;
      margin: var(--space-2) 0;
      padding-left: var(--space-3);
    }

    .module-aim {
      font-size: 0.85rem;
      margin: var(--space-2) 0;
      padding-left: var(--space-3);
      line-height: 1.5;
    }

    .section-label {
      font-weight: 700;
      font-size: 1rem;
      margin: var(--space-3) 0 var(--space-2) 0;
      color: var(--ink);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .slide img {
      max-width: 100%;
      height: auto;
      border: 2px solid var(--line);
      border-radius: var(--radius-sm);
      box-shadow: 4px 4px 0 var(--line);
      margin: var(--space-3) auto;
      display: block;
    }

    .slide-logo {
      height: 2rem;
      width: auto;
      border: none;
      border-radius: 0;
      box-shadow: none;
      margin: 0;
      mix-blend-mode: multiply;
    }

    img.slide-logo {
      height: 2rem;
      border: none;
      border-radius: 0;
      box-shadow: none;
      margin: 0;
    }

    .slide ul, .slide ol {
      margin: var(--space-2) 0;
      padding-left: var(--space-4);
    }

    .slide li {
      margin: 0.5rem 0;
      line-height: 1.6;
      font-size: 0.95rem;
    }

    a {
      color: var(--accent-alt);
      text-decoration: underline;
    }

    a:hover {
      color: var(--accent);
    }
  </style>
</head>
<body>
  <div class="slideshow-container">
'''

# Generate slides
for slide in slides_data:
    slide_num = slide['slide_number']
    content = slide['content']
    images = slide['images']
    
    # Format content with smart typography
    content_html = ""
    if content:
        is_first_heading = True
        for idx, text in enumerate(content):
            if text.strip() == "3D Interactive Media Development":
                continue  # Skip module title as it's now in slide-title
            
            # Split text into lines
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line == "":
                    continue
                
                # First substantive line is slide heading
                if is_first_heading:
                    content_html += f'    <h2>{line}</h2>\n'
                    is_first_heading = False
                    continue
                
                # Lines ending with colon are section headers
                if line.endswith(':'):
                    content_html += f'    <h3>{line}</h3>\n'
                # Lines starting with LO are learning outcomes
                elif line.startswith('LO'):
                    content_html += f'    <p class="learning-outcome"><strong>{line}</strong></p>\n'
                # Lines starting with L5- are module aims
                elif line.startswith('L5-'):
                    content_html += f'    <p class="module-aim"><strong>{line}</strong></p>\n'
                # Lines that are short, all caps (likely section labels)
                elif line.isupper() and len(line) < 50 and len(line.split()) <= 3:
                    content_html += f'    <p class="section-label">{line}</p>\n'
                else:
                    content_html += f'    <p>{line}</p>\n'
    
    # Add images
    for img in images:
        content_html += f'    <img src="images/{img["filename"]}" alt="Slide {slide_num} image" />\n'
    
    html_template += f'''    <!-- Slide {slide_num} -->
    <div class="slide{"" if slide_num != 1 else " active"}">
      <div class="slide-title">3D Interactive Media Development</div>
      <div class="slide-content">
{content_html}      </div>
      <div class="slide-controls">
        <button class="slide-button" onclick="changeSlide(-1)"{"" if slide_num > 1 else " disabled"}> ← Previous</button>
        <img src="../images/UOW_Logo_Length_Alpha.png" class="slide-logo" alt="University of Westminster" />
        <button class="slide-button" onclick="changeSlide(1)"{"" if slide_num < len(slides_data) else " disabled"}>Next → </button>
        <div class="slide-counter"><span id="current-slide-{slide_num}">{slide_num}</span> / <span id="total-slides">{len(slides_data)}</span></div>
      </div>
      <div class="keyboard-hint">
        Use <kbd>→</kbd> <kbd>←</kbd> or click buttons to navigate
      </div>
    </div>

'''

html_template += '''  </div>

  <script src="../assets/js/site.js?v=20260805f"></script>
  <script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;

    // Convert URLs in text nodes to clickable links
    function linkifyText(element) {
      const urlPattern = /(https?:\/\/[^\s]+)/g;
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

      nodesToReplace.forEach(textNode => {
        const span = document.createElement('span');
        span.innerHTML = textNode.textContent.replace(
          /(https?:\/\/[^\s]+)/g,
          '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        textNode.parentNode.replaceChild(span, textNode);
      });
    }

    // Initialize URL linking for all slides
    slides.forEach(slide => {
      linkifyText(slide);
    });

    // Update slide counter display
    function updateCounters() {
      const counter = document.querySelector('.slide-counter');
      if (counter) {
        counter.textContent = `${currentSlide + 1} / ${totalSlides}`;
      }
    }

    function showSlide(n) {
      slides.forEach(slide => slide.classList.remove('active'));
      slides[currentSlide].classList.add('active');
      
      // Update button states
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
    }

    function changeSlide(n) {
      currentSlide += n;
      if (currentSlide >= totalSlides) currentSlide = totalSlides - 1;
      if (currentSlide < 0) currentSlide = 0;
      showSlide(currentSlide);
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') changeSlide(1);
      if (e.key === 'ArrowLeft') changeSlide(-1);
    });

    // Initialize
    showSlide(currentSlide);
  </script>
</body>
</html>'''

# Write output
output_file = Path(__file__).parent / "site" / "lectures" / "lect-01a.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"Generated slideshow with {len(slides_data)} slides")
print(f"Saved to: {output_file}")
