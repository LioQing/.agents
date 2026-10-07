---
version: alpha
name: Northstar Report
description: The original Northstar API report design, expressed in Google's DESIGN.md format without changing its visual identity or layout.
colors:
  primary: "#09090b"
  secondary: "#3f3f46"
  tertiary: "#1d4ed8"
  neutral: "#ffffff"
  muted: "#71717a"
  description: "#52525b"
  border: "#e4e4e7"
  control-border: "#d4d4d8"
  open-border: "#a1a1aa"
  hover: "#fafafa"
  badge-surface: "#f4f4f5"
  callout-text: "#27272a"
  success: "#047857"
  success-border: "#6ee7b7"
  warning: "#b45309"
  warning-border: "#fcd34d"
  danger: "#b91c1c"
  danger-border: "#fca5a5"
  focus: "#3b82f6"
  dark-primary: "#f4f4f5"
  dark-secondary: "#d4d4d8"
  dark-tertiary: "#60a5fa"
  dark-neutral: "#000000"
  dark-muted: "#a1a1aa"
  dark-description: "#a1a1aa"
  dark-border: "#27272a"
  dark-control-border: "#3f3f46"
  dark-open-border: "#52525b"
  dark-hover: "#18181b"
  dark-badge-surface: "#18181b"
  dark-callout-text: "#e4e4e7"
  dark-success: "#34d399"
  dark-success-border: "#064e3b"
  dark-warning: "#fbbf24"
  dark-warning-border: "#78350f"
  dark-danger: "#f87171"
  dark-danger-border: "#7f1d1d"
  code-background: "#0d0d0d"
  code-text: "#f4f4f5"
  code-muted: "#a1a1aa"
  code-border: "#27272a"
  chart-primary: "#2563eb"
  chart-primary-fill: "#2563eb18"
  chart-secondary: "#a1a1aa"
