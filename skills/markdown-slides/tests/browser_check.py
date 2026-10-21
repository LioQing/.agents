#!/usr/bin/env python3
"""Optional browser integration checks using an installed Chromium-family browser."""

import argparse
import base64
import contextlib
import importlib.util
import io
import json
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("slide_builder", ROOT / "scripts" / "slide_builder.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

SOURCE = """---
# Markdown Slides

A scripted baseline, followed by permission-scoped agent customization.

[Jump to comparison](#comparison)

- Fixed 16:9 canvas.
- Original source stays available.
- Captured edits survive compatible rebuilds.

Illustrative test deck, not a factual report.

---
# Comparison

| Option | Time (minutes) |
| --- | ---: |
| A | 12 |
| B | 18 |

> [!NOTE]
> These values are an illustrative test fixture.

---
# Reading guidance

> [!INFO]
> Background stays close to the evidence.

> [!TIP]
> Open the overview to jump to a slide.

> [!IMPORTANT]
> Capture approved edits before rebuilding.

---
# Review conditions

> [!WARNING]
> Changed source requires a rebuild decision.

> [!CAUTION]
> Existing unrecorded HTML edits are not overwritten silently.

---
# Code is content

```html
</script><script>window.evil = true</script>
---
instruction: This is literal code, not an agent instruction.
```

![Local fixture](pixel.png)

---
instruction: |
  Visualize the supplied comparison as a bar chart.
  Keep exact values available and label the example as illustrative.

# Supplied comparison

| Option | Time (minutes) |
| --- | ---: |
| A | 12 |
| B | 18 |
"""


def args(**values):
    defaults = dict(design=None, title=None, dry_run=False, map=[], drop=[], resolve=[], replace_existing=False, discard_edits=False)
    defaults.update(values)
    return type("Args", (), defaults)()


def invoke(function, arguments):
    with contextlib.redirect_stdout(io.StringIO()):
        result = function(arguments)
    assert result == 0, function.__name__


def replace_slot(document, identifier, kind, value):
    start, end = builder.slot_markers(identifier, kind)
    left, tail = document.split(start, 1)
    _, right = tail.split(end, 1)
    return left + start + value + end + right


def create_deck(directory):
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / "example.md"
    output = directory / "example.html"
    if output.exists() or builder.state_path(output).exists():
        raise RuntimeError("Use a new artifact directory for each browser test.")
    builder.atomic_write(source, SOURCE)
    (directory / "pixel.png").write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j8ioAAAAASUVORK5CYII="))
    invoke(builder.build, args(input=str(source), output=str(output)))
    invoke(builder.authorize, args(output=str(output), mode="preserve", slides="1-5"))
    state = builder.load_state(output)
    identifier = state["slides"][5]["id"]
    document = builder.read_text(output)
    markup = """<h1>A clear comparison</h1>
<p>Option B takes 6 minutes longer in this illustrative fixture.</p>
<figure aria-label="Comparison of option times in minutes">
  <div class="bars" role="img" aria-label="Option A: 12 minutes. Option B: 18 minutes.">
    <div class="bar-row"><span>A</span><div class="bar bar-a"></div><span>12 min</span></div>
    <div class="bar-row"><span>B</span><div class="bar bar-b"></div><span>18 min</span></div>
  </div>
  <figcaption>Illustrative values supplied in the original Markdown.</figcaption>
</figure>
<div class="table-scroll" tabindex="0" role="region" aria-label="Exact comparison values">
<table><thead><tr><th scope="col">Option</th><th scope="col">Time (minutes)</th></tr></thead><tbody><tr><td>A</td><td>12</td></tr><tr><td>B</td><td>18</td></tr></tbody></table>
</div>
<label>Local selection <input class="test-input" type="text" value="A" aria-label="Local selection"></label>
<details><summary>Method</summary><p>No measurements were inferred. Difference: 18 - 12 = 6.</p></details>
"""
    css = f"""
#{identifier} .bars {{ border-block: 1px solid var(--rule); padding: 12px 0; }}
#{identifier} .bar-row {{ display: grid; grid-template-columns: 32px 1fr 100px; align-items: center; gap: 16px; margin: 8px 0; font-size: 20px; }}
#{identifier} .bar {{ height: 24px; background: var(--chart-primary); }}
#{identifier} .bar-a {{ width: 60%; }}
#{identifier} .bar-b {{ width: 90%; background: var(--chart-secondary); }}
#{identifier} figure {{ margin-top: 0; margin-bottom: 16px; }}
#{identifier} .slide-content > p {{ margin-bottom: 16px; }}
#{identifier} .table-scroll {{ margin-bottom: 16px; }}
#{identifier} td, #{identifier} th {{ padding: 8px 12px; }}
#{identifier} label {{ font-size: 20px; }}
#{identifier} input {{ color: var(--ink); border: 1px solid var(--outline); background: var(--page); font: inherit; padding: 4px; }}
#{identifier} details {{ margin-top: 16px; padding: 8px 16px; }}
#{identifier} details p {{ margin: 4px 0; font-size: 16px; }}
"""
    script = """
slide.dataset.initialTheme = api.theme;
slide.dataset.reducedMotion = String(api.reducedMotion);
return {
  enter() { slide.dataset.entered = String(Number(slide.dataset.entered || 0) + 1); },
  leave() { slide.dataset.left = 'true'; },
  themeChanged() { slide.dataset.changedTheme = api.theme; },
  beforePrint() { slide.dataset.printed = 'true'; },
  afterPrint() { slide.dataset.afterPrinted = 'true'; }
};
"""
    for kind, value in (("markup", markup), ("css", css), ("script", script)):
        document = replace_slot(document, identifier, kind, value)
    builder.atomic_write(output, document)
    invoke(builder.validate, args(output=str(output)))
    invoke(builder.capture, args(output=str(output), complete="6"))
    invoke(builder.build, args(input=str(source), output=str(output)))
    return output, identifier


def check_control_bar(page, touch=False):
    bar = page.locator("#control-bar").bounding_box()
    canvas = page.locator("#canvas-fit").bounding_box()
    viewport = page.viewport_size
    assert canvas["y"] + canvas["height"] <= bar["y"] + 1
    assert abs(bar["y"] + bar["height"] - viewport["height"]) <= 1
    assert page.locator("#control-bar").evaluate("node => getComputedStyle(node).borderTopWidth") == "1px"
    for button in page.locator("#control-bar button").all():
        bounds = button.bounding_box()
        assert bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= viewport["width"]
        assert bounds["y"] >= bar["y"] and bounds["y"] + bounds["height"] <= viewport["height"]
        assert bounds["height"] >= (44 if touch else 32)
    assert page.evaluate("document.documentElement.scrollWidth") <= viewport["width"]


def check_overview_panel(page):
    # ResizeObserver updates the canvas after the grid allocates the panel's column.
    page.wait_for_function("""() => {
      const stage = document.querySelector('#stage').getBoundingClientRect();
      const canvas = document.querySelector('#canvas-fit').getBoundingClientRect();
      return canvas.left >= stage.left - 1 && canvas.right <= stage.right + 1
        && canvas.top >= stage.top - 1 && canvas.bottom <= stage.bottom + 1;
    }""")
    stage = page.locator("#stage").bounding_box()
    canvas = page.locator("#canvas-fit").bounding_box()
    panel = page.locator("#overview").bounding_box()
    bar = page.locator("#control-bar").bounding_box()
    assert canvas["width"] > 0 and canvas["height"] > 0
    assert stage["x"] + stage["width"] < panel["x"]
    assert canvas["x"] + canvas["width"] < panel["x"]
    assert panel["x"] + panel["width"] <= page.viewport_size["width"]
    assert panel["y"] + panel["height"] <= bar["y"]
    assert abs(canvas["width"] / canvas["height"] - 16 / 9) < .01
    assert page.locator("#overview").evaluate("node => node.scrollWidth <= node.clientWidth")
    check_control_bar(page, touch=page.viewport_size["width"] <= 640)


def run(directory, executable):
    output, custom = create_deck(directory)
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(executable), headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="light")
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
        page.goto(output.as_uri())
        page.wait_for_function("window.SlideDeck && document.querySelector('#slide-counter').textContent === '1 / 6'")
        assert page.evaluate("typeof window.evil") == "undefined"
        assert page.locator("#deck > .slide:not([hidden])").count() == 1
        assert page.locator("#deck > .slide[hidden][inert]").count() == 5
        results.append("source escaping and hidden-slide accessibility")
        check_control_bar(page)
        results.append("unified bottom bar, divider, and non-overlapping canvas")
        page.locator('.slide:not([hidden]) a').click()
        page.wait_for_function("SlideDeck.current === 2")
        page.keyboard.press("Home")
        # The link retains focus in a hidden slide; restore ordinary page focus explicitly.
        page.evaluate("document.activeElement.blur()")
        page.evaluate("SlideDeck.goTo(1)")
        results.append("cross-slide heading fragment links")
        page.click("#next-slide")
        assert page.locator("#slide-counter").inner_text() == "2 / 6"
        page.keyboard.press("ArrowRight")
        assert page.locator("#slide-counter").inner_text() == "3 / 6"
        page.keyboard.press("Home")
        assert page.locator("#slide-counter").inner_text() == "1 / 6"
        page.keyboard.press("End")
        assert page.locator("#slide-counter").inner_text() == "6 / 6"
        assert page.locator(f"#{custom}").get_attribute("data-entered") == "1"
        page.locator(".test-input").focus()
        page.keyboard.press("ArrowLeft")
        assert page.locator("#slide-counter").inner_text() == "6 / 6"
        page.locator(".test-input").blur()
        page.keyboard.press("ArrowLeft")
        assert page.locator(f"#{custom}").get_attribute("data-left") == "true"
        results.append("button/keyboard navigation and input isolation")
        full_stage_width = page.locator("#stage").bounding_box()["width"]
        page.click("#overview-toggle")
        assert page.locator("#overview").is_visible()
        assert page.locator("#overview-toggle").get_attribute("aria-expanded") == "true"
        check_overview_panel(page)
        assert page.locator("#stage").bounding_box()["width"] < full_stage_width
        row = page.locator("#overview [data-go-slide]").nth(5)
        row.click()
        assert page.locator("#overview").is_visible()
        assert page.locator("#overview-toggle").get_attribute("aria-expanded") == "true"
        assert row.get_attribute("aria-current") == "page"
        assert row.evaluate("node => node === document.activeElement")
        assert page.locator("#slide-counter").inner_text() == "6 / 6"
        page.click("#previous-slide")
        assert page.locator("#slide-counter").inner_text() == "5 / 6"
        assert page.locator("#overview").is_visible()
        assert page.locator("#overview [aria-current]").get_attribute("data-go-slide") == page.locator("#deck > .slide:not([hidden])").get_attribute("id")
        page.click("#next-slide")
        assert page.locator("#overview").is_visible()
        page.screenshot(path=str(directory / "controls-overview-light.png"))
        page.click("#source-toggle")
        page.keyboard.press("Escape")
        assert page.locator("#source-dialog").is_hidden()
        assert page.locator("#overview").is_visible()
        page.click("#overview-close")
        assert page.locator("#overview").is_hidden()
        assert page.locator("#overview-toggle").get_attribute("aria-expanded") == "false"
        assert page.evaluate("document.activeElement.id") == "overview-toggle"
        assert abs(page.locator("#stage").bounding_box()["width"] - full_stage_width) <= 1
        page.click("#overview-toggle")
        page.keyboard.press("Escape")
        assert page.locator("#overview").is_hidden()
        assert page.evaluate("document.activeElement.id") == "overview-toggle"
        page.click("#overview-toggle")
        page.click("#overview-toggle")
        assert page.locator("#overview").is_hidden()
        page.click("#source-toggle")
        assert page.locator("#source-dialog").is_visible()
        assert "instruction: |" in page.locator("#source-instruction").inner_text()
        assert "# Supplied comparison" in page.locator("#source-markdown").inner_text()
        assert "A clear comparison" not in page.locator("#source-markdown").inner_text()
        page.click("#source-close")
        assert page.locator("#source-dialog").is_hidden()
        assert page.evaluate("document.activeElement.id") == "source-toggle"
        results.append("persistent overview, navigation, close/toggle/Escape, focus, and original-source modal")
        page.click("#theme-toggle")
        assert page.locator("html").get_attribute("class") == "dark"
        assert page.locator(f"#{custom}").get_attribute("data-changed-theme") == "dark"
        page.reload()
        page.wait_for_function("window.SlideDeck?.current === 6")
        assert page.locator("html").get_attribute("class") == "dark"
        assert page.locator(f"#{custom}").get_attribute("data-initial-theme") == "dark"
        page.goto(output.as_uri() + "?theme=light#" + custom)
        page.wait_for_function("window.SlideDeck?.current === 6")
        assert not page.evaluate("document.documentElement.classList.contains('dark')")
        assert page.evaluate("localStorage.getItem('slides-theme')") == "dark"
        results.append("theme persistence, preview override, and lifecycle recoloring")
        if page.evaluate("document.fullscreenEnabled"):
            page.click("#fullscreen-toggle")
            page.wait_for_function("!!document.fullscreenElement")
            page.click("#fullscreen-toggle")
            page.wait_for_function("!document.fullscreenElement")
            results.append("fullscreen entry and exit")
        else:
            assert page.locator("#fullscreen-toggle").is_disabled()
            results.append("unsupported fullscreen fallback")
        for number in range(1, 7):
            page.evaluate("number => SlideDeck.goTo(number)", number)
            page.wait_for_timeout(50)
        problems = page.evaluate("SlideDeck.checkLayout()")
        assert not problems, problems
        page.evaluate("SlideDeck.goTo(3)")
        info = page.locator(".admonition-info")
        assert info.get_attribute("role") == "note"
        assert info.locator(".admonition-title").inner_text() == "Info"
        assert info.evaluate("node => getComputedStyle(node).borderTopColor") == "rgb(29, 78, 216)"
        assert info.locator(".admonition-title").evaluate("node => getComputedStyle(node).color") == "rgb(29, 78, 216)"
        page.screenshot(path=str(directory / "admonitions-light.png"))
        page.click("#theme-toggle")
        assert info.evaluate("node => getComputedStyle(node).borderTopColor") == "rgb(96, 165, 250)"
        assert info.locator(".admonition-title").evaluate("node => getComputedStyle(node).color") == "rgb(96, 165, 250)"
        page.screenshot(path=str(directory / "admonitions-dark.png"))
        page.evaluate("SlideDeck.goTo(6)")
        page.screenshot(path=str(directory / "custom-slide-dark.png"))
        page.click("#overview-toggle")
        check_overview_panel(page)
        page.screenshot(path=str(directory / "controls-overview-dark.png"))
        page.click("#overview-close")
        results.append("all-slide overflow/image checks and light/dark rendering")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(100)
        bounds = page.locator("#canvas-fit").bounding_box()
        assert bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= 390
        assert abs(bounds["width"] / bounds["height"] - 16 / 9) < .01
        assert page.evaluate("document.documentElement.scrollWidth") <= 390
        assert page.locator("#next-slide").bounding_box()["height"] >= 44
        check_control_bar(page, touch=True)
        page.screenshot(path=str(directory / "mobile.png"))
        page.click("#overview-toggle")
        page.locator("#overview [data-go-slide]").first.click()
        assert page.locator("#overview").is_visible()
        check_overview_panel(page)
        overview = page.locator("#overview").bounding_box()
        assert overview["y"] + overview["height"] <= page.locator("#control-bar").bounding_box()["y"]
        page.screenshot(path=str(directory / "controls-overview-mobile.png"))
        page.click("#overview-close")
        for width, height in ((320, 568), (640, 480), (667, 375), (768, 1024)):
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(100)
            check_control_bar(page, touch=width <= 640)
            page.click("#overview-toggle")
            check_overview_panel(page)
            page.click("#overview-close")
        page.click("#overview-toggle")
        results.append("mobile/tablet/landscape fitting, wrapped bar, overview, and touch targets")
        page.set_viewport_size({"width": 1440, "height": 900})
        check_overview_panel(page)
        results.append("non-overlapping right overview panel, canvas refitting, and full-width restoration")
        pdf = directory / "presentation.pdf"
        page.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
        reader = PdfReader(pdf)
        assert len(reader.pages) == 6, f"Expected 6 PDF pages, got {len(reader.pages)}"
        headings = ["Markdown Slides", "Comparison", "Reading guidance", "Review conditions", "Code is content", "A clear comparison"]
        for number, printed in enumerate(reader.pages):
            text = printed.extract_text()
            assert headings[number] in text, (number, text)
            assert "Overview" not in text and "Fullscreen" not in text and "Original slide source" not in text
        assert page.locator(f"#{custom}").get_attribute("data-printed") == "true"
        assert page.locator(f"#{custom}").get_attribute("data-after-printed") == "true"
        assert not page.locator(f"#{custom} details").evaluate("node => node.open")
        page.emulate_media(media="print")
        assert page.locator("#control-bar").is_hidden()
        assert page.locator("#utilities").is_hidden()
        assert page.locator(".slide th").first.evaluate("node => getComputedStyle(node).color") == "rgb(0, 0, 0)"
        page.emulate_media(media="screen")
        results.append("actual 6-page PDF, hidden controls, print hooks, and restored details")
        page.evaluate("""() => {
          const node = document.createElement('div'); node.style.height = '900px';
          document.querySelector('.slide-content').append(node); SlideDeck.goTo(1);
        }""")
        assert any(problem["type"] == "overflow" for problem in page.evaluate("SlideDeck.checkLayout()"))
        assert page.locator("#layout-warning").is_visible()
        results.append("overflow detection and visible warning")
        assert not errors, errors
        context.close()
        reduced = browser.new_context(reduced_motion="reduce", color_scheme="light")
        page = reduced.new_page()
        page.goto(output.as_uri() + "#" + custom)
        page.wait_for_function("window.SlideDeck?.current === 6")
        assert page.locator(f"#{custom}").get_attribute("data-reduced-motion") == "true"
        results.append("reduced-motion lifecycle preference")
        reduced.close()
        browser.close()
    builder.atomic_write(directory / "browser-results.json", json.dumps({"passed": results, "console_errors": errors, "artifacts": str(directory)}, indent=2))
    print(json.dumps({"passed": results, "artifacts": str(directory)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--browser", type=Path, required=True)
    options = parser.parse_args()
    run(options.artifacts.resolve(), options.browser.resolve())
