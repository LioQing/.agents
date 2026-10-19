---
version: alpha
name: Northstar Slides
description: A fixed-canvas presentation adaptation of the Northstar report aesthetic, with quiet developer-documentation typography, zinc neutrals, thin rules, and restrained blue data accents.
colors:
  primary: "#09090b"
  secondary: "#3f3f46"
  tertiary: "#1d4ed8"
  neutral: "#ffffff"
  muted: "#71717a"
  description: "#52525b"
  border: "#e4e4e7"
  control-border: "#d4d4d8"
  hover: "#f4f4f5"
  focus: "#52525b"
  tip: "#1a7f37"
  important: "#8250df"
  warning: "#b45309"
  warning-border: "#fcd34d"
  danger: "#b91c1c"
  danger-border: "#fca5a5"
  success: "#047857"
  dark-primary: "#f4f4f5"
  dark-secondary: "#d4d4d8"
  dark-tertiary: "#60a5fa"
  dark-neutral: "#000000"
  dark-muted: "#a1a1aa"
  dark-description: "#a1a1aa"
  dark-border: "#27272a"
  dark-control-border: "#3f3f46"
  dark-hover: "#27272a"
  dark-focus: "#a1a1aa"
  dark-tip: "#3fb950"
  dark-important: "#a371f7"
  dark-warning: "#fbbf24"
  dark-warning-border: "#78350f"
  dark-danger: "#f87171"
  dark-danger-border: "#7f1d1d"
  dark-success: "#34d399"
  code-background: "#0d0d0d"
  code-text: "#f4f4f5"
  code-border: "#27272a"
  chart-primary: "#2563eb"
  chart-primary-fill: "#2563eb18"
  chart-secondary: "#a1a1aa"
typography:
  h1: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 48px, fontWeight: 600, lineHeight: 1.12, letterSpacing: -0.035em }
  h2: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 36px, fontWeight: 600, lineHeight: 1.2, letterSpacing: -0.025em }
  h3: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 28px, fontWeight: 600, lineHeight: 1.3 }
  body: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 24px, fontWeight: 400, lineHeight: 1.5 }
  small: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 20px, fontWeight: 400, lineHeight: 1.45 }
  caption: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 16px, fontWeight: 400, lineHeight: 1.5 }
  control: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 13px, fontWeight: 500, lineHeight: 18px }
  metric: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 48px, fontWeight: 600, lineHeight: 1.15 }
  code: { fontFamily: 'SFMono-Regular, "Cascadia Code", "Roboto Mono", ui-monospace, monospace', fontSize: 20px, fontWeight: 400, lineHeight: 1.45 }
rounded:
  control: 6px
  container: 8px
  callout: 12px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  component: 32px
  gutter: 40px
  slide-horizontal: 72px
  slide-vertical: 56px
components:
  slide: { backgroundColor: "{colors.neutral}", textColor: "{colors.primary}" }
  slide-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-primary}" }
  prose: { textColor: "{colors.secondary}", typography: "{typography.body}" }
  button: { textColor: "{colors.secondary}", rounded: "{rounded.control}", typography: "{typography.control}" }
  callout: { backgroundColor: "{colors.neutral}", rounded: "{rounded.callout}", typography: "{typography.small}" }
  code: { backgroundColor: "{colors.code-background}", textColor: "{colors.code-text}", rounded: "{rounded.container}", typography: "{typography.code}" }
---

# Northstar Slides design contract

## Overview

- **Format:** Google's DESIGN.md alpha format: metadata/tokens followed by authoritative human-readable rules.
- **Direction:** Adapt the `html-report-builder` Northstar report's developer-documentation aesthetic to presentations. Preserve zinc neutrals, restrained blue, flat evidence, quiet controls, and thin rules. Do not copy report-specific reading columns, rail, fictional facts, or section spacing onto slides.
- **Source of truth:** This document, including its executable CSS below. It is self-contained and does not require another skill to be installed.
- **Agent decisions:** Content, instruction-requested composition, and useful evidence-backed elements. Do not independently select different fonts, palettes, shapes, or chart skins.
- **Precedence:** Explicit user design overrides take priority. Record deck-specific overrides in editable slide CSS, not the shared skill assets.
- **Identity:** No Google/OpenAI branding, logos, or claims of affiliation. No marketing chrome, gradients, glass, decorative shadows, floating cards, or arbitrary stock art.

