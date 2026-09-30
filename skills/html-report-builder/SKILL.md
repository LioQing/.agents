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
- Read [references/design-system.md](references/design-system.md) before building.
- Use [assets/example-report.html](assets/example-report.html) as the implementation reference, adapting its structure rather than copying its example content.

## Execution Steps

1. **Define the report contract.** Identify the audience, report question, supplied evidence, intended filename, and the sections necessary to answer the question. If details are missing, make conservative assumptions and label illustrative data clearly.
2. **Choose only useful components.** Use prose for explanation, KPI tiles for a few headline numbers, a chart for patterns, a table for exact values, Mermaid for relationships or flow, KaTeX for real equations, and highlighted code for implementation detail. Do not add a component merely to demonstrate it.
3. **Plan one narrative.** Start with the conclusion or executive summary, move through evidence and interpretation, and finish with implications or next actions. Give every major section a stable, kebab-case `id`.
4. **Build one HTML document.** Use semantic `header`, `main`, `section`, `aside`, `nav`, `figure`, `table`, and `footer` elements. Load Tailwind from its CDN and prefer utility classes. Reserve custom CSS for scrollbars, library output, print rules, scroll-spy state, and behavior Tailwind cannot express cleanly.
5. **Match the visual system.** Use a near-black/white neutral palette, hairline borders, compact UI text, restrained corner radii, and ample whitespace. Avoid gradients, glassmorphism, oversized hero text, decorative blobs, and dense dashboard chrome.
6. **Add the right-side navigator.** On large screens, use a sticky narrow `aside` to the right of the reading column. Link to each major section, expose the active section with a slim border or stronger text, use `aria-label="On this page"`, and update state with `IntersectionObserver`. On smaller screens, replace it with a compact `<details>` contents control above the report.
7. **Support both themes.** Set `darkMode: 'class'`, initialize the theme before paint from `localStorage` or `prefers-color-scheme`, provide an accessible toggle, persist the choice, and update Chart.js/Mermaid colors when the theme changes.
8. **Make rich content usable.** Charts need legends, units, tooltips, and a nearby text takeaway. Tables need captions or headings, proper scopes, horizontal overflow, and sorting/filtering only when helpful. Code blocks need language labels, syntax highlighting, and copy buttons. Mermaid and KaTeX content must remain legible in both themes. Render callouts as full-outline rounded rows with a leading semantic Google Material Symbol and concise message; use neutral, success, or warning color according to meaning without relying on color alone. When an interface needs an icon, use an existing Google Material Symbol rather than drawing a custom SVG or glyph.
9. **Cover accessibility, motion, and output.** Maintain visible focus styles, sufficient contrast, keyboard-operable controls, descriptive labels, responsive layout, and print rules that hide controls/navigation and avoid clipped content. Give disclosure widgets and similar interactive content a complete enclosing border, generous click target, distinct open state, and focus-visible ring. Add restrained 120–220ms ease-out transitions for hover, press, theme changes, and disclosure open/close; animate opacity, color, border, or small transforms rather than decorative movement. Preserve native semantics and disable nonessential motion under `prefers-reduced-motion`.
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
- The content column remains comfortable to read, roughly 720–880px, while the right rail stays secondary.
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
- Do not copy OpenAI branding, logos, proprietary navigation, or claim affiliation. The aesthetic reference is a design direction only.

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
