# Lecture Conversion Playbook

Version: 1.3-draft
Last Updated: 2026-08-14
Status: Working Draft

## 1. Purpose and Scope
This playbook defines the operational procedure for converting lecture source material, including PPTX-derived content, into final lecture slideshow pages.

Objectives:
1. Produce lecture slides that comply with [final-lecture-template-spec.md](./final-lecture-template-spec.md).
2. Keep edits minimal and traceable.
3. Preserve instructional meaning while improving structure and readability.

In scope:
1. Full lecture conversions.
2. Incremental lecture updates.
3. Schedule, deadline, table, and media normalization.
4. Validation reporting and release gate checks.

Out of scope:
1. Tutorial page conversion workflow.
2. Broad visual redesign unrelated to lecture template conformance.
3. Rewriting pedagogical intent unless explicitly requested.

## 2. Normative References
1. [documentation-hub.md](./documentation-hub.md)
2. [final-lecture-template-spec.md](./final-lecture-template-spec.md)
3. [prompt-strategy-catalog.md](./prompt-strategy-catalog.md)
4. ../site/lectures/lecture-template.html
5. ../site/pages/lect-01a.html (canonical lecture panel implementation)
6. ../site/assets/css/slideshow.css
7. ../.github/copilot-instructions.md

## 3. Inputs, Outputs, and Preconditions
Inputs:
1. Target lecture HTML file.
2. Source PPTX file when available.
3. Extracted source text or JSON artifacts when available.
4. Extracted media asset directory when available.
5. Scope definition: full deck or specific slide range.

Outputs:
1. Updated lecture HTML that passes mandatory checks.
2. Any required scoped CSS changes in shared lecture stylesheet.
3. Conversion report with mapping, PASS/FAIL checklist, and residual risks.

Preconditions:
1. Target file path is confirmed.
2. Conversion scope is confirmed.
3. Lecture-only system boundaries are confirmed.
4. Any known no-touch zones are confirmed.

## 4. Conversion Modes
1. Full conversion: rebuild or rework the whole deck from source references.
2. Incremental update: apply source changes only to impacted slides/components.
3. Patch conversion: resolve identified compliance failures with minimal edits.

## 5. Stage 0: Intake and Scope Lock
Required actions:
1. Confirm lecture target and current baseline state.
2. Confirm source assets and extraction outputs available for use.
3. Confirm scope boundaries by slide index.
4. Confirm conversion mode.
5. Record assumptions before editing.

Exit criteria:
1. Scope and mode are unambiguous.
2. Required source materials are present or exceptions documented.

## 6. Stage 1: Extraction and Source Inventory
Required actions:
1. Build an inventory keyed by source slide or section.
2. Capture text blocks, heading candidates, media references, and date/deadline markers.
3. Record extraction anomalies such as missing media, malformed text, or ambiguous ordering.

Recommended inventory fields:
1. Source index.
2. Candidate target slide index.
3. Content summary.
4. Media references.
5. Schedule or deadline flags.
6. Confidence notes.

Exit criteria:
1. Every scoped source item appears in the inventory.
2. Known anomalies are documented.

## 7. Stage 2: Slide Mapping and Type Classification
Required actions:
1. Map source blocks to target slide positions.
2. Assign one primary slide type per target slide: text, accordion, schedule, table, media-heavy, or reference.
3. Mark merge or split decisions and rationale.

Decision rules:
1. Merge when content belongs to one instructional idea and remains readable with approved component patterns.
2. Split when readability, chronology, or interaction quality degrades.
3. Keep chronology strict for schedule/deadline content.

Exit criteria:
1. Each target slide has a mapped source basis and declared type.
2. Merge or split decisions are recorded.

## 8. Stage 3: Structural Conversion
Required actions:
1. Enforce lecture slide shell and required regions.
2. Ensure each slide conforms to title, content, controls/footer, and keyboard hint contract.
3. Apply allowed wrappers and component blocks for chosen slide type.
4. Remove forbidden wrappers and tutorial-only patterns.

Structural safety rules:
1. Do not remove required controls or counter regions.
2. Do not introduce alternate slide shells that bypass normalization behavior.
3. Keep content order stable unless required by approved merge or split mapping.

Exit criteria:
1. All scoped slides satisfy baseline structural contract.

### 8a. Automated Conversion Tooling (2-step)
This process is implemented as two automated steps that produce a fully compliant
lecture page with no manual re-authoring for the base conversion:

Step 1 — Extraction and structural build (produces plain h2/h3/p/ul slides):
1. `python extract_pptx.py --lecture-id <id> --pptx "<file>.pptx"` — extracts text and
   images from the source PPTX into `site/pages/<id>-content.json` plus
   `site/pages/images/`. Use the system Python interpreter (e.g. `C:\Python312\python.exe`)
   if the repo `.venv` is broken or missing.
2. `python generate_html_slideshow.py --lecture-id <id> --lecture-title "..."` for a
   standard deck, or a custom one-off build script (see `temp/build_lect_02b_03b.py`
   for a worked example) when the source needs extra normalization such as
   whitespace/tab cleanup, bullet-list detection, or a recurring attribution/citation
   line (rendered via the `.slide-citation` class in slideshow.css).

