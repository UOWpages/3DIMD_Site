# 3DIMD_Site

Static course site migration output, neobrutalism styling and tooling for 3DIMD 2026-2027.

## Build The Migrated Site

Run the migration pipeline from the repository root:

powershell
./tools/migrate-site.ps1

This generates:

- site/index.html and site/pages/*.html
- site/assets/css/site.css and site/assets/js/site.js
- docs/migration-reference.md
- docs/authoring-guide.md
- reports/validation-report.md

## Notes

- Source DOCX and legacy HTML files remain unchanged.
- Generated pages use one shared stylesheet and one shared layout shell.
- Video embeds are placed in collapsed details sections by default.