## Theme replacement interface

To install another aesthetic, replace only `DESIGN.md`. Keep:

1. This document's responsibility for all aesthetic guidance.
2. Exactly one CSS block between `<!-- slide-theme:start -->` and `<!-- slide-theme:end -->`.
3. The structural hooks `.slide`, `.slide-content`, `.admonition`, `.admonition-title`, `.admonition-body`, `.table-scroll`, and the existing control IDs.
4. Light and `.dark` styling, readable no-CDN behavior, reduced-motion compatibility, and a print treatment.

The builder copies that CSS into the HTML. It does not interpret token YAML or fetch this document at presentation time. Keep tokens, prose, and CSS consistent. The template and structural CSS own navigation behavior and 1280×720 geometry, not theme choices.

Changing this file invalidates prior theme compatibility. The builder requires explicit review before replacing captured slides, since slide-specific styling may have depended on the previous theme.

## Colors and depth

| Role | Light | Dark |
| --- | --- | --- |
| Canvas and panels | White | Black |
| Headings | Zinc-950 | Zinc-100 |
| Body | Zinc-700 | Zinc-300 |
| Secondary text | Zinc-600 | Zinc-400 |
| Captions | Zinc-500 | Zinc-400 |
| Links / restrained labels / list markers | Blue-700 | Blue-400 |
| Rules | Zinc-200 | Zinc-800 |
| Control outlines | Zinc-300 | Zinc-700 |
| Hover | Zinc-100 | Zinc-800 |
| Focus | Zinc-600 | Zinc-400 |

Use explicit labels with status colors. Do not rely on color alone. Ordinary text must meet 4.5:1 contrast; large text and meaningful indicators must meet 3:1. Controls are monochrome, not blue primary actions.

All content is flat. Figures, tables, and KPI groups use horizontal rules rather than enclosing rounded cards. Callouts and source panels may have outlined containers. No elevation, translucency, blur, or decorative layers.

## Typography and composition

- Sans stack: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`. Do not require a font download.
- Mono stack: `SFMono-Regular, "Cascadia Code", "Roboto Mono", ui-monospace, monospace`.
- Typography values are measured on the fixed 1280×720 canvas, not the scaled viewport.
- H1 48px, H2 36px, H3 28px, body 24px, secondary/table/callout 20px, captions 16px, code 20px. Body line-height 1.5; headings weight 600. UI controls remain 13px at viewport scale.
- One main heading per slide is preferred, but preserve source hierarchy unless authorized to change it.
- Ordered-list numbers and unordered-list bullets use the link blue. List content retains its surrounding text color.
- Canvas padding is 72px horizontally and 56px vertically. Use 24px content gaps and 40px multi-column gutters.
- Improve fit through composition only when authorized. Never automatically shrink text, delete evidence, truncate code, crop data imagery, or add slides to conceal overflow.
- Fixed 16:9 proportions remain on mobile. The whole canvas scales; slide typography does not independently collapse into report-style prose.
- `.columns` is a two-column grid. `.metrics` is a flat equal-width strip with shared dividers. These helpers are optional and must serve content, not demonstrate components.
- Large numerical values use tabular figures. Do not invent metrics, deltas, labels, or citations.

## Controls and navigation

- One compact bottom bar groups slide navigation and utilities, separated from slide content by a thin horizontal rule. Reserve its height outside the scaled canvas, and wrap controls on small viewports. No floating controls, site header, or permanent sidebar.
- Controls use 6px corners, 13px/18px medium labels, neutral hover/press, and 150ms color transitions. No press scaling or translation.
- Minimum 32px control height on desktop. On touch-sized viewports use 44px targets; overview rows and dialog actions use 44px targets at all sizes.
- Focus is a 2px neutral outline with 3px offset. Disabled controls use native `disabled` and 0.45 opacity.
- Overview is a collapsible right-hand panel with a neutral outline and no shadow, above the bottom bar. Selecting a slide or using navigation leaves it open. Close it with Overview, its explicit Close button, or Escape. Active slide rows use inherited text, stronger weight, and `aria-current`, not saturated fills.
- Source is a native modal dialog with a 1px neutral outline, 8px radius, 24px padding, and black 48% backdrop. Original Markdown remains selectable monospace text.
- Theme preference is initialized before paint, stored under `slides-theme`, and falls back to the system preference. `?theme=light` and `?theme=dark` are non-persistent preview overrides. Storage failure must not prevent in-memory toggling.
- UI labels provide a no-font/no-CDN fallback. No icon font is required. If icons are requested, use Material Symbols Outlined with accessible text labels and hide decorative icons from assistive technology.

## Components

### Tables, code, and images

- Tables: semantic headers, 20px type, transparent header fill, 12px cell padding, thin row rules, numeric columns right-aligned when meaningful. Named local scroll regions prevent document-level overflow.
- Code: fixed `#0d0d0d` surface in both themes, zinc-100 text, zinc-800 outline, 8px radius, 20px/1.45 monospace, 20px padding. Preserve indentation. Highlighting is optional and never required for readability.
- Inline code: plain monospace, not filled badges.
- Blockquotes: 2px neutral left rule, 20px inset, no filled card.
- Images: preserve natural aspect ratio, descriptive alt text, and supplied attribution. Constrain dimensions to available slide space; do not crop evidence. Broken or absent assets remain explicit limitations.
- Links: blue with underline. Navigation stays neutral.