typography:
  h1: { fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', fontSize: 48px, fontWeight: 600, lineHeight: 1, letterSpacing: -0.035em }
  h1-mobile: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 36px, fontWeight: 600, lineHeight: 40px, letterSpacing: -0.035em }
  h2: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 30px, fontWeight: 600, lineHeight: 36px, letterSpacing: -0.025em }
  h2-mobile: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 24px, fontWeight: 600, lineHeight: 32px, letterSpacing: -0.025em }
  lead: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 18px, fontWeight: 400, lineHeight: 32px }
  body: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 15px, fontWeight: 400, lineHeight: 28px }
  small: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 14px, fontWeight: 400, lineHeight: 24px }
  nav: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 14px, fontWeight: 400, lineHeight: 20px }
  caption: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 12px, fontWeight: 400, lineHeight: 20px }
  label: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 12px, fontWeight: 600, lineHeight: 16px, letterSpacing: 0.14em }
  control: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 12px, fontWeight: 500, lineHeight: 16px }
  metric: { fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif', fontSize: 24px, fontWeight: 600, lineHeight: 32px, fontFeature: '"tnum"' }
  code: { fontFamily: 'SFMono-Regular, "Cascadia Code", "Roboto Mono", ui-monospace, monospace', fontSize: 16px, fontWeight: 400, lineHeight: 24px }
rounded:
  none: 0px
  copy: 4px
  input: 6px
  container: 8px
  callout: 12px
  pill: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  callout: 20px
  xl: 24px
  component: 32px
  metric: 40px
  header-padding: 48px
  gutter: 56px
  header-gap: 64px
  section: 80px
  page-padding: 96px
  frame: 1180px
  reading: 820px
  rail: 200px
  margin: 40px
  margin-mobile: 24px
components:
  page: { backgroundColor: "{colors.neutral}", textColor: "{colors.primary}" }
  page-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-primary}" }
  prose: { backgroundColor: "{colors.neutral}", textColor: "{colors.secondary}", typography: "{typography.body}" }
  prose-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-secondary}" }
  caption: { backgroundColor: "{colors.neutral}", textColor: "{colors.muted}", typography: "{typography.caption}" }
  caption-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-muted}" }
  description: { backgroundColor: "{colors.neutral}", textColor: "{colors.description}" }
  description-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-description}" }
  section-label: { backgroundColor: "{colors.neutral}", textColor: "{colors.tertiary}" }
  section-label-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-tertiary}" }
  toolbar-button: { backgroundColor: "{colors.neutral}", textColor: "{colors.primary}", typography: "{typography.control}", rounded: "{rounded.pill}", height: 36px }
  toolbar-button-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-primary}" }
  toolbar-button-hover: { backgroundColor: "{colors.hover}" }
  toolbar-button-dark-hover: { backgroundColor: "{colors.dark-hover}" }
  input: { backgroundColor: "{colors.neutral}", textColor: "{colors.description}", rounded: "{rounded.input}", typography: "{typography.small}" }
  input-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-description}" }
  callout: { backgroundColor: "{colors.neutral}", textColor: "{colors.callout-text}", rounded: "{rounded.callout}", typography: "{typography.small}" }
  callout-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-callout-text}" }
  success: { backgroundColor: "{colors.neutral}", textColor: "{colors.success}" }
  success-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-success}" }
  warning: { backgroundColor: "{colors.neutral}", textColor: "{colors.warning}" }
  warning-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-warning}" }
  danger: { backgroundColor: "{colors.neutral}", textColor: "{colors.danger}" }
  danger-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-danger}" }
  badge: { backgroundColor: "{colors.badge-surface}", textColor: "{colors.description}", rounded: "{rounded.pill}" }
  badge-dark: { backgroundColor: "{colors.dark-badge-surface}", textColor: "{colors.dark-description}" }
  code: { backgroundColor: "{colors.code-background}", textColor: "{colors.code-text}", typography: "{typography.code}", rounded: "{rounded.container}" }
  code-caption: { backgroundColor: "{colors.code-background}", textColor: "{colors.code-muted}" }
  rule: { backgroundColor: "{colors.border}" }
  rule-dark: { backgroundColor: "{colors.dark-border}" }
  control-outline: { backgroundColor: "{colors.control-border}" }
  control-outline-dark: { backgroundColor: "{colors.dark-control-border}" }
  open-outline: { backgroundColor: "{colors.open-border}" }
  open-outline-dark: { backgroundColor: "{colors.dark-open-border}" }
  success-outline: { backgroundColor: "{colors.success-border}" }
  success-outline-dark: { backgroundColor: "{colors.dark-success-border}" }
  warning-outline: { backgroundColor: "{colors.warning-border}" }
  warning-outline-dark: { backgroundColor: "{colors.dark-warning-border}" }
  danger-outline: { backgroundColor: "{colors.danger-border}" }
  danger-outline-dark: { backgroundColor: "{colors.dark-danger-border}" }
  focus: { backgroundColor: "{colors.focus}" }
  code-outline: { backgroundColor: "{colors.code-border}" }
  chart-line: { backgroundColor: "{colors.chart-primary}" }
  chart-fill: { backgroundColor: "{colors.chart-primary-fill}" }
  chart-comparison: { backgroundColor: "{colors.chart-secondary}" }
---

# Northstar Report design contract

## Overview

