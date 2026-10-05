# Authoring Guide

## Goal

Keep all future additions normalized, semantic, and compatible with the shared style system.

## Precedence For Tutorial Pages

- For tutorial page structure and pseudo-code formatting, [docs/tutorial-layout-prompt.md](./tutorial-layout-prompt.md) is the authoritative rule set.
- If this guide conflicts with that prompt on tutorial pages, follow the tutorial layout prompt.

## Required Structure

1. Use the shared persistent shell page and shared stylesheet only.
2. Use shared content wrappers/classes, but do not add extra `section-card` wrappers when tutorial layout rules prohibit them.
3. Use semantic tags only: h1-h3, p, ul, ol, figure, details/summary, iframe, section, nav, main.
4. Keep all video iframes inside collapsed details sections (no open attribute).
5. Preserve source-accurate HTML indentation and nested-list structure for readability; do not flatten or reflow markup unless required for a fix.
6. For readability, use one-line markup for simple text-only `li` and `h3` elements (for example `<li>content</li>`, `<h3>Heading</h3>`), while keeping multi-line formatting for nested/complex content.
7. When tutorial content is organized into major numbered tasks, each major numbered task should be represented as its own top-level accordion section, with its subtasks and media kept inside the matching section.

## Allowed Components

- Notes: note, note--important, note--tip
- Accordions: accordion with summary and accordion-body
- Embeds: video-embed for YouTube/Vimeo, panopto-embed for Panopto
- Media links: media-list and link-card
- Images: image-figure with image-caption

## Banned Patterns

- Inline style attributes
- Per-page style blocks
- Word-export markup and class names
- Layout deviations from the shared shell/content page templates
- Mojibake or other encoding-corrupted text; keep page content UTF-8 clean.

## Media Handling Rules

1. **YouTube/youtu.be links:** convert to an embed iframe wrapped in a nested
   collapsible `<details class="accordion accordion--nested video-accordion">` section
   with `class="video-embed"` on the iframe, `loading="lazy"` and `allowfullscreen` attributes.
   Each video gets its own collapsible accordion with a descriptive summary label.
2. **Panopto links:** convert to an embed iframe with the same nested video-accordion
   collapsible pattern, using `class="panopto-embed"` on the iframe, with
   `/Panopto/Pages/Embed.aspx?id=<UUID>&autoplay=false&offerviewer=true&showtitle=true&showbrand=true&captions=true&interactivity=all`
   embed URL and `/Viewer.aspx?id=<UUID>` fallback watch link.
   Student authentication may require opening the Viewer fallback in a normal or
   incognito browser window.
3. **Other video hosts (Vimeo, etc.):** use the host's standard embed URL with the same
   nested video-accordion collapsible pattern, `class="video-embed"`, `loading="lazy"`,
   and `allowfullscreen` attributes.
4. Other media links: use link-card entries in a media-list.
5. Gyazo links: use preview image when possible, with a clickable fallback link.
6. Site-wide image interaction: clicking embedded figure images opens an expanded image overlay; clicking the expanded image/overlay closes it.
7. Caption wording for Gyazo previews: use "Gyazo preview (click image to expand)."
8. External links should include `target="_blank"` and `rel="noopener noreferrer"` together when they point off-site.

## Website Cards

Use the existing `.embed-card` styling for website references. Place the card
inside the relevant existing accordion body; do not add tutorial wrappers or
change lecture assets just to embed a website. These patterns are for websites,
not a replacement for the video-specific components above.

### Option 1: Embedded Website With a Fallback Link

Use this when the destination permits iframe embedding. Prefer the provider's
official embed URL when one is available. Replace both URLs and the iframe title
with the intended destination and a descriptive name.

```html
<article class="embed-card">
  <iframe
    src="https://example.com/"
    title="Website presentation"
    loading="lazy">
  </iframe>
  <p>
    <a href="https://example.com/"
       target="_blank"
       rel="noopener noreferrer">
      Open website in a new tab
    </a>
  </p>
</article>
```

Keep the fallback link visible even when embedding works. Add iframe permissions
only when required by the provider; no additional CSS is needed for this pattern.
Test the iframe on the hosted site, not only from a local file.

### Option 2: Link-Only Website Card

Use this when the destination blocks embedding, requires a normal browser window,
or has no suitable embed endpoint. Remove the iframe and retain the card and link.

```html
<article class="embed-card">
  <p>
    <a href="https://example.com/"
       target="_blank"
       rel="noopener noreferrer">
      Open website in a new tab
    </a>
  </p>
</article>
```

A "refused to connect" message can indicate that the destination restricts
embedding through `X-Frame-Options` or CSP `frame-ancestors`. For example,
`blaurel.medium.com` returned `X-Frame-Options: SAMEORIGIN`, preventing this
site from embedding its article. HTML, CSS, iframe permissions, and hosting
changes on this site cannot override the destination's restriction.

The link-only card is a manual authoring alternative, not an automatic fallback:
an iframe `load` event does not reliably prove that a cross-origin website
rendered successfully. Verify the external link independently.

## QA Checklist

1. No style="..." attributes in generated page HTML.
2. No style blocks in page HTML.
3. Shared stylesheet linked correctly.
4. site-shell on index and content-page class on tutorial pages.
5. No details open by default.
6. No iframe outside details.
7. Embedded figure images use click-to-expand overlay behavior.
8. Gyazo preview captions use "click image to expand" wording.
9. External links include `target="_blank"` and `rel="noopener noreferrer"` together.
10. Page text remains UTF-8 clean with no mojibake.
11. Simple text-only `li` items are formatted on one line.
12. Simple text-only `h3` headings are formatted on one line.
13. Major numbered tutorial tasks are represented as top-level sections where applicable, and task content remains inside the matching section.
