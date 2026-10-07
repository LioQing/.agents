---
version: alpha
name: Quiet Report
description: Deterministic visual system for single-page evidence-led reports, using Google's DESIGN.md format, not Google branding or Material page layouts.
colors:
  primary: "#18181b"
  secondary: "#52525b"
  tertiary: "#1d4ed8"
  neutral: "#ffffff"
  surface: "#fafafa"
  border: "#d4d4d8"
  hover: "#f4f4f5"
  on-accent: "#ffffff"
  accent-hover: "#1e40af"
  info: "#1d4ed8"
  success: "#047857"
  warning: "#92400e"
  danger: "#b91c1c"
  tip: "#6d28d9"
  dark-primary: "#f4f4f5"
  dark-secondary: "#a1a1aa"
  dark-tertiary: "#93c5fd"
  dark-neutral: "#09090b"
  dark-surface: "#18181b"
  dark-border: "#52525b"
  dark-hover: "#27272a"
  dark-on-accent: "#09090b"
  dark-accent-hover: "#bfdbfe"
  dark-info: "#93c5fd"
  dark-success: "#6ee7b7"
  dark-warning: "#fcd34d"
  dark-danger: "#fca5a5"
  dark-tip: "#c4b5fd"
  code-background: "#0d0d0d"
  code-text: "#f4f4f5"
  code-muted: "#a1a1aa"
  code-border: "#52525b"
typography:
  h1: { fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', fontSize: 40px, fontWeight: 600, lineHeight: 1.15, letterSpacing: -0.035em }
  h1-mobile: { fontFamily: system-ui, fontSize: 32px, fontWeight: 600, lineHeight: 1.2, letterSpacing: -0.035em }
  h2: { fontFamily: system-ui, fontSize: 28px, fontWeight: 600, lineHeight: 1.25, letterSpacing: -0.02em }
  h2-mobile: { fontFamily: system-ui, fontSize: 24px, fontWeight: 600, lineHeight: 1.3, letterSpacing: -0.02em }
  h3: { fontFamily: system-ui, fontSize: 20px, fontWeight: 600, lineHeight: 1.4 }
  lead: { fontFamily: system-ui, fontSize: 18px, fontWeight: 400, lineHeight: 1.7 }
  body: { fontFamily: system-ui, fontSize: 16px, fontWeight: 400, lineHeight: 1.75 }
  small: { fontFamily: system-ui, fontSize: 14px, fontWeight: 400, lineHeight: 1.6 }
  caption: { fontFamily: system-ui, fontSize: 12px, fontWeight: 400, lineHeight: 1.6 }
  label: { fontFamily: system-ui, fontSize: 12px, fontWeight: 600, lineHeight: 1.5, letterSpacing: 0.1em }
  control: { fontFamily: system-ui, fontSize: 14px, fontWeight: 500, lineHeight: 1.5 }
  metric: { fontFamily: system-ui, fontSize: 28px, fontWeight: 600, lineHeight: 1.2, fontFeature: '"tnum"' }
  code: { fontFamily: 'ui-monospace, "Cascadia Code", "SFMono-Regular", Consolas, monospace', fontSize: 13px, fontWeight: 400, lineHeight: 1.7 }
rounded:
  none: 0px
  control: 6px
  container: 8px
  callout: 12px
  pill: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  xxl: 32px
  section: 80px
  section-mobile: 56px
  frame: 1180px
  reading: 820px
  rail: 200px
  gutter: 56px
  margin: 40px
  margin-mobile: 24px
components:
  page: { backgroundColor: "{colors.neutral}", textColor: "{colors.primary}", typography: "{typography.body}" }
  page-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-primary}" }
  secondary-text: { backgroundColor: "{colors.neutral}", textColor: "{colors.secondary}" }
  secondary-text-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-secondary}" }
  button-primary: { backgroundColor: "{colors.tertiary}", textColor: "{colors.on-accent}", typography: "{typography.control}", rounded: "{rounded.control}", height: 44px, padding: 12px }
  button-primary-hover: { backgroundColor: "{colors.accent-hover}", textColor: "{colors.on-accent}" }
  button-primary-dark: { backgroundColor: "{colors.dark-tertiary}", textColor: "{colors.dark-on-accent}" }
  button-primary-dark-hover: { backgroundColor: "{colors.dark-accent-hover}", textColor: "{colors.dark-on-accent}" }
  button-secondary: { backgroundColor: "{colors.neutral}", textColor: "{colors.primary}", rounded: "{rounded.control}", height: 44px }
  button-secondary-hover: { backgroundColor: "{colors.hover}" }
  button-secondary-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-primary}" }
  button-secondary-dark-hover: { backgroundColor: "{colors.dark-hover}" }
  input: { backgroundColor: "{colors.neutral}", textColor: "{colors.primary}", rounded: "{rounded.control}", height: 44px, typography: "{typography.control}" }
  input-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-primary}" }
  panel: { backgroundColor: "{colors.surface}", textColor: "{colors.primary}", rounded: "{rounded.container}", padding: 24px }
  panel-dark: { backgroundColor: "{colors.dark-surface}", textColor: "{colors.dark-primary}" }
  note: { backgroundColor: "{colors.neutral}", textColor: "{colors.secondary}", rounded: "{rounded.callout}", padding: 16px }
  info: { backgroundColor: "{colors.neutral}", textColor: "{colors.info}" }
  success: { backgroundColor: "{colors.neutral}", textColor: "{colors.success}" }
  warning: { backgroundColor: "{colors.neutral}", textColor: "{colors.warning}" }
  danger: { backgroundColor: "{colors.neutral}", textColor: "{colors.danger}" }
  tip: { backgroundColor: "{colors.neutral}", textColor: "{colors.tip}" }
  note-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-secondary}" }
  info-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-info}" }
  success-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-success}" }
  warning-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-warning}" }
  danger-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-danger}" }
  tip-dark: { backgroundColor: "{colors.dark-neutral}", textColor: "{colors.dark-tip}" }
  code: { backgroundColor: "{colors.code-background}", textColor: "{colors.code-text}", typography: "{typography.code}", rounded: "{rounded.container}" }
  code-toolbar: { backgroundColor: "{colors.code-background}", textColor: "{colors.code-muted}" }
  code-outline: { backgroundColor: "{colors.code-border}" }
  outline: { backgroundColor: "{colors.border}" }
  outline-dark: { backgroundColor: "{colors.dark-border}" }
