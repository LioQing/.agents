# Format and editing contract

## Input grammar

A top-level, unindented line containing `---` (optionally trailing whitespace) separates slides. The first separator is optional. Fenced/indented code, nested list/quote content, HTML blocks, and indented multiline instructions are not split. Empty interior slides are errors; an opening/trailing separator is ignored. Use `***`/`___` for in-slide rules and ATX (`#`) headings. Setext headings and YAML front matter are not supported.

The first nonblank line of a slide may be `instruction: plain text` or `instruction: |`. In block form, indent every nonblank instruction line by at least two spaces with a consistent base indent. More-indented lines retain their additional indentation. Blank lines are allowed. The first unindented nonblank line starts Markdown content. Tabs and other YAML block operators are not supported. Instruction text is not interpreted as YAML, Markdown, or shell code.

```markdown
instruction: |
  Arrange the supplied figures in a comparison.
  Keep all labels and values unchanged.

# Comparison

| Option | Time |
| --- | ---: |
| A | 12 |
| B | 18 |

---
# Deployment

> [!WARNING]
> Check the supplied deployment conditions first.
```

An empty instruction is treated as absent. Only one annotation is recognized at the start. A later `instruction:` line is ordinary content. Escape the colon in a literal opening field as `instruction\:` or place it in a code block.

The safe raw HTML subset covers ordinary prose tags, semantic tables, figures, details, spans/divs, and disabled task checkboxes. No raw scripts, styles, frames, event handlers, arbitrary IDs, or inline styling are carried over from Markdown. This avoids unintended execution and collisions with protected presentation regions. Agent customization can add richer semantic HTML through approved editable slots.

GitHub admonitions support `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, and `[!CAUTION]` at the start of a blockquote. Marker capitalization is exact. Multiline and nested Markdown are retained. Unknown markers remain ordinary quotes. Type labels and semantic classes stay constant across themes; appearance belongs to `DESIGN.md`.

## Commands

Here `builder` means `python <skill>/scripts/slide_builder.py` in an environment with the pinned requirements installed.

```text
builder build source.md --output output/deck.html
builder inspect output/deck.html
builder authorize output/deck.html --mode design --slides 1,3-5
builder authorize output/deck.html --mode preserve --slides 2
builder validate output/deck.html
builder capture output/deck.html --complete 1,3-5
builder build source.md --output output/deck.html --dry-run
```

- Output is JSON, suitable for agent inspection. Exit 0 means success; exit 2 means an error or unresolved build conflict. No output is replaced on a planning conflict.
- `--title` sets the HTML document title; it does not create a title slide.
- `--design <file>` selects an alternate design contract using the same marked CSS interface. Default: the skill's `DESIGN.md`.
- Slide selections accept `all`, stable IDs, or comma-separated numbers/ranges. Numbers are 1-based and refer to the current deck.
- `authorize` records the user's decision; it does not invent permission or perform the edits. Annotated slides keep the narrower `instruction` permission.
- `capture` saves allowed editable regions without touching the HTML. `--complete` records the agent's reviewed completion claim. Without that flag, changed slides stay `needs-agent`.
- `validate` checks structure/assets, not factual correctness, semantic rewrite scope, JavaScript syntax, or visual fit. A valid deck may still have pending slides. Browser review remains necessary.
- `inspect --slides 3 --history` includes saved bundles and previous versions for adaptation/recovery.

The work queue has `needs-permission`, `needs-agent`, and `complete` states. Script-only builds are immediately presentable but do not pretend that pending agent work was performed.

## Editable HTML slots

For each stable identifier, three paired markers define editable regions:

```html
<!-- slides:s-EXAMPLE:markup:start -->
<h1>Approved slide content</h1>
<!-- slides:s-EXAMPLE:markup:end -->
```

```css
/* slides:s-EXAMPLE:css:start */
#s-EXAMPLE .comparison { display: grid; grid-template-columns: 1fr 1fr; }
/* slides:s-EXAMPLE:css:end */
```

```javascript
// slides:s-EXAMPLE:script:start
const element = slide.querySelector('.comparison');
return {
  enter() { /* resume or size the component */ },
  leave() { /* pause animation or background activity */ },
  themeChanged() { /* recolor using api.theme */ },
  beforePrint() { /* prepare printable evidence */ },
  afterPrint() { /* restore presentation state */ },
  dispose() { /* remove listeners and release resources */ }
};
// slides:s-EXAMPLE:script:end
```

Replace only text **between** the markers. Preserve exact markers and all other bytes, including shell whitespace. The script region is already wrapped in `SlideDeck.register(id, (slide, api) => { ... })`; write a function body, not another wrapper or `<script>` tag.

The runtime creates a lifecycle instance once, when a slide first becomes visible or needs printing. `enter`/`leave` repeat on navigation, `themeChanged` runs for initialized instances, and `dispose` runs on page exit. Initialize new instances from the current `api.theme` rather than assuming the default theme. Query elements through `slide` and use slide-prefixed element IDs when needed.

`api` provides:

- `theme`: `light` or `dark`.
- `reducedMotion`: current preference.
- `announce(message)`: polite presentation status.
- `checkLayout()`: schedule a fresh overflow/image check.

`SlideDeck.goTo(number)` accepts 1-based slide numbers. `SlideDeck.checkLayout()` returns detected overflow/broken-image items, also available as `SlideDeck.layoutProblems`.

CSS selectors must begin with the slide's `#id` and remain inside that slide. Supported nested rules are `@media`, `@supports`, `@container`, and `@layer`. Global imports, font faces, keyframes, and other global rules are rejected. Use scoped CSS transitions or the Web Animations API when motion is requested. Never alter fixed canvas geometry or shared controls to conceal overflow.

