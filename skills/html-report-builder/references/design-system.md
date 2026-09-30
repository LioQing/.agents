# Design System

## Direction

Use the aesthetic of high-quality developer documentation without reproducing any product's branding or global navigation. The report is a document, not a dashboard or marketing page.

## Layout

- No top navigation bar and no left sidebar.
- Center the overall frame and use a two-column desktop grid: the reading column first, a 180–220px right rail second.
- Keep the right rail sticky with an `On this page` label and a slim vertical rule.
- Collapse the right rail below large breakpoints and expose the same links in a small `<details>` element.
- Prefer section spacing of 64–96px over card-heavy grouping.

## Typography

- Use a clean system sans stack for prose and a system monospace stack for code.
- Body text: 15–17px, comfortable line height, neutral foreground.
- H1: 36–48px and tightly tracked; avoid billboard-sized type.
- H2: 24–30px with a top rule or clear whitespace transition when useful.
- Labels and metadata: 11–13px, medium weight, often uppercase with tracking.

## Color and Surfaces

- Light: white page, near-black text, zinc/gray secondary text, light gray borders.
- Dark: near-black page rather than blue-black, off-white text, muted gray secondary text, charcoal borders.
- Use one restrained accent (blue by default) for links, active navigation, and chart focus.
- Status colors should carry meaning and include text/icon cues; do not rely on color alone.

## Components

- Prefer flat sections and thin dividers to floating cards.
- KPI tiles may use subtle borders and small radii; keep shadows absent or barely visible.
- Buttons should be compact, pill or small-radius, with clear hover/focus states.
- Tables use hairline row separators, tabular numerals, sticky headers only for genuinely long tables, and horizontal overflow on mobile.
- Code blocks use a near-black surface in both themes, a language label, and a copy control.
- Callouts use a complete 1px outline, 10–12px radius, transparent or page-matched fill, a leading semantic Google Material Symbol, and one concise message. Use neutral styling with `info`, green with `check_circle` for success, and amber/yellow with `warning` for warnings; preserve explicit wording so color is never the only signal.
- Interactive disclosures and similar expandable rows must each have their own complete border and rounded container. Make the entire summary row clickable, keep at least 44px of target height, show a visible focus ring, and distinguish the open state with a subtle border change. Do not present clickable rows as borderless text separated only by horizontal rules.
- Use Google Material Symbols Outlined whenever an interface icon is needed. Load only the named icons used on the page through the Google Fonts `icon_names` parameter when possible. Do not hand-draw SVG icons, use Unicode lookalikes, or improvise icon geometry.

## Interaction

- Use `IntersectionObserver` for active section state.
- Respect `prefers-reduced-motion`.
- Persist the user's theme choice in `localStorage`.
- Give buttons and inputs 120–160ms color, border, shadow, and press-state transitions. A subtle pressed scale around `0.97` is sufficient; avoid bounce or spring effects.
- Cross-fade theme color, background, and border changes over roughly 180ms, then remove temporary transition classes so ordinary page updates remain immediate.
- Animate disclosure content in both directions over roughly 180–200ms using height plus opacity and at most a 4px vertical offset. Keep semantic `<details>/<summary>` behavior and keyboard activation; fall back to instant native toggling when reduced motion is requested.
- Avoid scroll-jacking and decorative animation.
- Re-render or recolor third-party charts/diagrams when the theme changes.

## Print

- Hide theme, print, filter, copy, and navigation controls.
- Force a white background and black text.
- Avoid breaking figures, tables, and code blocks across pages where practical.
- Expand essential collapsible content or ensure its summary communicates what is omitted.