Step 2 — Polish pass (produces the final lect-01a/01b visual/interaction style):
1. `python wrap_code_blocks.py site/pages/<id>.html` — detects contiguous C#/code
   paragraphs and replaces each run inline with a hand-authored `.pseudo-panel`
   (matching the tutorial pseudocode panel styling exactly: chrome with dots/title,
   monospace body, comment/brace/statement/code tone coloring, indent tracking on
   `{`/`}`). The panel is NOT wrapped in its own collapsible `<details>` — it renders
   directly in place so the code is always visible without an extra click.
2. `python accordionize_lecture.py site/pages/<id>.html` — groups each slide's
   content into collapsible `<details class="accordion">` sections keyed by that
   slide's own `<h2>`/`<h3>` headings (used verbatim as `<summary>` labels, minus
   trailing colon), wraps them in `.accordion-scroll`, and sets
   `.slide-content-accordion` on the outer content div. This must run **after**
   `wrap_code_blocks.py`, since it treats already-built `<details>` code blocks as
   atomic units (via div/details-depth balancing) rather than reprocessing their
   contents. It also gives slide body text the same larger font size used in
   lect-01a/01b for free, since that sizing lives on
   `.slide-content .accordion-body p/li/a` in slideshow.css rather than on plain
   `.slide-content p`.
3. Re-run both scripts from a clean Step 1 output rather than re-running them on
   their own prior output — they are not designed to be idempotent on
   already-wrapped/already-accordion-ized content.
4. Manual pass — embed video links: after accordionizing, find any bare video URL
   paragraphs left in an accordion body and replace them in place with embedded
   videos wrapped in nested collapsible `video-accordion` sections. Each video gets
   its own collapsible accordion for a clean, browsable presentation. Keep other
   surrounding `<p>` lines untouched; only the raw video URL lines are replaced.
   Number videos sequentially per slide when a slide has more than one.
   
   **All video types** (YouTube, youtu.be, Panopto, Vimeo, etc.) use this nested
   collapsible pattern:
   ```html
   <details class="accordion accordion--nested video-accordion">
     <summary>Video: <Description or Context from Nearby Text></summary>
     <div class="accordion-body">
       <article class="embed-card">
         <iframe class="video-embed" src="<EMBED_URL>" title="<Slide/Section Heading> video <N>" loading="lazy" allowfullscreen></iframe>
         <p><a href="<WATCH_URL>" target="_blank" rel="noopener noreferrer">Open source link</a></p>
       </article>
     </div>
   </details>
   ```
   
   **YouTube and youtu.be links:**
   - Extract `<VIDEO_ID>` from:
     - `https://www.youtube.com/watch?v=<ID>` → use `<ID>`
     - `https://youtu.be/<ID>` → use `<ID>`
   - `<EMBED_URL>` = `https://www.youtube.com/embed/<VIDEO_ID>`
   - `<WATCH_URL>` = original URL (watch or youtu.be)
   - `class="video-embed"`
   
   **Panopto links:**
   - Extract `<UUID>` from the Panopto URL's `id=` parameter
   - `<EMBED_URL>` = `https://westminster.cloud.panopto.eu/Panopto/Panopto/Pages/Embed.aspx?id=<UUID>`
   - `<WATCH_URL>` = `https://westminster.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=<UUID>`
   - `class="panopto-embed"`
   
   **Other video hosts (Vimeo, etc.):**
   - Use the standard embed URL provided by the host
   - `class="video-embed"`
   
   **Summary text guidance:**
   Infer video content from nearby text/headings. Examples:
   - "Create (Legacy) and call from other script" → "Video: Create (Legacy) and call from other script"
   - "Animator states" section → "Video: Animator states setup"
   - When context unclear, use generic "Video 1", "Video 2", etc.
   
5. Add the new page's nav entry under `.nav-group[data-nav-group="lectures"]` in
   `site/index.html`, and bump the `?v=` query string on any shared CSS/JS files
   that were touched.

## 9. Stage 4: Content Normalization
Required actions:
1. Normalize headings and body text for clarity and scanability.
2. Preserve instructional meaning and intent.
3. Convert dense blocks into approved components where needed.
4. Normalize schedule text into week cards and deadline callouts where applicable.
5. When creating accordion summaries, infer section labels from nearby headings before using generic defaults.

Content constraints:
1. Preserve chronology for schedule content.
2. Avoid stylistic rewrites that alter teaching intent.
3. Keep terminology consistent within the lecture.
4. If no reliable local heading exists for an accordion summary, use an explicit override label.

Exit criteria:
1. Content is readable, structured, and aligned to slide type.

## 10. Stage 5: Media and Embed Handling
Required actions:
1. Place images in source-relevant in-flow positions.
2. Preserve source sequence unless a justified structural split requires repositioning.
3. Ensure external links follow safe attribute patterns.
4. Ensure embeds use approved containment patterns and loading behavior.