- **Source of truth:** The original Northstar API report in [assets/example-report.html](assets/example-report.html).
- **Format:** [Google Labs' DESIGN.md specification](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md), alpha.
- **Purpose:** Express the existing design, not redesign it or adopt Google's visual identity.
- **Identity:** Developer-documentation report; white/black page, zinc neutrals, restrained blue, thin horizontal rules, generous whitespace.
- **Agent decisions:** Content, section names, and useful evidence-backed components only.
- **Preserve:** Original typography, fixed top-right utilities, flat KPI strip, two-column executive prose, right rail, chart styling, and horizontal diagram.
- **Implementation:** Reuse the example's Tailwind classes and small behavior-specific CSS. Tokens name existing values; they do not require replacing utilities with a new component framework.
- **Extensions:** Additional component examples live in a closed Methodology disclosure, not a replacement showcase page.
- **Precedence:** Explicit user design overrides take priority; otherwise follow this contract.
- **Runtime:** Embed authorized source data; never fetch this document or private data from the report.

## Colors

| Role | Light | Dark |
| --- | --- | --- |
| Page | `neutral`, white | `dark-neutral`, black |
| Headings | `primary`, zinc-950 | `dark-primary`, zinc-100; strong emphasis may use white |
| Executive prose | `secondary`, zinc-700 | `dark-secondary`, zinc-300 |
| Lead / descriptions | `description`, zinc-600 | `dark-description`, zinc-400 |
| Metadata / captions / rail | `muted`, zinc-500 | `dark-muted`, zinc-400 |
| Section labels / prose links | `tertiary`, blue-700 | `dark-tertiary`, blue-400 |
| Active navigation | Inherited heading color, not blue | Inherited heading color, not blue |
| Rules / table dividers | `border`, zinc-200 | `dark-border`, zinc-800 |
| Inputs / neutral callout outlines | `control-border`, zinc-300 | `dark-control-border`, zinc-700 |
| Open disclosure outline | `open-border`, zinc-400 | `dark-open-border`, zinc-600 |
| Hover | `hover`, zinc-50 | `dark-hover`, zinc-900; disclosure hover at 60% opacity |
| Callout body | `callout-text`, zinc-800 | `dark-callout-text`, zinc-200 |
| Status: success / warning / danger | Emerald-700 / amber-700 / red-700 | Emerald-400 / amber-400 / red-400 |
| Focus | Blue-500 | Blue-500 |
| Code | Fixed #0d0d0d surface; zinc-100 text; zinc-400 toolbar; zinc-800 outline | Same |

- Charts retain blue-600 as the primary series and zinc-400 as the comparison series in both themes.
- Blue chart fill is `#2563eb18`, not a gradient.
- Note, Information, Tip, and Recommendation share the original neutral callout palette.
- Status colors require explicit labels; do not rely on color alone.
- Normal text meets 4.5:1 contrast; large text and meaningful focus indicators meet 3:1.
- Boundary tokens describe outlines, not text colors.
- No decorative palettes, purple tips, tinted equation fills, or saturated callout fills.

## Typography

| Role | ≥640px | <640px | Original treatment |
| --- | --- | --- | --- |
| H1 | 48px / 48px | 36px / 40px | Weight 600; tracking -.035em; max-width 768px |
| H2 | 30px / 36px | 24px / 32px | Weight 600; tracking -.025em |
| Lead | 18px / 32px | Same | Zinc-600/400; max-width 672px |
| Executive prose | 15px / 28px | Same | Zinc-700/300 |
| Component prose | 14px / 24px | Same | Descriptions zinc-600/400 |
| Rail / table | 14px / 20px | Same | Compact document UI |
| Captions | 12px / 20px | Same | Zinc-500/400 |
| Section eyebrow | 12px / 16px | Same | Uppercase; weight 600; tracking .14em |
| Header metadata | 12px / 16px | Same | Weight 500; uppercase; tracking .16em |
| KPI values | 24px / 32px | Same | Weight 600; tabular numerals |
| Utility buttons | 12px / 16px | Same | Weight 500 |
| Code block | 16px / 24px | Same | Original monospace stack |

- Sans stack: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif`.
- Preserve the Inter-first fallback stack; do not add a font download or replace it with a new family.
- Mono stack: `SFMono-Regular, Cascadia Code, Roboto Mono, ui-monospace, monospace`.
- Inline endpoint identifiers use 12px monospace; code blocks use the original larger type.
- One H1; H2 for report sections; bold compact subheadings inside secondary component examples.
- KaTeX uses its supplied math fonts.

| Supporting text | Pattern |
| --- | --- |
| Lists | Native bullets/numbers; 24px inset; 8px item gaps |
| Definitions | Semibold term; description 4px below |
| Inline code | Plain monospace; do not introduce filled chips |
| `kbd` | Compact 1px neutral outline; 4px radius |
| Quotations | 2px neutral left rule; 16px inset; attribution below; no filled card |
| Prose links | Blue-700/400; underline |
| Navigation links | Unadorned; inherited neutral active state |
| Citations | Numbered anchors; supplied source details; ordered references and return links |

- Never invent quotations, attribution, or citations.
- UI icons use Google Material Symbols Outlined, weight 400, optical size 20, fill 0.
- Standard icons are 20px; the original toolbar contrast icon is 16px.
- Load only named icons; give icon controls accessible names; hide decorative icons from assistive technology.
- Do not draw custom SVG/Unicode UI icons; content SVGs remain allowed.

## Layout

| Property | ≥1024px | <1024px |
| --- | --- | --- |
| Frame | Centered, max-width 1180px including padding | Same maximum, single column |
| Horizontal padding | 40px | 24px |
| Columns | `minmax(0,820px) 200px` | One fluid reading column |
| Gap | 56px | No rail |
| Frame top padding | 96px | 80px |
| Frame bottom padding | 96px | 96px |
| Contents | Right rail, sticky 96px from top | Outlined native disclosure below header |
| Executive prose | Two columns from 640px; 32px gap | One column below 640px |
| KPIs | Four columns from 640px | Two columns below 640px, including narrow phones |

| Element | Original geometry |
| --- | --- |
| Utilities | Fixed top-right, 16px from edges; 8px gap; z-index 50 |
| Header | 1px bottom rule; 48px bottom padding; 64px following space |
| Header order | Metadata/status → H1 → lead → KPI strip |
| Metadata → H1 | 24px |
| H1 → lead | 20px |
| Lead → KPI strip | 40px |
| KPI strip | Top/bottom rules and shared internal dividers; no rounded enclosing card |
| KPI cells | 20px vertical padding; 16px internal horizontal separation |
| KPI label → value → delta | 8px / 4px |
| Section gap | 80px at all screen widths; final Methodology gap 64px |
| Section start, except first | 1px horizontal rule; 32px top padding |
| Eyebrow → H2 | 12px |
| H2 → description | 12px |
| Summary → prose | 24px |
| Figure gap | 32px |
| Math / code gap | 28px |
| Section scroll margin | 32px |
| Mobile contents bottom margin | 48px |

- Keep the reading column first in the DOM and the rail second.
- Keep the original fixed utility controls; they are not a site navigation bar.
- No global top navigation or left sidebar.
- Do not move Theme/Print into the header, flatten executive prose to one desktop column, or turn KPIs/figures/tables into boxed cards.
- Omit unavailable metrics or show `N/A`; never invent deltas.
- Preserve section IDs and update both contents lists when replacing content.

## Elevation & Depth

| Element | Treatment |
| --- | --- |
| Report sections / metrics / figures / tables | Flat, thin rules, no shadow |
| Original fixed utility buttons | `shadow-sm`; page-colored 90% fill; backdrop blur |
| Callouts / disclosures | Full outline; no shadow |
| Optional tooltip | Code-colored surface; no decorative shadow |
| Native dialog | Page surface; neutral outline; backdrop `rgb(0 0 0 / .48)` |

- Preserve the toolbar's subtle translucency/blur; do not extend it to reading surfaces.
- No gradients, floating evidence cards, decorative layers, or marketing chrome.

## Shapes

| Element | Radius |
| --- | --- |
| Fixed utility buttons / status badges | Pill |
| Filter inputs / optional local buttons | 6px |
| Code / equation / disclosure containers | 8px |
| Callouts | 12px |
| Copy button | 4px |
| KPI strip / chart and table rules | None |

## Components

### Navigation and themes

| Property | Rule |
| --- | --- |
| Rail | 200px; sticky 96px from top; no new surface/box |
| Rail label | 12px uppercase; tracking .14em; 16px bottom gap |
| Rail links | 1px left rule; 16px horizontal / 8px vertical padding; 14px type |
| Active link | Inherited text/rule color; weight 600; `aria-current="location"` |
| Scroll tracking | `IntersectionObserver`; native fragment navigation; final section active at page bottom |
| Mobile contents | Native outlined disclosure; same report links |
| Theme setup | Head script before paint; `.dark`; `color-scheme`; stored `report-theme`, otherwise system preference |
| Preview override | `?theme=light` / `?theme=dark`; do not persist until user toggles |
| Toggle | Original compact Theme button; accessible name; `aria-pressed` reflects dark mode |
| Storage failure | Catch errors; toggle still works in memory |
| Rich content | Recolor Chart.js; rerender Mermaid from preserved source; serialize renders |

### Buttons, forms, tooltips, and feedback

| Control | Pattern |
| --- | --- |
| Theme / Print | 36px tall; pill; 12px horizontal padding; 12px text; 1px neutral outline |
| Theme label | Hidden below 640px; accessible name stays available |
| Copy | Original compact 4px radius; 8px horizontal / 4px vertical padding |
| Filter | Transparent fill; 1px zinc-300/700 outline; 6px radius; 12px horizontal / 8px vertical padding; 14px text; max-width 384px |
| Local primary action | Blue-600 fill; white label; compact 6px-radius geometry; only when content requires it |
| Local secondary action | Neutral outline; transparent fill; same compact geometry |
| Focus | Blue-500 ring, 2px; inset for summary rows |
| Press | Scale .97; no bounce |
| Disabled | Native `disabled`; opacity .5; no hover/press motion |
| Textarea / select | Same filter border/type/radius; textarea vertically resizable |
| Labels / helpers | Visible; 8px label gap; 12px helpers; `aria-describedby` where applicable |
| Validation | Red outline; explicit message; `aria-invalid="true"` |
| Checkbox / radio | Native controls; wrapped 44px label targets; labeled radio fieldset |
| Tooltip | Code palette; 12px/20px; max-width 240px; 8px padding; 6px radius |

- Tooltips open on hover and focus, use `aria-describedby`, and close with Escape.
- Keep essential information out of tooltips and dialogs.
- Use persistent `role="status"` / polite announcements for copy, sort, filter, and local preview feedback.
- Copy success: **Copied**; failure: **Copy unavailable. Select the code to copy.**
- Placeholders are examples, not labels.
- Forms are optional report-local interactions; no fabricated submission flows.
- Preserve original compact visible controls; do not impose a new 44px button design globally.

### Tables and badges

| Property | Original pattern |
| --- | --- |
| Table container | Horizontal overflow; top/bottom neutral rules; no side box or radius |
| Table | 14px; scoped headers; semantic caption; tabular values |
| Header | 12px muted text; transparent fill; 12px padding; weight 500 |
| Body cells | 12px horizontal / 16px vertical padding |
| Rows | 1px zinc-200/800 dividers |
| Alignment | Labels left; numeric values right |
| Endpoint IDs | 12px monospace |
| Sort | Native header buttons; `aria-sort` on active header; polite column/direction feedback |
| Filter | Visible count; explicit no-results text; Reset filter when empty |
| Missing data | `N/A`, not zero |
| Badge | Compact 12px pill; 8px horizontal / 4px vertical padding; explicit status text |

- Use a keyboard-focusable, named local scroll region; prevent horizontal page overflow.
- Only long tables need sticky headers inside bounded scroll regions.
- Preserve plain colored assessment text in endpoint rows; do not turn every assessment into a badge.
- Preserve the original outlined Healthy badge and subtle filled Lower is better badge.
- Do not claim fictional example values reconcile with unrelated metrics.

### Charts

| Property | Original Chart.js pattern |
| --- | --- |
| Figure | Top/bottom rules; no enclosing rounded card |
| Plot region | 340px at all widths; 20px vertical padding |
| Primary series | Blue-600; 2px stroke; 3px points; tension .32; subtle `#2563eb18` fill |
| Comparison series | Zinc-400; 1.5px stroke; 2px points; tension .32; transparent fill |
| Grid | Zinc-200 light / zinc-800 dark; no axis frame |
| Tick / legend text | Zinc-600 light / zinc-400 dark |
| Legend | Bottom; point-style keys; 8px box width; 24px padding |
| Tooltip | Original Chart.js dark tooltip; explicit values and units |
| Y axis | `suggestedMin: 0`; units in ticks |
| Interaction | `intersect: false`; `mode: 'index'` |
| Caption | 12px/20px; 12px top gap |
| Reduced motion | Disable chart animation |
| Theme changes | Recolor text/grid without changing series styling |

- Time → line; category comparison → horizontal bars; discrete periods → vertical bars; relationships → scatter; otherwise table.
- Other chart types inherit the original flat figure, palette, and compact legend, not the discarded showcase style.
- Bars start at zero; any materially truncated line axis requires an explicit caption.
- Keep a written takeaway, accessible chart name, and reachable exact-value table.
- No 3D, dual-axis, gradient, or decorative chart treatments.
- On library failure, show a concise fallback pointing to exact values.
- Do not replace curved blue/gray lines with a multicolor dashed, unfilled style.

### Diagrams and images

| Property | Original Mermaid pattern |
| --- | --- |
| Theme | `neutral` in light mode; `dark` in dark mode |
| Security | Strict |
| Font | `Inter, system-ui, sans-serif` |
| Direction | Original left-to-right flow; preserve its relationship layout |
| Figure | Top/bottom rules; 32px vertical padding; no rounded outer card |
| SVG | `max-width: 100%; height: auto`; centered |
| Source | Preserved in a `<template>` |
| Theme update | Rerender from source; prevent stale results |
| Failure | Readable prose equivalent, not a blank diagram |

- Do not switch the reference diagram to a vertical flow or replace Mermaid's original themes with a new base palette.
- Complex/large diagrams may scroll locally; never make the whole page overflow.
- Authorized images use semantic figures, descriptive alt text, natural aspect ratio, max-width 100%, and supplied captions/attribution.
- Optional images may use 8px rounding; no decorative stock art or evidence cropping.
- Content SVGs are allowed; custom SVG UI icons are not.

### Admonitions

| Shared property | Original pattern |
| --- | --- |
| Container | Complete 1px outline; 12px radius; page-matched fill |
| Spacing | 20px horizontal / 16px vertical padding; 16px icon gap |
| Icon | Leading 20px Material Symbol |
| Message | 14px/24px; zinc-800/200 body; explicit semibold label |
| Accessibility | Static `role="note"`, not assertive live alerts |

| Type | Palette | Icon |
| --- | --- | --- |
| Note | Original neutral | `info` |
| Information / Important / Recommendation | Original neutral | `info` |
| Tip | Original neutral, no new purple palette | `lightbulb` |
| Success | Emerald label/icon/outline | `check_circle` |
| Warning / Caution | Amber label/icon/outline | `warning` |
| Danger / Error | Red label/icon/outline | `error` |

- Semantic outlines use the light 300 / dark 900 status shades; body text remains neutral.
- Neutral labels use heading color, as in the original Recommendation.
- Use success only for verified outcomes; keep caution and recommendation wording explicit.

### Mathematics

| Property | Pattern |
| --- | --- |
| Library | KaTeX; `output: 'htmlAndMathml'`; `trust: false`; `throwOnError: false` |
| Inline / display delimiters | `\(...\)` / `\[...\]`; avoid currency collisions |
| Equation panel | Transparent/page fill; 1px zinc-200/800 outline; 8px radius |
| Panel padding | 20px horizontal / 24px vertical |
| Alignment | Center equation; definitions/interpretation left-aligned below |
| Display overflow | Local horizontal scrolling; 8px vertical breathing room |
| Multi-line | `aligned` |
| Failure | Raw TeX plus a plain-language equivalent |

- Preserve the original math typography; no new forced 1.05em treatment or tinted panel.
- Number equations only when referenced; do not include ornamental formulas.

### Code

| Property | Original pattern |
| --- | --- |
| Panel | #0d0d0d in both themes; zinc-800 outline; 8px radius |
| Toolbar | Zinc-400, 12px; 16px horizontal / 8px vertical padding |
| Copy | Compact original control, not a tall replacement button |
| Code | Original mono stack; 16px/24px; 20px padding |
| Highlighting | Versioned Highlight.js GitHub Dark stylesheet |
| Overflow | Preserve indentation and lines; horizontal scrolling |
| Copy source | `textContent`, excluding toolbar |
| Failure | Selectable raw code; polite copy-failure message |

- Escape embedded HTML; do not set user source with `innerHTML`.
- Do not shrink code to 13px or add line numbers without a user request.

### Expandable sections

| Property | Original pattern |
| --- | --- |
| Semantics | Native `<details>/<summary>` |
| Container | Full zinc-300/700 outline; 8px radius; transparent fill |
| Open outline | Zinc-400/600 |
| Gap | 12px |
| Summary | 14px medium; 20px horizontal / 16px vertical padding; ≥44px target |
| Mobile contents summary | 16px horizontal / 12px vertical padding |
| Hover | Zinc-50 / zinc-900 at 60% opacity; no permanent filled open-summary redesign |
| Icon | Trailing 20px `add`, zinc-400; 45° rotation when open |
| Focus | Inset 2px blue-500 ring |
| Body | 20px horizontal / 16px bottom padding; muted 14px/24px text |
| Animation | 190ms `cubic-bezier(.2,.8,.2,1)`; height/opacity; at most 4px offset |
| Reduced motion / unsupported animation | Native instant toggle |

- Preserve keyboard activation, both animation directions, and cancellation handling.
- Keep essential conclusions visible outside closed details.
- Additional examples belong in the closed component-reference disclosure so the original report remains the default presentation.

### Supporting content and optional controls

| Component | Extension of existing patterns |
| --- | --- |
| Evidence card | Neutral 1px outline; 8px radius; 24px padding; transparent fill; no shadow |
| Action list | Native numbered list; owner/deadline only if supplied |
| Timeline | Neutral 1px left rule; 16px inset; bold supplied date |
| Progress | Native `<progress>`; visible label and numeric value; 8px track; blue-600 accent |
| Loading | Native indeterminate progress only for actual loading; explicit label |
| Empty state | Neutral outlined 8px panel; 24px padding; plain limitation text |
| Error state | Danger admonition |
| Dialog | Native `<dialog>`; page fill; neutral outline; 8px radius; 24px padding; max-width 512px; 24px viewport margins |

- Dialog uses `aria-labelledby`, `showModal()`, labeled Close, Escape, and focus restoration.
- No fabricated milestones, loading decoration, or essential evidence hidden in modal UI.
- Mark demonstration states as examples; distinguish zero results from missing evidence.
- Omit all components the report content does not need.

### Accessibility, motion, fallbacks, and print

| Concern | Rule |
| --- | --- |
| Control transitions | 150ms color/border/shadow; 120ms press; scale .97 |
| Theme transition | Temporary 180ms color/background/border/shadow; remove transition class afterward |
| Disclosure motion | Original 190ms enhancement |
| Reduced motion | Disable nonessential animation and smooth scrolling, including Chart.js |
| Keyboard | Visible focus; semantic native controls; named local scroll regions |
| Libraries | Initialize independently; failures must retain readable evidence |
| CDN versions | Pin where practical; existing Tailwind v3 CDN is the exception |
| No-CDN reading | Keep semantic prose, exact values, raw code/TeX, and native disclosures usable |

| Print concern | Rule |
| --- | --- |
| Hide | Utilities, navigation, filters, forms, copy/dialog controls |
| Colors | White background, black text and syntax spans; remove shadows |
| Width / overflow | Full document width; unwrap scroll regions; wrap long code |
| Disclosure / filter state | Expand details; show all rows; restore prior states afterward |
| Rich evidence | Exact tables and readable diagram equivalents remain available |
| Page breaks | Keep headings with content; avoid splitting short figures/code/rows; allow long sections/tables to break |
| Validation | Inspect actual print output, not a screen-only screenshot |

## Do's and Don'ts

| Do | Don't |
| --- | --- |
| Read this contract and the original example | Treat Google's file format as permission to redesign |
| Preserve original utilities, title scale, KPI strip, prose grid, and rail | Move controls into the header or box every component |
| Preserve original blue/gray curved chart and horizontal Mermaid | Substitute the discarded showcase chart/diagram defaults |
| Change content, IDs, data, and necessary component count | Change palette, font, spacing, radii, or visual identity |
| Keep extensions as secondary examples using existing patterns | Replace the original report with a component catalog |
| Ask when an essential new interaction has no defined pattern | Invent a new design system |
| Verify evidence and label limitations | Copy fictional example claims into real reports |
| Test included components in both themes, desktop/mobile, and print | Claim untested behavior or Google/OpenAI affiliation |