### GitHub-style admonitions

Support exactly the standard markers at the beginning of a blockquote:

```markdown
> [!NOTE]
> Useful background.

> [!WARNING]
> A condition that needs attention.
```

Also support `TIP`, `IMPORTANT`, and `CAUTION`, nested Markdown, and multiline bodies. Unknown markers remain ordinary blockquotes. Markers inside fenced code remain literal code.

| Marker | Label | Treatment |
| --- | --- | --- |
| `[!NOTE]` | Note | Neutral heading and outline |
| `[!TIP]` | Tip | Green label and outline |
| `[!IMPORTANT]` | Important | Purple label and outline |
| `[!WARNING]` | Warning | Amber label and outline |
| `[!CAUTION]` | Caution | Red label and outline |

GitHub syntax determines semantic type. Tip uses GitHub-style green (`#1a7f37` light / `#3fb950` dark), and Important uses purple (`#8250df` light / `#a371f7` dark). Other admonitions retain this theme's treatments. Caution uses red to distinguish serious risk from warning.

- Complete 1px outline, 12px radius, page-matched fill, 20px horizontal/16px vertical padding.
- Explicit 20px semibold label, neutral 20px/1.45 body. Labels do not replace the author's body.
- Static `role="note"`, never assertive live alerts. Optional leading icons are decorative, not the sole type indication.
- Tip and Important borders match their label colors. Warning borders: amber-300/amber-900; caution borders: red-300/red-900. Body text stays neutral.

### Agent-generated charts and diagrams

- Use only when authorized and useful. Plain HTML/CSS/SVG is acceptable; online libraries are allowed but not mandatory.
- Charts: blue-600 primary series, zinc-400 comparison, thin zinc grid, no axis frame, flat figure. Line primary: 2px stroke, 3px points, tension .32, subtle `#2563eb18` fill. Bars start at zero. No 3D, dual axes, gradients, or decorative multicolor series.
- Add a clear takeaway, accessible figure name, units, and exact-value table or textual equivalent. A chart must not be the sole representation of important values.
- Recolor labels/grid on theme changes. Preserve series styling. Disable nonessential animation with reduced motion.
- Diagrams: restrained neutral surfaces and thin rules. Mermaid, if used, requires strict security and neutral/dark themes; preserve original diagram source. Provide a prose equivalent and useful fallback.
- Mathematics, if requested: KaTeX with `trust: false`, `output: 'htmlAndMathml'`, and readable raw-source fallback. Do not add equations solely for decoration.
- Dependency URLs should be versioned. Initialize components independently; a failed CDN must not prevent presentation navigation or reading supplied content. Do not fetch private data at runtime.
- Custom components must use slide lifecycle hooks for visibility, theme changes, printing, and cleanup.

## Motion, accessibility, and printing