Media handling constraints:
1. Avoid duplicate media insertion unless pedagogically required.
2. Record missing or unresolved assets in risk notes.

Exit criteria:
1. Media and embeds are correctly placed and compliant.

## 11. Stage 6: CSS and JS Alignment
Required actions:
1. Reuse existing slideshow component classes first.
2. Add new classes only when reusable and scoped.
3. Preserve navigation behavior, counter behavior, and control states.
4. Preserve normalization idempotency.

JS alignment checks:
1. Previous and next state behavior remains correct on first and last slides.
2. Keyboard navigation behavior remains intact.
3. Counter updates consistently after navigation.

Exit criteria:
1. No regression in shared lecture behavior.
2. No unscoped CSS side effects.

## 12. Stage 7: Verification and Release Gate
Run mandatory checks and report PASS/FAIL for each:
1. Slide shell and required-region compliance.
2. Slide-type pattern compliance.
3. Overflow and scrolling compliance.
4. Typography and readability consistency.
5. Schedule and deadline component compliance.
6. Table component compliance when applicable.
7. Link and embed safety compliance.
8. Navigation, keyboard, and counter behavior compliance.
9. Footer/logo/control arrangement consistency.
10. Accessibility baseline compliance.
11. No tutorial pattern contamination.
12. No unscoped style or behavior regressions.

Release gate policy:
1. Mandatory items must all PASS before release.
2. Any accepted exception must be explicit and documented.

## 13. Stop-and-Ask Triggers
Stop and request clarification when:
1. Source chronology conflicts with existing lecture chronology.
2. Critical media is missing and placement cannot be inferred safely.
3. Mapping is ambiguous across multiple plausible slide types.
4. Requested edits conflict with final lecture template requirements.
5. Completing the request requires non-minimal refactor beyond approved scope.

## 14. Minimal-Diff Enforcement
1. Edit only scoped lecture files and required shared lecture assets.
2. Do not refactor unrelated sections.
3. Do not normalize formatting globally unless required to fix a compliance issue.
4. Preserve existing compliant behavior and content unchanged.

## 15. Compliance Reporting Format
Every conversion run must output:
1. Scope summary: target file, slide range, and conversion mode.
2. Source summary: source artifacts used and inventory status.
3. Mapping summary: source-to-slide mapping decisions including merges and splits.
4. Checklist summary: PASS/FAIL for all mandatory checks.
5. Change summary: files changed and minimal-diff rationale.
6. Risk summary: assumptions, exceptions, unresolved blockers.

## 16. Pairing Matrix to Final Lecture Template Spec
1. [Lecture Architecture Contract](./final-lecture-template-spec.md) maps to Stage 2 and Stage 3.
2. [HTML Rules](./final-lecture-template-spec.md) map to Stage 4 and Stage 5.
3. [CSS Rules](./final-lecture-template-spec.md) map to Stage 6.
4. [JS Rules](./final-lecture-template-spec.md) map to Stage 6 and Stage 7 behavior checks.
5. [Accessibility Requirements](./final-lecture-template-spec.md) map to Stage 7.
6. [Validation Checklist](./final-lecture-template-spec.md) maps directly to Stage 7 release gate.
7. [Anti-Patterns](./final-lecture-template-spec.md) map to Stage 3, Stage 6, and Stage 14 enforcement.
8. [Compliance Reporting Format](./final-lecture-template-spec.md) maps to Stage 15 outputs.

## 17. Governance
1. Keep this playbook synchronized with [final-lecture-template-spec.md](./final-lecture-template-spec.md).
2. Update [prompt-strategy-catalog.md](./prompt-strategy-catalog.md) when playbook stages or checks change.
3. Version and date each revision.
4. Record material process changes in the change log.

## 18. Change Log
- 1.3-draft: Formalized the conversion into a repeatable 2-step process (documented in section 8a): Step 1 (extract_pptx.py + generate_html_slideshow.py or a custom build script) produces plain structural slides (h2/h3/p/ul); Step 2 (wrap_code_blocks.py + accordionize_lecture.py, promoted from one-off temp/ scripts to permanent root-level tooling) polishes them into the lect-01a/01b visual style — code snippets become collapsible pseudo-panel-styled blocks, and each slide's h3-delimited content is grouped into collapsible accordion sections (using the slide's own h2/h3 headings as section names), which also gives slide body text the same font sizing as lect-01a/01b for free.
- 1.2-draft: Milestone — first full PPTX-to-HTML lecture conversion executed end-to-end via extract_pptx.py + a JSON-to-slide builder script, producing site/pages/lect-02b-03b.html (75 slides, 24 images) with 1:1 slide mapping, list/heading/citation normalization, and no manual re-authoring required. Added the reusable `.slide-citation` component class to slideshow.css for recurring source attribution lines.
- 1.1-draft: Updated canonical lecture reference to site/pages/lect-01a.html and aligned playbook with full-bleed lecture panel behavior.
- 1.0-draft: Expanded from skeleton to full operational draft aligned 1:1 with final lecture template spec.
- 0.1-draft: Initial skeleton.