---

# Quiet Report design contract

## Overview

- **Authority:** This file defines the design for every `html-report-builder` output.
- **Format:** [Google Labs' DESIGN.md alpha specification](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md), checked on 7 October 2026.
- **Identity:** Our report aesthetic in Google's format, not Google branding or a Material Design redesign.
- **Audience:** Readers evaluating evidence, not dashboard operators.
- **Aesthetic:** Flat surfaces, restrained blue, thin outlines, generous spacing, secondary right rail.
- **Agent decisions:** Content and useful evidence-backed components only, not visual design.
- **Implementation:** Reuse matching markup, tokens, and behavior from `assets/example-report.html`; omit unused components.
- **Precedence:** Explicit user design overrides take priority; otherwise all tokens and rules below are mandatory.
- **Runtime:** Never fetch this document or private source data from the report.

| Token | CSS variable | Theme behavior |
| --- | --- | --- |
| `primary` | `--text` | Substitute `dark-primary` under `.dark` |
| `secondary` | `--muted` | Substitute `dark-secondary` |
| `tertiary` | `--accent` | Substitute `dark-tertiary` |
| `neutral` | `--page` | Substitute `dark-neutral` |
| Other color tokens | Same name prefixed with `--` | Substitute the corresponding `dark-*` token |
| `code-*` | Same name prefixed with `--` | Unchanged in both themes |

## Colors

| Role | Token / rule |
| --- | --- |
| Page themes | White light theme; near-black dark theme |
| Table headers, quotations, diagram nodes, equations, loading/empty panels | `surface` |
| Hovered controls and open disclosure summaries | `hover` |
| 1px boundaries and chart grids | `border` |
| Prose links, focus rings, active navigation, primary controls | `accent` |
| Admonition labels/icons/outlines and badges | Matching semantic token |
| Admonition message body | Normal `text`, no saturated fill |
| Normal text and controls | Contrast ≥4.5:1 |
| Large text | Contrast ≥3:1 |
| Meaningful non-text controls and focus indicators | Contrast ≥3:1 |

- Chart colors follow **accent, success, tip, warning, danger, muted**, using theme-correct values.
- Distinguish chart series with labels, dash patterns, and point shapes, not color alone.
- Split more than six series into small multiples; do not invent colors.
- Outside charts, color conveys semantic state, not arbitrary category branding.
- `outline` entries are boundary swatches, not text styles; divider colors need not meet text contrast.
- No transparent reading surfaces, gradients, glass, or decorative colors.

## Typography

| Content | Token / treatment |
| --- | --- |
| Report title | One `h1`; `h1-mobile` below 640px |
| Report sections | `h2`; `h2-mobile` below 640px |
| Subsections | `h3` |
| Executive takeaway | `lead` |
| Prose | `body`, maximum 72ch |
| Component descriptions and tables | `small` |
| Captions and helper text | `caption` |
| Uppercase metadata and eyebrows | `label` |
| KPI values | `metric`, tabular numerals |
| UI controls | `control` |
| Code and technical identifiers | `code` |
| Strong text | Weight 600 |
| Long links and identifiers | `overflow-wrap: anywhere` |
| Code blocks | Preserve lines; local horizontal scrolling |

- Use the exact `h1` system sans stack for all non-code text.
- Use the `code` monospace stack for block/inline code and technical identifiers.
- Use KaTeX's supplied math fonts; do not load Inter or decorative fonts.
- Use only weights 400/500/600; preserve the browser's 16px base size.
- Do not uppercase body copy; use tabular numerals for table values.

| Text element | Fixed styling / behavior |
| --- | --- |
| Bulleted / numbered lists | Native markers; 24px left padding; 8px between items |
| Nested lists | 12px top margin |
| Definition lists | Bold terms; description below with 4px spacing |
| Inline code and `kbd` | `surface`; 1px border; 4px radius; 2px vertical / 4px horizontal padding |
| Blockquotes | `surface`; 2px muted left rule; 16px padding; `small` text; attribution below |
| Prose links | Always underlined |
| Metadata / navigation links | Unadorned until hover or focus |
| Citations | Numbered anchors; ordered references; supplied publisher/title/date; return link |

- Never invent quotations, attributions, or citations.
- UI icons use **Google Material Symbols Outlined** only: 20px, weight 400, optical size 20, fill 0.
- Load only used icons, alphabetized in Google Fonts' `icon_names`.
- Give icon controls visible labels or accessible names; hide decorative icons from assistive technology.
- On icon-font failure, hide ligatures; retain labels and native disclosure markers.

## Layout

| Layout property | ≥1024px | <1024px |
| --- | --- | --- |
| Frame | Centered; max-width 1180px including padding | Single fluid column |
| Horizontal padding | 40px | 24px |
| Grid columns | `minmax(0, 820px) 200px` | `minmax(0, 1fr)` |
| Column gap | 56px | No rail gap |
| Contents | Right rail, sticky 32px from top | Fully outlined native disclosure after header |
| Rail height | Max `calc(100dvh - 64px)`; local scrolling | Hidden |

| Spacing property | ≥640px | <640px |
| --- | --- | --- |
| Frame top / bottom padding | 64px / 80px | 40px / 56px |
| Section bottom spacing | 80px | 56px |
| KPI columns | 4 | 2 at 400–639px; 1 below 400px |

| Document element | Fixed rule |
| --- | --- |
| DOM order | Reading column before right rail |
| Reading width | Maximum 820px; shrinks with available frame width |
| Both contents lists | Identical links; `aria-label="On this page"` |
| Header actions | Normal flow; above metadata; right-aligned; wrapping |
| Theme / Print controls | Secondary buttons |
| Header order | Actions → category/date/context → H1 → lead conclusion → optional KPIs → 1px bottom rule |
| Header bottom padding / following space | 32px / 32px |
| KPI container | Single 1px outline; 8px radius; shared dividers; 16px cell padding; no shadow |
| Section start, except first | 1px rule; 32px top padding |
| H2 → introduction | 12px |
| Heading block → component | 24px |
| Paragraph / component-group gap | 16px |
| Section scroll margin | 32px |
| Figures / tables / code | Full reading-column width |
| Plain prose | Maximum 72ch |

- Identify illustrative/example content in the first viewport when applicable.
- Omit unavailable metrics or show `N/A` with explanation; never invent deltas.
- No site shell, top navigation, left sidebar, or fixed floating toolbar.
- Do not wrap every paragraph in cards or force two-column executive prose.

## Elevation & Depth

| Element | Depth treatment |
| --- | --- |
| Ordinary controls, metrics, cards, charts, disclosures | No shadow; separate with 1px boundaries, whitespace, and `surface` |
| Tooltips | Code surface; no shadow |
| Native dialogs | Shadow `0 16px 48px rgb(0 0 0 / .2)`; backdrop `rgb(0 0 0 / .48)` |

- Do not stack decorative layers.

## Shapes

| Element | Radius |
| --- | --- |
| Controls | 6px |
| Components, figures, disclosures | 8px |
| Admonitions | 12px |
| Compact status badges | Pill |
| Straight rules and table dividers | 0px |

- Use existing Material Symbols for UI icons, not handwritten SVGs or Unicode substitutes.
- SVG/canvas is allowed for chart, diagram, and evidence content, not bespoke UI icons.
- No oversized container rounding.

## Components

### Navigation and theme

| Navigation property | Rule |
| --- | --- |
| Contents links | 1px left boundary; 16px horizontal padding; ≥44px target |
| Active link | Accent text/border; weight 600; `aria-current="location"` |
| Initial state | Explicit active link |
| Fragment click | Immediately update active state; preserve native fragment navigation |
| Scroll tracking | `IntersectionObserver` updates both lists |
| Active section on scroll | Last section crossing 35% of viewport height; final section at page bottom |
| Skip link | Keyboard-visible; targets `<main id="report">` |

- No scroll-jacking.
- Initialize `.dark` and `color-scheme` in a head script before paint.
- Read stored `report-theme`; otherwise use system preference.
- Catch storage failures; keep explicit choices working in memory.
- Treat `?theme=light` / `?theme=dark` as preview overrides; persist only after a user toggle.
- Theme toggle has a label and `aria-pressed` reflecting dark mode.
- Follow system changes only until the user makes an explicit choice.
- On theme change, recolor charts and rerender Mermaid from preserved source.
- Serialize diagram rendering so stale renders cannot overwrite the latest theme.

### Buttons, links, tooltips, and feedback

| Button property / variant | Rule |
| --- | --- |
| Common geometry | 44px tall; 12px horizontal padding; 8px icon gap |
| Secondary | Page fill; 1px border; text-colored label |
| Primary | Accent fill / on-accent text; only for a content-required main action |
| Tertiary | Text-only; same hit target |
| Code copy | Fixed code palette |
| Hover | Defined hover tokens |
| Focus | 2px accent outline; 2px offset |
| Pressed | Scale `.98` |
| Disabled | Native `disabled`; opacity `.55`; no press/hover motion |

- Keep meaningful labels; do not replace them with icon-only controls or fabricated CTAs.
- Copy/sort/filter/demo feedback uses a persistent nearby `role="status"` or `aria-live="polite"` line.
- A transient toast must not be the only result.
- Copy success: **Copied**.
- Copy failure: **Copy unavailable. Select the code to copy.**

| Tooltip property | Rule |
| --- | --- |
| Text / palette | `small`; code palette |
| Size | Max-width 240px; 8px padding; 6px radius |
| Open | Hover and keyboard focus |
| Association | `aria-describedby` |
| Close | Escape |
| Content | Optional explanation only; never the sole location of essential information |

### Forms and filters

| Form element | Rule |
| --- | --- |
| Visible label | 8px before control |
| Text / search / select | 44px tall; 12px padding; page fill; 1px border; `control` typography |
| Textarea | ≥112px tall; vertically resizable |
| Helper text | `caption`; 8px top spacing; `aria-describedby` |
| Validation error | Danger outline; explicit message; `aria-invalid="true"` |
| Placeholder | Example only, never a label replacement |
| Checkbox / radio | Native control; accent color; wrapped ≥44px label target |
| Radio group | Labeled fieldset |

- Include controls only for report-local interactions required by the content.
- Prefer native controls, sections, and disclosures over custom switches, tabs, menus, or submission flows.

### Tables and badges

| Table property | Rule |
| --- | --- |
| Semantics | Caption; scoped headers |
| Typography | 14px; tabular numeric values |
| Header / cells | Surface-filled header; 12px cell padding; 1px row dividers |
| Alignment | Labels left; numbers right |
| Scroll container | 1px outline; 8px radius; accessible name; keyboard focus; local horizontal scrolling |
| Sticky header | Only for >20 rows inside a bounded scroll region |
| Sort control | Labeled button; `swap_vert` icon; `aria-sort` on active `<th>` |
| Sort feedback | Announce column and direction in status line |
| Filter feedback | Visible row count; textual no-results panel; Reset filter control |
| Missing values | `N/A`, never zero |

- Do not cause horizontal page scrolling on mobile.
- Do not claim fictional example tables reconcile with unrelated KPIs.
- Badges use `small` text, pill radius, 1px semantic outline, and 4px vertical / 8px horizontal padding.
- Use explicit labels such as **Within target** or **Needs attention**; color is supplemental.
- Status badges are not interactive.

### Charts

| Evidence question | Chart type |
| --- | --- |
| Trend over time | Line |
| Category comparison | Horizontal bar |
| Discrete periods | Vertical bar |
| Relationship between variables | Scatter |
| No suitable visual pattern | Table instead |

| Chart.js property | Fixed value / behavior |
| --- | --- |
| Figure | 1px outline; 8px radius; 16px padding; labeled heading |
| Plot height | 300px mobile / 340px desktop |
| Caption / takeaway | Outside plot |
| Axis / legend / tooltip type | System font, 12px |
| Grid | 1px `border`; no axis frame |
| Ticks / legend labels | Theme-correct `muted` / `text` |
| Tooltips | `code-background` / `code-text`; values and units |
| Lines | 2px stroke; 3px points; tension 0; no fill |
| Bars | 4px radius; no border; zero baseline |
| Axes | Explicit units |
| Line baseline | Zero unless a nonzero baseline is explained in caption |
| Legend | Bottom for multiple series; omit for one named series |
| Animation | 180ms; 0 under reduced motion |
| Theme update | `update('none')` |

| Series | Color | Dash pattern | Point shape |
| --- | --- | --- | --- |
| 1 | `accent` | `[]` | `circle` |
| 2 | `success` | `[6,4]` | `rect` |
| 3 | `tip` | `[2,3]` | `triangle` |
| 4 | `warning` | `[8,3,2,3]` | `rectRot` |
| 5 | `danger` | `[10,3]` | `cross` |
| 6 | `muted` | `[1,4]` | `star` |

- Every chart needs an accessible name, written conclusion, and reachable exact-value table.
- Exact-value tables may be in a native disclosure.
- On library failure, hide the blank canvas and show a fallback pointing to the table.
- Print exact-value tables, not dark or unrendered canvases.
- No pie/donut, 3D, gradient, dual-axis, or decorative charts.
- The example shows line and horizontal bar; other types inherit the same settings.

### Diagrams and images

| Mermaid property | Fixed value / mapping |
| --- | --- |
| Theme / security | `theme: 'base'`; strict security |
| Font | System font, 14px |
| Primary / secondary / tertiary backgrounds | `surface` |
| Node text / borders | `text` / `border` |
| `lineColor` | `muted` |
| `edgeLabelBackground` | `page` |
| Nodes / edges | Uniform neutral nodes; labeled edges |
| Flow direction | Top-to-bottom at all widths |
| Figure | Same outline/radius as charts; 24px padding; local horizontal overflow |
| SVG sizing | `max-width: 100%; height: auto` |
| Source | Preserve in a `<template>` |

- No arbitrary per-node palettes.
- Keep a prose equivalent outside the generated diagram, visible without JS/CDNs.
- Show a short rendering-failure fallback; print the prose equivalent instead of theme-dependent SVG.
- Images use semantic figures, descriptive alt text, 8px radius, max-width 100%, and intrinsic aspect ratio.
- Include captions and supplied attribution; never add decorative stock images or crop evidence.
- The example's illustrative inline SVG is a content figure, not a bespoke UI icon or external dependency.

### Admonitions

| Admonition property | Rule |
| --- | --- |
| Container | Full 1px semantic outline; 12px radius; page fill |
| Spacing | 16px padding; 12px icon/text gap |
| Icon | Leading 20px Material Symbol |
| Text | `small`; bold explicit label; normal body color |
| Semantic emphasis | Label/icon/outline, not the whole message |
| Accessibility | Static `role="note"`, not an assertive live region |

| Type | Token | Icon | When to use |
| --- | --- | --- | --- |
| Note | secondary | info | Context or limitation without severity |
| Information | info | info | A factual clarification needed to read evidence |
| Tip | tip | lightbulb | Optional technique or shortcut |
| Success | success | check_circle | An evidenced successful outcome |
| Warning | warning | warning | Risk or caveat requiring attention |
| Danger | danger | error | A blocking condition or harmful action |

- **Important / Recommendation:** Information style with the explicit label.
- **Caution:** Warning style.
- Do not create extra palettes or mark unverified recommendations as success.

### Mathematics

| Math property | Rule |
| --- | --- |
| KaTeX configuration | `output: 'htmlAndMathml'`; `trust: false`; `throwOnError: false` |
| Inline delimiters | `\(...\)` |
| Display delimiters | `\[...\]` |
| Inline appearance | Inherit text color and size |
| Display panel | `surface` fill; 1px border; 8px radius; 24px padding; local horizontal overflow |
| Display type / alignment | 1.05em; centered |
| Definitions / interpretation | Left-aligned prose below |
| Multi-line expressions | `aligned` |
| Equation numbering | Only when cross-referenced |
| Rendering failure | Retain raw TeX and a prose equivalent |

- Do not use dollar delimiters that misinterpret currency.
- Include formulas only when they explain the evidence, not as decoration.

### Code

| Code property | Rule |
| --- | --- |
| Panel | Fixed `code-background` / `code-text` in both themes; 1px `code-border`; 8px radius |
| Toolbar | Language/filename; 44px Copy button |
| Code type / spacing | 13px monospace; 16px padding; preserved indentation |
| Overflow | Local scrolling; no line wrapping |
| Highlighting | Highlight.js; versioned GitHub Dark stylesheet |
| Copy source | `textContent`, excluding toolbar |
| Clipboard failure | Announce selectable-code fallback |
| Print | Black-on-white; wrap lines; retain language label |

- Escape embedded HTML; never use `innerHTML` for user-provided source.
- Add line numbers or screen line wrapping only when explicitly requested.

### Expandable sections

| Disclosure property | Rule |
| --- | --- |
| Semantics | Native `<details>/<summary>` |
| Container | Complete 1px border per item; 8px radius |
| Item gap | 12px |
| Summary | ≥44px height; 16px padding; weight 500 |
| Closed fill | `page` |
| Open summary / border | `hover` / `muted` |
| Icon | Trailing `add`; rotate 45° when open |
| Icon failure | Retain native marker |
| Focus ring | Inset to avoid clipping |
| Content padding | 16px sides and bottom |
| Animation | Example's 180ms height/opacity enhancement; both directions; cancellation-safe |
| Reduced motion / unsupported Web Animations | Instant native toggling |
| Mobile contents | Same disclosure pattern |
| Print | Expand all; restore previous states afterward; preserve table filters |

- Keep essential findings outside closed disclosures.
- Do not delay native keyboard activation or require JS to read details.

### Supporting panels, progress, and dialogs

| Supporting element | Rule |
| --- | --- |
| Evidence card | 1px border; 8px radius; 24px padding; no shadow; H3 plus body |
| Action list | Native numbered list; owner/deadline only when supplied |
| Timeline | Ordered list; 1px left rule; 16px inset; bold date; body text |
| Quantitative progress | Native `<progress>`; visible label and numeric text; 8px border-colored track; accent fill |
| Loading progress | Omit value; label **Loading**; only for an actual loading state |
| Empty / loading panel | `surface`; 1px border; 8px radius; 24px padding; explicit text |
| Error state | Danger admonition |

- Cards group distinct related evidence, not every section.
- Do not invent timeline milestones or use loading as animated decoration.
- Distinguish zero results from missing source data.
- Mark showcase states as demonstrations, not live measurements.

| Native dialog property | Rule |
| --- | --- |
| Purpose | Optional, content-required secondary detail only |
| Size | Max-width 480px; 24px viewport margin |
| Container | Page fill; 1px border; 8px radius; 24px padding |
| Title / close control | `aria-labelledby`; labeled Close button |
| Open | `showModal()`; focus an appropriate control |
| Close | Escape or Close; restore opener focus |

- Never hide executive evidence or essential chart values in a dialog/tooltip.
- Omit charts, images, forms, progress, and dialogs that the content does not need.

### Motion, accessibility, fallbacks, and print

| Interaction / accessibility property | Rule |
| --- | --- |
| Control motion | 150ms ease-out |
| Theme / disclosure motion | 180ms |
| Theme transition scope | Temporary color/background/border only |
| Reduced motion | Disable nonessential animation and smooth scrolling, including Chart.js |
| Keyboard | All controls operable; visible focus |
| Mobile targets | ≥44px |
| Semantics | Headings/landmarks; figure captions; table scopes; status announcements; explicit units |

- No motion beyond the specified small affordances.
- Preserve the example's embedded CSS so the layout remains readable without Tailwind.
- Libraries enhance existing prose/tables/TeX/code, never replace the only readable evidence.
- Pin dependencies where practical; Tailwind's v3 CDN is the intentional unversioned exception.
- Initialize libraries independently so one failure does not disable other interactions.
- Do not fetch source data at runtime.

| Print concern | Rule |
| --- | --- |
| Hide | Actions, navigation, forms, dialogs, copy controls, interaction status, sort/disclosure icons |
| Colors | White surfaces; black text, including syntax spans |
| Depth | Remove shadows |
| Overflow | Unwrap local scroll regions; wrap long code/links/TeX |
| Chart / diagram output | Exact-value tables / prose equivalents |
| Disclosures / filtered tables | Expand all disclosures; show every row |
| Page breaks | Keep headings/captions with following content; avoid breaks inside short figures/rows/code panels |
| Long sections / tables | Allow page breaks |
| Paper | 16mm margins; no forced paper size |
| KaTeX failure | Retain readable raw TeX |
| After print | Restore theme, filters, and disclosure state |

- Verify actual print output; a screen-only screenshot is not print verification.

## Do's and Don'ts

| Do | Don't |
| --- | --- |
| Read this contract and the example before building | Restyle by topic or randomly choose a design |
| Preserve theme/layout/component implementation | Invent fonts, palettes, spacing, chart skins, navigation, or icons |
| Replace content, IDs, component count, and data | Copy fictional showcase facts, unsupported claims, or example-only demos |
| Select components by their evidence purpose | Add components merely to demonstrate them |
| Reuse existing panel/type/semantic tokens for uncommon content | Invent an essential new interactive pattern; ask the user instead |
| Omit unnecessary controls | Redesign them to fill space |
| Test only components included in the output | Claim untested behavior works |
| Preserve our report identity | Copy Google/OpenAI branding or imply affiliation |

- Validate light/dark at desktop/mobile, theme persistence, keyboard/focus, links/scroll-spy, and print.
- Where included, also validate sorting/filtering/reset, copying, disclosures, library failures, and reduced motion.