- Instant slide changes by default. No forced page transitions, autoplay, or ornamental animation.
- Visible keyboard focus, native control semantics, hidden-slide inertness, accessible chart alternatives, and readable source text are required.
- Print uses white canvas and black text, preserves data distinctions, and removes utilities/overview/source/navigation. One 1280×720 slide per landscape page; no clipping or automatic content scaling to hide overflow.
- Details inside slides open for printing and restore afterward. Custom chart/diagram hooks must preserve printable evidence.
- Validate actual PDF page count and inspect printed content when browser tooling supports it.

## Executable baseline theme

This is the complete aesthetic layer consumed by the builder. Geometry, hiding, navigation positioning, and pagination remain in the theme-neutral structure file.

<!-- slide-theme:start -->
```css
:root {
  --page: #ffffff; --ink: #09090b; --body: #3f3f46; --description: #52525b;
  --muted: #71717a; --link: #1d4ed8; --rule: #e4e4e7; --outline: #d4d4d8;
  --hover: #f4f4f5; --pressed: #e4e4e7; --focus: #52525b;
  --tip: #1a7f37; --important: #8250df;
  --warning: #b45309; --warning-border: #fcd34d;
  --danger: #b91c1c; --danger-border: #fca5a5;
  --chart-primary: #2563eb; --chart-secondary: #a1a1aa; --chart-grid: #e4e4e7;
  --sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --mono: SFMono-Regular, "Cascadia Code", "Roboto Mono", ui-monospace, monospace;
}
.dark {
  --page: #000000; --ink: #f4f4f5; --body: #d4d4d8; --description: #a1a1aa;
  --muted: #a1a1aa; --link: #60a5fa; --rule: #27272a; --outline: #3f3f46;
  --hover: #27272a; --pressed: #3f3f46; --focus: #a1a1aa;
  --tip: #3fb950; --important: #a371f7;
  --warning: #fbbf24; --warning-border: #78350f;
  --danger: #f87171; --danger-border: #7f1d1d; --chart-grid: #27272a;
}
body { font-family: var(--sans); color: var(--ink); background: var(--page); text-rendering: optimizeLegibility; }
.slide { background: var(--page); color: var(--body); padding: 56px 72px; font-size: 24px; line-height: 1.5; }
.slide h1, .slide h2, .slide h3, .slide h4, .slide h5, .slide h6 { color: var(--ink); font-weight: 600; margin: 0 0 24px; }
.slide h1 { font-size: 48px; line-height: 1.12; letter-spacing: -.035em; }
.slide h2 { font-size: 36px; line-height: 1.2; letter-spacing: -.025em; }
.slide h3 { font-size: 28px; line-height: 1.3; }
.slide h4, .slide h5, .slide h6 { font-size: 24px; }
.slide p, .slide ul, .slide ol, .slide blockquote, .slide pre, .slide .table-scroll, .slide .admonition { margin: 0 0 24px; }
.slide li { margin: 8px 0; }
.slide li::marker { color: var(--link); }
.slide ul, .slide ol { padding-left: 32px; }
.slide a { color: var(--link); text-decoration: underline; }
.slide hr { border: 0; border-top: 1px solid var(--rule); margin: 32px 0; }
.slide blockquote { border-left: 2px solid var(--outline); padding-left: 20px; color: var(--description); }
.slide strong { font-weight: 600; color: var(--ink); }
.slide code { font-family: var(--mono); font-size: .85em; }
.slide pre { padding: 20px; border: 1px solid #27272a; border-radius: 8px; background: #0d0d0d; color: #f4f4f5; font-size: 20px; line-height: 1.45; }
.slide pre code { font-size: inherit; }
.slide img { display: block; height: auto; max-height: 420px; object-fit: contain; }
.slide figcaption, .slide .caption { font-size: 16px; line-height: 1.5; color: var(--muted); margin-top: 12px; }
.slide .table-scroll { border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }
.slide table { width: 100%; border-collapse: collapse; font-size: 20px; font-variant-numeric: tabular-nums; }
.slide th { text-align: left; font-weight: 500; color: var(--description); }
.slide th[align="right"], .slide td[align="right"] { text-align: right; }
.slide th[align="center"], .slide td[align="center"] { text-align: center; }
.slide th[align="left"], .slide td[align="left"] { text-align: left; }
.slide td, .slide th { padding: 12px; border-bottom: 1px solid var(--rule); }
.slide tr:last-child td { border-bottom: 0; }
.slide .admonition { border: 1px solid var(--outline); border-radius: 12px; padding: 16px 20px; font-size: 20px; line-height: 1.45; }
.slide .admonition-title { color: var(--ink); font-weight: 600; margin-bottom: 8px; }
.slide .admonition-body > :last-child { margin-bottom: 0; }
.slide .admonition-tip { border-color: var(--tip); }
.slide .admonition-tip > .admonition-title { color: var(--tip); }
.slide .admonition-important { border-color: var(--important); }
.slide .admonition-important > .admonition-title { color: var(--important); }
.slide .admonition-warning { border-color: var(--warning-border); }
.slide .admonition-warning > .admonition-title { color: var(--warning); }
.slide .admonition-caution { border-color: var(--danger-border); }
.slide .admonition-caution > .admonition-title { color: var(--danger); }
.slide .columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 40px; }
.slide .metrics { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; border-block: 1px solid var(--rule); }
.slide .metric { padding: 20px; border-right: 1px solid var(--rule); }
.slide .metric:last-child { border-right: 0; }
.slide .metric-value { color: var(--ink); font-size: 48px; font-weight: 600; font-variant-numeric: tabular-nums; }
.slide details { border: 1px solid var(--outline); border-radius: 8px; padding: 16px 20px; font-size: 20px; }
.slide summary { cursor: pointer; font-weight: 500; }
.slide input[type="checkbox"] { accent-color: var(--ink); }
button { font: 500 13px/18px var(--sans); color: var(--body); background: transparent; border: 1px solid var(--outline); border-radius: 6px; padding: 6px 10px; min-height: 32px; cursor: pointer; transition: color 150ms, background-color 150ms, border-color 150ms; }
button:hover:not(:disabled) { background: var(--hover); }
button:active:not(:disabled) { background: var(--pressed); }
button:disabled { opacity: .45; cursor: default; }
button:focus-visible, a:focus-visible, summary:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible, [tabindex="0"]:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }
#control-bar { background: var(--page); border-top: 1px solid var(--rule); padding: 8px 16px; }
#control-bar button { border-color: transparent; }
#slide-counter { font-size: 13px; min-width: 64px; text-align: center; color: var(--muted); font-variant-numeric: tabular-nums; }
#overview { padding: 20px; border: 1px solid var(--outline); border-radius: 8px; background: var(--page); }
#overview-header { margin-bottom: 16px; }
#overview h2 { font-size: 16px; margin: 0; }
#overview nav { gap: 8px; }
#overview button { border-color: transparent; min-height: 44px; }
#overview button[aria-current] { font-weight: 600; color: var(--ink); border-left-color: var(--ink); }
#source-dialog { padding: 24px; border: 1px solid var(--outline); border-radius: 8px; color: var(--ink); background: var(--page); }
#source-dialog::backdrop { background: rgb(0 0 0 / .48); }
#source-dialog h2 { font-size: 24px; margin: 0 0 24px; }
#source-dialog h3 { font-size: 14px; margin: 24px 0 8px; color: var(--description); }
#source-dialog pre { font: 14px/1.6 var(--mono); color: var(--body); }
#source-close { min-height: 44px; }
#layout-warning { color: var(--warning); background: var(--page); font-size: 13px; }
@media (max-width: 640px) { #utilities button, #navigation button { min-height: 44px; } }
@media print {
  :root { --page: #ffffff; --ink: #000000; --body: #000000; --description: #000000; --muted: #000000; --link: #000000; --rule: #d4d4d8; --outline: #a1a1aa; --warning: #000000; --danger: #000000; }
  body, .slide { background: white !important; color: black !important; }
  .slide li::marker { color: black !important; }
  .slide h1, .slide h2, .slide h3, .slide h4, .slide h5, .slide h6, .slide strong, .slide a, .slide figcaption, .slide .caption, .slide .admonition-title { color: black !important; }
  .slide pre { background: white !important; color: black !important; border-color: #d4d4d8; white-space: pre-wrap; overflow-wrap: anywhere; }
  .slide table, .slide .admonition-body { color: black; }
  .slide .admonition { border-color: #a1a1aa; }
  .slide { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
}
```
<!-- slide-theme:end -->
