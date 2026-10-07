---
name: html-report-builder
description: Build a polished single-page HTML report when the user wants research, analysis, metrics, comparisons, or technical findings presented as a standalone web page. Use for reports needing Tailwind CSS, charts, diagrams, tables, math, code, light/dark mode, and a sticky right-side section navigator.
---

# HTML Report Builder

## Overview

Create one polished, portable HTML report that turns supplied facts and data into a readable narrative. The visual language should feel like modern developer documentation: quiet neutral surfaces, precise typography, thin rules, compact controls, generous space, and restrained accent color.

Deliver a single `.html` file. Do not create a site shell, top navigation, or left sidebar. Keep a section navigator on the right at desktop widths.

## Prerequisites

- A browser for visual review.
- Internet access when using CDN-hosted Tailwind CSS, Chart.js, Mermaid, KaTeX, or Highlight.js.
- The user's source data, claims, citations, and code. Do not invent factual report content.
- Read all of [DESIGN.md](DESIGN.md) before building. It is the authoritative design contract in Google's DESIGN.md format, with exact tokens, component rules, responsive behavior, themes, fallbacks, and print styling.
- Read [assets/example-report.html](assets/example-report.html), then reuse its matching markup, embedded styles, and behaviors. Replace illustrative content/data and omit irrelevant showcase components; do not reinterpret the design.

## Execution Steps

1. **Define the report contract.** Identify the audience, report question, supplied evidence, intended filename, and the sections necessary to answer the question. If details are missing, make conservative assumptions and label illustrative data clearly.
2. **Choose only useful components.** Use prose for explanation, KPI tiles for a few headline numbers, a chart for patterns, a table for exact values, Mermaid for relationships or flow, KaTeX for real equations, and highlighted code for implementation detail. Do not add a component merely to demonstrate it.
3. **Plan one narrative.** Start with the conclusion or executive summary, move through evidence and interpretation, and finish with implications or next actions. Give every major section a stable, kebab-case `id`.
4. **Build one HTML document.** Preserve the example's semantic layout, CSS-variable token mapping, reusable component classes, and embedded fallback styles. Use Tailwind utilities for incidental layout, not competing component skins. All report data and initialization stay inside the document.
5. **Apply the design contract without design decisions.** Use the exact values and patterns in DESIGN.md. Decide only content, section names, and which evidence-backed components are useful. Do not select alternate palettes, fonts, layouts, radii, chart skins, or navigation patterns. Explicit user design overrides take precedence. For a genuinely essential interactive element with no defined pattern, ask rather than inventing a new design.
6. **Add the right-side navigator.** On large screens, use a sticky narrow `aside` to the right of the reading column. Link to each major section, expose the active section with a slim border or stronger text, use `aria-label="On this page"`, and update state with `IntersectionObserver`. On smaller screens, replace it with a compact `<details>` contents control above the report.
7. **Support both themes.** Set `darkMode: 'class'`, initialize the theme before paint from `localStorage` or `prefers-color-scheme`, provide an accessible toggle, persist the choice, and update Chart.js/Mermaid colors when the theme changes.
8. **Make rich content usable.** Follow DESIGN.md's exact chart/diagram/math/code/table/disclosure patterns. Preserve exact chart values in accessible tables, prose diagram equivalents, math symbol definitions, status announcements, and labeled fallbacks. Use the six defined admonition types and existing Material Symbols. Include filters, forms, tooltips, progress, images, or dialogs only when the report content actually needs them, not to reproduce the showcase.
9. **Cover accessibility, motion, and output.** Preserve DESIGN.md's exact focus, hit-target, disclosure, motion, reduced-motion, fallback, and print behavior. Keep native semantics and ensure reading remains useful when a CDN fails.
10. **Validate.** Open the file in a browser at desktop and mobile widths. Test theme persistence, all section links, active navigation, chart rendering, Mermaid, math, table behavior, code copying, no-console-error behavior, and printing. Confirm the page still presents a useful reading order if a CDN is unavailable.

## Default Dependencies

Use versioned CDN URLs when practical:

- Tailwind CSS for layout and styling.
- Chart.js for interactive charts.
- Mermaid for flowcharts and relationship diagrams.
- KaTeX with auto-render for mathematics.
- Highlight.js for syntax highlighting.

Keep all report data and initialization code inside the HTML file. If the user requires fully offline output, vendor or inline the dependencies and document the increased file size.

## Quality Bar

- The first viewport states the topic, date/context, executive takeaway, and key metrics without feeling like a marketing landing page.
- The exact responsive frame, typography, component tokens, and right-side navigation match DESIGN.md and its showcase.
- Every visualization answers a stated question and has a prose interpretation.
- Exact values remain available in text or a table; never make a chart the only representation of critical data.
- Light and dark modes are deliberately styled, not merely color-inverted.
- The report has no placeholder copy, broken anchors, horizontal page overflow, or unnecessary application chrome.

## Error Handling and Limitations

- If data is incomplete, show `N/A`, state the limitation, or omit the component. Never fabricate missing measurements.
- If a library fails to load, keep the written takeaway and accessible table visible. Show a short fallback message in the affected figure.
- If Mermaid cannot safely express a complex diagram, use semantic HTML/CSS or an accessible SVG with a text description.
- If a table is very large, summarize it in the report and provide the raw data separately rather than rendering thousands of rows.
- Do not fetch private data from the page at runtime. Embed only data the user authorized for the report.
- Do not copy Google/OpenAI branding, logos, proprietary navigation, or claim affiliation. Google's DESIGN.md supplies the file format, not a replacement brand aesthetic.

## Concrete Example

User prompt:

```text
Create a single-page HTML report from quarterly-metrics.csv. Lead with the three most important findings, chart revenue and churn by quarter, include a sortable regional table, show the data pipeline as a diagram, and put the retention formula in math notation. Save it as outputs/q3-business-review.html.
```

Expected behavior:

```text
The agent verifies the CSV fields, builds one responsive HTML file, uses a sticky right-side section navigator, includes only evidence-backed metrics, supports light/dark mode and print, tests every interaction, and returns a link to the completed report.
```

## Test Prompt

```text
Use the html-report-builder skill to turn the supplied API reliability metrics into one standalone HTML report. Include an executive summary, KPI cards, a weekly latency chart, a sortable endpoint table, a Mermaid incident-response flow, a KaTeX error-budget equation, and a copyable Python snippet. Use light/dark mode and a right-side section navigator.
```
