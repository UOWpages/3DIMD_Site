#!/usr/bin/env python3
"""Extract content and images from PowerPoint file"""

import os
import sys

# Try to import pptx, install if needed
try:
    from pptx import Presentation
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx", "Pillow", "-q"])
    from pptx import Presentation

import json
from pathlib import Path

pptx_path = Path(__file__).parent / "site" / "lectures" / "3DIMD Lecture 01a Module Info 01.pptx"
output_dir = Path(__file__).parent / "site" / "lectures" / "images"
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Extracting from: {pptx_path}")

prs = Presentation(str(pptx_path))
slides_data = []

for slide_num, slide in enumerate(prs.slides, 1):
    slide_content = {
        "slide_number": slide_num,
        "title": "",
        "content": [],
        "images": []
    }
    
    # Extract text and shapes
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            text = shape.text.strip()
            if shape.name.startswith("Title"):
                slide_content["title"] = text
            else:
                slide_content["content"].append(text)
        
        # Extract images
        if shape.shape_type == 13:  # Picture
            try:
                image = shape.image
                image_filename = f"slide{slide_num}_image{len(slide_content['images'])}.png"
                image_path = output_dir / image_filename
                
                with open(image_path, 'wb') as f:
                    f.write(image.blob)
                
                slide_content["images"].append({
                    "filename": image_filename,
                    "path": f"images/{image_filename}"
                })
                print(f"  Saved image: {image_filename}")
            except Exception as e:
                print(f"  Error saving image: {e}")
    
    slides_data.append(slide_content)
    print(f"Slide {slide_num}: {slide_content['title']}")

# Output as JSON for easy review
output_file = Path(__file__).parent / "site" / "lectures" / "lect-01a-content.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(slides_data, f, indent=2, ensure_ascii=False)

print(f"\nExtracted {len(slides_data)} slides")
print(f"Content saved to: {output_file}")
print("\nSlide Summary:")
for slide in slides_data:
    print(f"\nSlide {slide['slide_number']}: {slide['title']}")
    for line in slide['content']:
        print(f"  - {line[:80]}")
    if slide['images']:
        print(f"  Images: {len(slide['images'])}")
