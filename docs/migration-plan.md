# Migration Plan

## Workflow

1. Discover all source files and classify them by audience (students, lecturers, assessment).
2. Convert DOCX sources into semantic HTML blocks with shared component classes.
3. Normalize links, Gyazo references, and video embeds into common media components.
4. Generate one persistent shell page and lightweight content pages with shared stylesheet.
5. Run validation checks and publish a compliance report.

## Information Architecture

- Home: module overview and sitemap
- Students: tutorial pages sourced from student DOCX files
- Lecturers: lecturer guidance pages sourced from lecturer DOCX files
- Assessments: migrated quiz page

## Naming Conventions

- Pages: lowercase kebab-case filename derived from source title, stored in site/pages
- Media assets: site/assets/media/<page-slug>/<original-file>
- Shared assets: site/assets/css/site.css and site/assets/js/site.js
- Section classes: section-card, note, accordion, embed-card, image-figure, link-card

## Shared Component Classes

- Container/layout: module-header, site-shell, nav-rail, content-shell, content-frame, content-area
- Note/callout: note, note--important, note--tip
- Section card: section-card
- Accordion: accordion, accordion-body
- Video embed: video-embed
- Panopto embed: panopto-embed
- Image figure and caption: image-figure, image-caption
- Link card and media list: link-card, media-list

## Content Inventory