Register events in the script slot, not HTML `on*` attributes. Markup may contain SVG/canvas/forms as authorized, but no scripts, styles, frames, linked stylesheets, or global metadata. Do not include closing `</script>` or `</style>` strings in their corresponding raw-text slots. Use escaped strings if necessary.

External libraries are optional. To use one, load a pinned dependency from the authorized slide lifecycle, handle load failure, retain accessible fallback content, and clean up resources. Browser review must cover the actual dependency and print behavior. No automatic library downloads happen during build.

The original instruction and Markdown are held in a protected, safely escaped JSON record. Source controls use `textContent`, never interpreted HTML. They display original input, not the current customized HTML.

## Rebuild identity and conflicts

Exact source and instruction fingerprints match unchanged slides one-to-one. An entirely unchanged input also preserves identity for repeated identical slides. Once a deck with duplicates changes, duplicate identity is not guessed by position.

Local source images and captured custom images are fingerprinted. The original-source directory and output directory are part of compatibility. Relative image/link references are rebased from the Markdown file to the output location. Cross-drive references use file URLs. Missing local images are warnings during baseline build and errors during final validation.

Heading IDs are namespaced by stable slide ID. Markdown fragments such as `#comparison` resolve within the same slide first, or across slides when the target heading is unique. Duplicate headings receive `-1`, `-2`, etc. Broken or ambiguous fragment links require correction rather than guessing. Runtime fragment navigation opens the containing slide. Preserve heading IDs referenced elsewhere when customizing their visible text.

Captured local CSS URLs and media/SVG image references are also fingerprinted. Dynamically constructed script URLs and complex `srcset` references cannot be discovered reliably; the agent must review them separately.

Changed slides require approval even if they have not yet been customized, so the user never gets silent regeneration of an earlier presentation. Changed source without a unique exact match also requires an identity decision:

```text
builder build source.md --output deck.html --dry-run
builder build source.md --output deck.html --map 2=s-OLDID --resolve s-OLDID=adapt
builder build source.md --output deck.html --drop s-REMOVEDID
```

- `--map NEW_NUMBER=OLD_ID`: explicitly associate current source with a prior slide.
- `--resolve OLD_ID=regenerate`: start that changed slide from the new baseline.
- `--resolve OLD_ID=adapt`: also starts from the new baseline but retains the previous captured bundle as adaptation context. The agent applies an approved adaptation; the script does not merge it.
- `--drop OLD_ID`: explicitly retire a prior slide with no current match. Its bundle stays in history.

All required conflict choices may be combined in one build. Do not supply them without the user's approval. Newly changed/unannotated source receives no inherited rewrite permission. Previously approved slides with unchanged source but changed theme/assets also require review and renewed customization scope.

If output has uncaptured HTML edits, validate and capture them first. If the user explicitly wants to discard them, `--discard-edits` backs up the current HTML/state before replacement. If output has no state, `--replace-existing` performs the same backup after explicit approval. The backup directory is `.<deck-name>.slides-history/` beside the deck. An incompatible/corrupt state or missing HTML must be restored or handled through a new output path, not silently ignored.

The companion JSON includes version, input/output, source/compatibility fingerprints, protected-shell hash, last captured HTML hash, per-slide sources/permissions/status, baseline and captured bundles, local asset fingerprints, and recovery history. Do not hand-edit it.

## Validation and limitations

- Automated checks cover slide count/order/IDs, protected records/shell, paired slots, scoped CSS, safe markup, required controls, local image existence, and internal anchors.
- Browser runtime checks overflow and failed loaded images on all slides. Code/table internal scrolling is allowed, but containers must fit. It does not prove readability or that every custom asynchronous component was inspected.
- Review every customized slide by visiting it, checking the content and interactions, and inspecting console errors. Exercise both themes, desktop/mobile fitting, overview/source, fullscreen where supported, keyboard/input behavior, and PDF pagination.
- Browser fragment URLs identify the active slide for bookmarking this same document; they are not separate slide files.
- CSS print pages are fixed landscape presentation size. Actual browser print settings can override them; PDF export should honor CSS page size. Overflow remains a content problem, not a hidden clipping fix.
- No automatic factual verification, semantic merges, online research, speaker notes, presenter view, PowerPoint export, programmatic production PDF exporter, or guaranteed offline packaging.
- Remote asset changes cannot be detected from local hashes. SVG/data-image inputs are intentionally conservative; authorized content SVGs can be added through agent markup.
- State is unnecessary to present, but is required to rebuild safely. The deck may still reference local/online assets, so retain those references when sharing.

## Developer checks

```text
python -m unittest discover -s <skill>/tests -p test_*.py
```

Browser tests use optional `playwright` and `pypdf`, plus an installed Chromium-family browser. They are not runtime dependencies. Test artifacts belong in a task-specific temporary directory, never in the user's source tree.

```text
python <skill>/tests/browser_check.py --artifacts <new-temp-directory> --browser <installed-chromium-executable>
```