| Source file | Target page | Media assets needed | Parsing confidence | Risks / manual review notes |
|---|---|---|---:|---|
| .\Lecturers\Tut 00 01 Lecturer Version.docx | site/pages/tut-00-01-lecturer-version.html | none | 0.92 | Low risk in automated conversion. |
| .\Lecturers\Tut 02 03 Lecturer.docx | site/pages/tut-02-03-lecturer.html | none | 0.92 | Low risk in automated conversion. |
| .\Lecturers\Tut 04 Lecturers.docx | site/pages/tut-04-lecturers.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 00 01 Student Version .docx | site/pages/tut-00-01-student-version.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 02 03 Students.docx | site/pages/tut-02-03-students.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 04 Students.docx | site/pages/tut-04-students.html | assets/media/tut-04-students/* | 0.87 | Image placement inferred into media section, not original in-flow position. |
| .\Tut 05.docx | site/pages/tut-05.html | assets/media/tut-05/* | 0.87 | Image placement inferred into media section, not original in-flow position. |
| .\Tut 07 UI Overview.docx | site/pages/tut-07-ui-overview.html | none | 0.84 | Large number of Gyazo links; preview availability may vary by source asset. |
| .\Tut 08 Character Troubleshooting BB.docx | site/pages/tut-08-character-troubleshooting-bb.html | none | 0.84 | Table semantics converted generically; verify headers. |
| .\Tut 09 10 0 Blender Origins and Pivots Cheatsheet.docx | site/pages/tut-09-10-0-blender-origins-and-pivots-cheatsheet.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 09 10 00 Blender UI Overview.docx | site/pages/tut-09-10-00-blender-ui-overview.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 09 10 01 Blender UI CheatSheet.docx | site/pages/tut-09-10-01-blender-ui-cheatsheet.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 09 10 02 Blender Lego Minifig Tutorial - Startup and Reference Images.docx | site/pages/tut-09-10-02-blender-lego-minifig-tutorial-startup-and-reference-images.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 09 10 03 Blender Lego Minifig Tutorial - Torso and Head.docx | site/pages/tut-09-10-03-blender-lego-minifig-tutorial-torso-and-head.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 09 10 04 Blender Lego Minifig Tutorial - Hips and Legs (2).docx | site/pages/tut-09-10-04-blender-lego-minifig-tutorial-hips-and-legs-2.html | none | 0.86 | Duplicate filename variant detected; confirm canonical source. |
| .\Tut 09 10 04 Blender Lego Minifig Tutorial - Hips and Legs.docx | site/pages/tut-09-10-04-blender-lego-minifig-tutorial-hips-and-legs.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 09 10 05 Blender Lego Minifig Tutorial - Arms and Hands (2).docx | site/pages/tut-09-10-05-blender-lego-minifig-tutorial-arms-and-hands-2.html | none | 0.86 | Duplicate filename variant detected; confirm canonical source. |
| .\Tut 09 10 05 Blender Lego Minifig Tutorial - Arms and Hands.docx | site/pages/tut-09-10-05-blender-lego-minifig-tutorial-arms-and-hands.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 11 01 Blender Materials and Texturing.docx | site/pages/tut-11-01-blender-materials-and-texturing.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 11 02 Blender Pivots and Animation Sheet.docx | site/pages/tut-11-02-blender-pivots-and-animation-sheet.html | none | 0.92 | Low risk in automated conversion. |
| .\Tut 12 URP Lighting 2026.docx | site/pages/tut-12-urp-lighting-2026.html | assets/media/tut-12-urp-lighting-2026/* | 0.87 | Image placement inferred into media section, not original in-flow position. |
| ./Tut 08 Physics Quiz RBCT.html | site/pages/tut-08-physics-quiz-rbct.html | none | 0.98 | Script behavior preserved, but quiz UI was restyled to shared components. |

## Automated Parsing Metrics

| Source file | Paragraphs | Lists | Tables | Images | Links | Gyazo | YouTube | Panopto |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| .\Lecturers\Tut 00 01 Lecturer Version.docx | 337 | 131 | 0 | 0 | 21 | 4 | 1 | 7 |
| .\Lecturers\Tut 02 03 Lecturer.docx | 210 | 75 | 0 | 0 | 15 | 0 | 3 | 4 |
| .\Lecturers\Tut 04 Lecturers.docx | 130 | 52 | 0 | 0 | 7 | 0 | 1 | 5 |
| .\Tut 00 01 Student Version .docx | 236 | 132 | 0 | 0 | 23 | 5 | 1 | 7 |
| .\Tut 02 03 Students.docx | 171 | 79 | 0 | 0 | 18 | 0 | 2 | 5 |
| .\Tut 04 Students.docx | 129 | 46 | 0 | 1 | 7 | 0 | 1 | 5 |
| .\Tut 05.docx | 71 | 59 | 0 | 4 | 4 | 1 | 0 | 3 |
| .\Tut 07 UI Overview.docx | 144 | 89 | 0 | 0 | 36 | 34 | 1 | 0 |
| .\Tut 08 Character Troubleshooting BB.docx | 50 | 43 | 1 | 0 | 5 | 0 | 3 | 0 |
| .\Tut 09 10 0 Blender Origins and Pivots Cheatsheet.docx | 44 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| .\Tut 09 10 00 Blender UI Overview.docx | 89 | 75 | 0 | 0 | 1 | 0 | 0 | 1 |
| .\Tut 09 10 01 Blender UI CheatSheet.docx | 87 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| .\Tut 09 10 02 Blender Lego Minifig Tutorial - Startup and Reference Images.docx | 85 | 0 | 0 | 0 | 2 | 1 | 0 | 1 |
| .\Tut 09 10 03 Blender Lego Minifig Tutorial - Torso and Head.docx | 124 | 0 | 0 | 0 | 8 | 3 | 0 | 5 |
| .\Tut 09 10 04 Blender Lego Minifig Tutorial - Hips and Legs (2).docx | 119 | 0 | 0 | 0 | 13 | 13 | 0 | 0 |
| .\Tut 09 10 04 Blender Lego Minifig Tutorial - Hips and Legs.docx | 120 | 0 | 0 | 0 | 13 | 13 | 0 | 0 |
| .\Tut 09 10 05 Blender Lego Minifig Tutorial - Arms and Hands (2).docx | 113 | 84 | 0 | 0 | 13 | 13 | 0 | 0 |
| .\Tut 09 10 05 Blender Lego Minifig Tutorial - Arms and Hands.docx | 122 | 91 | 0 | 0 | 15 | 15 | 0 | 0 |
| .\Tut 11 01 Blender Materials and Texturing.docx | 79 | 69 | 0 | 0 | 7 | 6 | 0 | 0 |
| .\Tut 11 02 Blender Pivots and Animation Sheet.docx | 178 | 23 | 0 | 0 | 3 | 3 | 0 | 0 |
| .\Tut 12 URP Lighting 2026.docx | 142 | 127 | 0 | 2 | 16 | 8 | 7 | 0 |
| ./Tut 08 Physics Quiz RBCT.html | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
