#!/usr/bin/env python3
"""Markdown slides: deterministic build, bounded edit capture, and conflict-safe rebuilds."""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urlsplit
import uuid

try:
    from bs4 import BeautifulSoup, Comment
    import bleach
    from markdown_it import MarkdownIt
    from mdit_py_plugins.tasklists import tasklists_plugin
    import tinycss2
except ImportError as error:
    raise SystemExit(f"Missing dependency: {error.name}. Install scripts/requirements.txt in a virtual environment.") from error


VERSION = "1.0.0"
STATE_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MODES = {"preserve", "design", "rewrite", "instruction"}
SAFE_TAGS = {
    "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "em", "s",
    "a", "img", "ul", "ol", "li", "blockquote", "pre", "code", "table", "thead",
    "tbody", "tr", "th", "td", "caption", "input", "div", "span", "aside", "figure",
    "figcaption", "details", "summary", "sub", "sup", "kbd", "dl", "dt", "dd",
}
SAFE_ATTRS = {
    "*": ["class", "title", "role", "aria-label"],
    "a": ["href", "title"], "img": ["src", "alt", "title", "width", "height"],
    "input": ["type", "checked", "disabled", "class"],
    "ol": ["start"], "th": ["scope", "align"], "td": ["align"], "details": ["open"],
}
PROTECTED_IDS = {
    "deck-structure", "deck-theme", "utilities", "overview-toggle", "source-toggle",
    "theme-toggle", "fullscreen-toggle", "print-deck", "overview", "stage", "canvas-fit",
    "deck", "navigation", "previous-slide", "slide-counter", "next-slide", "deck-status",
    "layout-warning", "source-dialog", "source-title", "source-instruction", "source-markdown",
    "source-close", "deck-source", "deck-runtime",
}


class BuildError(Exception):
    """An actionable error that must not replace existing work."""


def digest(value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_text(path):
    # Preserve newline bytes for the source viewer and edit fingerprints.
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return stream.read()


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def state_path(output):
    return Path(output).with_suffix(".slides-state.json")


def load_state(output):
    path = state_path(output)
    if not path.exists():
        return None
    try:
        state = json.loads(read_text(path))
        if state["version"] != STATE_VERSION or not isinstance(state["slides"], list):
            raise BuildError("Unsupported state format. Preserve the old deck and use a different output path.")
        identifiers = [slide["id"] for slide in state["slides"]]
        if len(identifiers) != len(set(identifiers)):
            raise BuildError("Duplicate identifiers in state; restore a known-good state file.")
        if Path(state["output"]).resolve() != Path(output).resolve():
            raise BuildError("State belongs to a different output path. Move/rebuild explicitly, not by overwriting this deck.")
        return state
    except (ValueError, KeyError, TypeError) as error:
        raise BuildError(f"Invalid state file: {path}") from error


def save_state(output, state):
    atomic_write(state_path(output), json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def backup(output):
    output = Path(output)
    if not output.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    history = output.parent / f".{output.stem}.slides-history"
    target = history / f"{stamp}-{output.name}"
    atomic_write(target, read_text(output))
    old_state = state_path(output)
    if old_state.exists():
        atomic_write(target.with_suffix(".slides-state.json"), read_text(old_state))
    return str(target)


def boundary_rule(state, start, end, silent):
    if state.level != 0 or state.parentType != "root" or state.tShift[start] != 0:
        return False
    line = state.src[state.bMarks[start]:state.eMarks[start]]
    if line.rstrip() != "---":
        return False
    if not silent:
        token = state.push("slide_boundary", "", 0)
        token.map = [start, start + 1]
        state.env["slide_start"] = start + 1
        state.line = start + 1
    return True


def instruction_rule(state, start, end, silent):
    if state.level != 0 or state.parentType != "root" or state.tShift[start] != 0:
        return False
    prior = state.src[state.bMarks[state.env.get("slide_start", 0)]:state.bMarks[start]]
    if prior.strip():
        return False
    line = state.src[state.bMarks[start]:state.eMarks[start]]
    match = re.fullmatch(r"instruction:\s*(.*)", line)
    if not match:
        return False
    if silent:
        return True
    value = match[1]
    stop = start + 1
    if value == "|":
        content = []
        indentation = None
        while stop < end:
            item = state.src[state.bMarks[stop]:state.eMarks[stop]]
            if not item.strip():
                content.append("")
                stop += 1
                continue
            spaces = len(item) - len(item.lstrip(" "))
            if item.startswith("\t"):
                raise BuildError(f"Line {stop + 1}: instruction indentation must use spaces, not tabs.")
            if not spaces:
                break
            if spaces < 2 or "\t" in item[:spaces + 1]:
                raise BuildError(f"Line {stop + 1}: instruction lines require at least two spaces, without tabs.")
            if indentation is None:
                indentation = spaces
            if spaces < indentation:
                raise BuildError(f"Line {stop + 1}: inconsistent instruction indentation.")
            content.append(item[indentation:])
            stop += 1
        value = "\n".join(content).rstrip()
    elif value in {">", "|-", "|+", ">-", ">+"}:
        raise BuildError(f"Line {start + 1}: only single-line instructions and 'instruction: |' are supported.")
    token = state.push("slide_instruction", "", 0)
    token.map = [start, stop]
    token.meta = {"instruction": value}
    state.line = stop
    return True


def markdown_parser():
    parser = MarkdownIt("commonmark", {"html": True}).disable("lheading")
    parser.enable("table").enable("strikethrough")
    parser.use(tasklists_plugin)
    parser.block.ruler.before("hr", "slide_boundary", boundary_rule, {"alt": ["paragraph", "reference", "blockquote", "list"]})
    parser.block.ruler.before("fence", "slide_instruction", instruction_rule, {"alt": ["paragraph"]})
    return parser


def admonitions(tokens, parser):
    """Transform matching blockquote token pairs without flattening nested Markdown."""
    result = copy.deepcopy(tokens)
    remove = set()
    for position, token in enumerate(result):
        if token.type != "blockquote_open" or position + 3 >= len(result):
            continue
        paragraph, inline, close = result[position + 1:position + 4]
        if paragraph.type != "paragraph_open" or inline.type != "inline" or close.type != "paragraph_close":
            continue
        match = re.match(r"^\[!(NOTE|INFO|TIP|IMPORTANT|WARNING|CAUTION)\](?:\n|$)", inline.content)
        if not match:
            continue
        kind = match[1].lower()
        token.type = "html_block"
        token.content = f'<aside class="admonition admonition-{kind}" role="note"><div class="admonition-title">{kind.title()}</div><div class="admonition-body">\n'
        depth = 1
        for ending in range(position + 1, len(result)):
            candidate = result[ending]
            if candidate.type == "blockquote_open":
                depth += 1
            if candidate.type == "blockquote_close":
                depth -= 1
                if depth == 0:
                    candidate.type = "html_block"
                    candidate.content = "</div></aside>\n"
                    break
        inline.content = inline.content[match.end():]
        inline.children = parser.parseInline(inline.content)[0].children
        if not inline.content:
            remove.update({position + 1, position + 2, position + 3})
    return [token for position, token in enumerate(result) if position not in remove]


def parse_slides(text):
    parser = markdown_parser()
    env = {}
    tokens = parser.parse(text, env)
    lines = text.splitlines(keepends=True)
    boundaries = [token.map[0] for token in tokens if token.type == "slide_boundary"]
    starts = [0] + [line + 1 for line in boundaries]
    stops = boundaries + [len(lines)]
    slides = []
    for start, stop in zip(starts, stops):
        raw = "".join(lines[start:stop])
        if not raw.strip():
            if start == 0 or stop == len(lines):
                continue
            raise BuildError(f"Empty slide near line {start + 1}.")
        # Closing tokens have no map. Select the complete token range instead.
        first = next((i for i, token in enumerate(tokens) if token.type != "slide_boundary" and token.map and start <= token.map[0] < stop), None)
        last = next((i for i in range(first or 0, len(tokens)) if tokens[i].type == "slide_boundary" and tokens[i].map[0] >= stop), len(tokens))
        local = tokens[first:last] if first is not None else []
        annotation = next((token for token in local if token.type == "slide_instruction"), None)
        instruction = annotation.meta["instruction"] if annotation else ""
        annotation_text = "".join(lines[annotation.map[0]:annotation.map[1]]) if annotation else ""
        markdown = "".join(lines[annotation.map[1]:stop]) if annotation else raw
        render_tokens = [token for token in local if token.type != "slide_instruction"]
        render_tokens = admonitions(render_tokens, parser)
        for token in render_tokens:
            if token.type in {"th_open", "td_open"}:
                alignment = re.fullmatch(r"text-align:(left|right|center)", token.attrGet("style") or "")
                if alignment:
                    token.attrSet("align", alignment[1])
                    token.attrs.pop("style", None)
        rendered = parser.renderer.render(render_tokens, parser.options, env)
        safe = bleach.clean(rendered, tags=SAFE_TAGS, attributes=SAFE_ATTRS, protocols={"http", "https", "mailto", "data"}, strip=True)
        soup = BeautifulSoup(safe, "html.parser")
        for element in soup.select('input:not([type="checkbox"])'):
            element.decompose()
        for element in soup.select('input[type="checkbox"]'):
            element["disabled"] = ""
            element["aria-label"] = element.parent.get_text(" ", strip=True) or "Task status"
        for element in soup.find_all("img"):
            if element.get("src", "").startswith("data:") and not re.match(r"^data:image/(?:png|jpeg|gif|webp|avif);base64,", element["src"], re.I):
                del element["src"]
        for element in soup.find_all("a"):
            if element.get("href", "").lower().startswith("data:"):
                del element["href"]
        for table in list(soup.find_all("table")):
            wrapper = soup.new_tag("div", attrs={"class": "table-scroll", "tabindex": "0", "role": "region", "aria-label": "Slide table"})
            table.wrap(wrapper)
            for header in table.find_all("th"):
                header["scope"] = "col"
        heading = soup.find(re.compile("^h[1-6]$"))
        slides.append({
            "raw": raw, "markdown": markdown, "annotation": annotation_text,
            "instruction": instruction, "source_hash": digest(raw),
            "title": heading.get_text(" ", strip=True) if heading else f"Slide {len(slides) + 1}",
            "markup": str(soup), "line": start + 1,
        })
    if not slides:
        raise BuildError("No nonempty slides found.")
    return slides


def local_path(url, base):
    parsed = urlsplit(url)
    if parsed.scheme == "file":
        path = unquote(parsed.path)
        if os.name == "nt" and re.match(r"^/[A-Za-z]:", path):
            path = path[1:]
        if parsed.netloc:
            path = "//" + parsed.netloc + path
        return Path(path).resolve()
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return (base / unquote(parsed.path)).resolve()


def asset_record(path):
    return {"path": str(path), "hash": digest(path.read_bytes()) if path.is_file() else None}


def rebase_markup(markup, source, output):
    soup = BeautifulSoup(markup, "html.parser")
    assets = []
    for element in soup.find_all(["img", "a"]):
        attribute = "src" if element.name == "img" else "href"
        url = element.get(attribute, "")
        path = local_path(url, source.parent)
        if path is None:
            continue
        parsed = urlsplit(url)
        try:
            relative = Path(os.path.relpath(path, output.parent)).as_posix()
            replacement = quote(relative, safe="/")
        except ValueError:  # Different Windows drives: a file URI is the usable reference.
            replacement = path.as_uri()
        element[attribute] = replacement + (f"?{parsed.query}" if parsed.query else "") + (f"#{parsed.fragment}" if parsed.fragment else "")
        if element.name == "img":
            assets.append(asset_record(path))
    return str(soup), assets


def heading_links(records):
    """Namespace heading IDs, then resolve unambiguous Markdown fragment links."""
    anchors = {}
    soups = {}
    for record in records:
        soup = BeautifulSoup(record["baseline"]["markup"], "html.parser")
        counts, local = {}, {}
        for heading in soup.find_all(re.compile("^h[1-6]$")):
            slug = re.sub(r"[^\w\s-]", "", heading.get_text().lower()).strip()
            slug = re.sub(r"\s+", "-", slug) or "heading"
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            unique = slug + (f"-{count}" if count else "")
            heading["id"] = record["id"] + "-" + unique
            local[unique] = heading["id"]
            anchors.setdefault(unique, []).append(heading["id"])
        soups[record["id"]] = (soup, local)
    for record in records:
        soup, local = soups[record["id"]]
        for link in soup.find_all("a", href=True):
            reference = link["href"]
            if not reference.startswith("#"):
                continue
            fragment = unquote(reference[1:])
            target = local.get(fragment)
            if not target and len(anchors.get(fragment, [])) == 1:
                target = anchors[fragment][0]
            if target:
                link["href"] = "#" + target
        record["baseline"]["markup"] = str(soup)
        # Captured regions are authoritative. Only update newly generated baseline bundles.
        if record.pop("fresh_bundle", False):
            record["bundle"]["markup"] = record["baseline"]["markup"]


def bundle_asset_paths(bundle, base):
    paths = set()
    fragment = BeautifulSoup(bundle["markup"], "html.parser")
    for element in fragment.find_all(True):
        urls = []
        if element.name in {"img", "video", "audio", "source"}:
            urls.append(element.get("src", ""))
        if element.name == "video":
            urls.append(element.get("poster", ""))
        if element.name == "image":
            urls.extend([element.get("href", ""), element.get("xlink:href", "")])
        for url in urls:
            path = local_path(url, base)
            if path:
                paths.add(path)
    def css_urls(tokens):
        for token in tokens:
            url = None
            if token.type == "url":
                url = token.value
            elif token.type == "function" and token.lower_name == "url":
                significant = [item for item in token.arguments if item.type not in {"whitespace", "comment"}]
                if len(significant) == 1 and significant[0].type == "string":
                    url = significant[0].value
            if url is not None:
                path = local_path(url, base)
                if path:
                    paths.add(path)
            for name in ("content", "arguments"):
                children = getattr(token, name, None)
                if children:
                    css_urls(children)
    css_urls(tinycss2.parse_component_value_list(bundle["css"]))
    return sorted(paths, key=str)


def theme_css(path):
    text = read_text(path)
    blocks = re.findall(r"<!-- slide-theme:start -->\s*```css\s*\n(.*?)\n```\s*<!-- slide-theme:end -->", text, re.S)
    if len(blocks) != 1:
        raise BuildError("DESIGN.md must contain exactly one marked slide-theme CSS block. See the theme replacement interface.")
    if "</style" in blocks[0].lower():
        raise BuildError("Theme CSS may not contain a closing HTML style tag.")
    return text, blocks[0]


def slot_markers(identifier, kind):
    prefix = f"slides:{identifier}:{kind}"
    if kind == "markup":
        return f"<!-- {prefix}:start -->", f"<!-- {prefix}:end -->"
    if kind == "css":
        return f"/* {prefix}:start */", f"/* {prefix}:end */"
    return f"// {prefix}:start\n", f"// {prefix}:end"


def extract_slots(document, identifiers):
    bundles = {}
    masked = document
    for identifier in identifiers:
        bundles[identifier] = {}
        for kind in ("markup", "css", "script"):
            start, end = slot_markers(identifier, kind)
            left, right = 0, len(masked)
            if kind in {"css", "script"}:
                tag = "style" if kind == "css" else "script"
                attribute = "data-slide-style" if kind == "css" else "data-slide-script"
                opening = f'<{tag} {attribute}="{identifier}">'
                if masked.count(opening) != 1:
                    raise BuildError(f"Missing or duplicated {kind} container for {identifier}.")
                left = masked.index(opening) + len(opening)
                right = masked.find(f"</{tag}>", left)
                if right < left:
                    raise BuildError(f"Unclosed {kind} container for {identifier}.")
            region = masked[left:right]
            if region.count(start) != 1 or region.count(end) != 1:
                raise BuildError(f"Missing or duplicated {kind} markers for {identifier}.")
            pattern = re.compile(re.escape(start) + r"(.*?)" + re.escape(end), re.S)
            match = pattern.search(region)
            if not match:
                raise BuildError(f"Invalid slot boundaries for {identifier}.")
            bundles[identifier][kind] = match[1]
            region = pattern.sub(lambda _: start + f"[editable:{kind}]" + end, region, count=1)
            masked = masked[:left] + region + masked[right:]
    return bundles, digest(masked)


def slot(identifier, kind, content):
    start, end = slot_markers(identifier, kind)
    return start + content + end


def render_document(records, theme, title):
    styles, sections, overview, scripts, sources = [], [], [], [], []
    for number, record in enumerate(records, 1):
        identifier = record["id"]
        bundle = record["bundle"]
        styles.append(f'<style data-slide-style="{identifier}">\n{slot(identifier, "css", bundle["css"])}\n</style>')
        sections.append(f'<section id="{identifier}" class="slide" data-slide-id="{identifier}" aria-label="{html.escape(record["title"], quote=True)}" aria-hidden="{str(number != 1).lower()}"{ " hidden inert" if number != 1 else ""}><div class="slide-content">{slot(identifier, "markup", bundle["markup"])}</div></section>')
        overview.append(f'<button type="button" data-go-slide="{identifier}">{number}. {html.escape(record["title"])}</button>')
        scripts.append(f'<script data-slide-script="{identifier}">\nSlideDeck.register("{identifier}", (slide, api) => {{\n{slot(identifier, "script", bundle["script"])}\n}});\n</script>')
        sources.append({key: record[key] for key in ("id", "title", "raw", "markdown", "annotation", "instruction")})
    # JSON in a raw-text HTML script must escape '<', including '</script>'.
    source_json = json.dumps(sources, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    values = {
        "VERSION": VERSION, "TITLE": html.escape(title), "STRUCTURE": read_text(ASSETS / "structure.css"),
        "THEME": theme, "SLIDE_STYLES": "\n".join(styles), "OVERVIEW": "\n".join(overview),
        "SLIDES": "\n".join(sections), "SOURCE": source_json, "RUNTIME": read_text(ASSETS / "runtime.js"),
        "SLIDE_SCRIPTS": "\n".join(scripts),
    }
    template = read_text(ASSETS / "presentation-template.html")
    return re.sub(r"@@([A-Z_]+)@@", lambda match: values[match[1]], template)


def css_errors(css, identifier):
    errors = []
    def check(rules):
        for rule in rules:
            if rule.type == "error":
                errors.append(f"{identifier}: CSS parse error: {rule.message}")
            elif rule.type == "qualified-rule":
                # Commas nested in :is()/functions are not top-level separators.
                selectors, group = [], []
                for token in rule.prelude:
                    if token.type == "literal" and token.value == ",":
                        selectors.append(tinycss2.serialize(group).strip())
                        group = []
                    else:
                        group.append(token)
                selectors.append(tinycss2.serialize(group).strip())
                for selector in selectors:
                    scoped = re.match(r"^#" + re.escape(identifier) + r"(?=$|[\s.:#\[>])", selector)
                    # A root compound selector may never escape via a sibling combinator.
                    # Tokenize to distinguish spaces inside :is()/attribute values.
                    root_tokens = tinycss2.parse_component_value_list(selector)
                    descendant = False
                    escaped = False
                    for index, token in enumerate(root_tokens[1:], 1):
                        if token.type == "whitespace":
                            following = next((item for item in root_tokens[index + 1:] if item.type != "whitespace"), None)
                            if following and not (following.type == "literal" and following.value in {"+", "~"}):
                                descendant = True
                        elif token.type == "literal" and token.value == ">":
                            descendant = True
                        elif token.type == "literal" and token.value in {"+", "~"} and not descendant:
                            escaped = True
                    if not scoped or escaped:
                        errors.append(f"{identifier}: CSS selector must start with #{identifier} and remain within that slide: {selector}")
                if not rule.content:
                    continue
                for declaration in tinycss2.parse_declaration_list(rule.content, skip_comments=True, skip_whitespace=True):
                    if declaration.type == "error":
                        errors.append(f"{identifier}: invalid CSS declaration: {declaration.message}")
            elif rule.type == "at-rule":
                if rule.lower_at_keyword in {"media", "supports", "container", "layer"} and rule.content is not None:
                    check(tinycss2.parse_rule_list(rule.content, skip_comments=True, skip_whitespace=True))
                else:
                    errors.append(f"{identifier}: unsupported global CSS @{rule.lower_at_keyword}; use scoped selectors without global resources/keyframes.")
    check(tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True))
    return errors


def validate_document(document, state):
    identifiers = [record["id"] for record in state["slides"]]
    bundles, protected = extract_slots(document, identifiers)
    errors, warnings = [], []
    if protected != state["protected_hash"]:
        errors.append("Protected HTML changed. Restore only the altered shell/source/markers; do not rebuild over uncaptured slide edits.")
    soup = BeautifulSoup(document, "html.parser")
    ids = [element["id"] for element in soup.find_all(id=True)]
    if len(ids) != len(set(ids)):
        errors.append("HTML contains duplicate element IDs.")
    if not PROTECTED_IDS.issubset(set(ids)):
        errors.append("Required presentation controls/source regions are missing.")
    if [element.get("id") for element in soup.select("#deck > .slide")] != identifiers:
        errors.append("Slide count, order, or identifiers changed.")
    expected_sources = [{key: record[key] for key in ("id", "title", "raw", "markdown", "annotation", "instruction")} for record in state["slides"]]
    try:
        if json.loads(soup.find(id="deck-source").get_text()) != expected_sources:
            errors.append("Original slide source records changed.")
    except (AttributeError, ValueError):
        errors.append("Original source JSON is missing or invalid.")
    base = Path(state["output"]).parent
    for record in state["slides"]:
        identifier = record["id"]
        bundle = bundles[identifier]
        start, end = slot_markers(identifier, "markup")
        start_comment = soup.find(string=lambda value: isinstance(value, Comment) and str(value) == start[4:-3])
        end_comment = soup.find(string=lambda value: isinstance(value, Comment) and str(value) == end[4:-3])
        if not start_comment or not end_comment or start_comment.parent is not end_comment.parent or "slide-content" not in start_comment.parent.get("class", []) or start_comment.parent.parent.get("id") != identifier:
            errors.append(f"{identifier}: markup escaped its slide-content container or unbalanced HTML changed slot containment.")
        errors.extend(css_errors(bundle["css"], identifier))
        if "</script" in bundle["script"].lower() or "</style" in bundle["css"].lower():
            errors.append(f"{identifier}: slot content closes its containing HTML element.")
        fragment = BeautifulSoup(bundle["markup"], "html.parser")
        if fragment.find(["script", "style", "iframe", "object", "embed", "link", "base", "meta"]):
            errors.append(f"{identifier}: executable/global HTML belongs outside markup; use the lifecycle script slot.")
        for element in fragment.find_all(True):
            for attribute, value in element.attrs.items():
                if attribute.lower().startswith("on"):
                    errors.append(f"{identifier}: event handlers must be registered in the lifecycle slot, not HTML attributes.")
                if attribute in {"href", "src", "action", "xlink:href"} and re.match(r"\s*(?:javascript|vbscript):", str(value), re.I):
                    errors.append(f"{identifier}: unsafe URL scheme in {attribute}.")
            reference = element.get("href", "")
            if reference.startswith("#") and reference[1:] not in ids:
                errors.append(f"{identifier}: broken internal link {reference}.")
        for image in fragment.find_all("img"):
            if not image.has_attr("alt"):
                warnings.append(f"{identifier}: image has no alt text.")
        for path in bundle_asset_paths(bundle, base):
            if not path.is_file():
                errors.append(f"{identifier}: missing local asset {path}.")
    return {"errors": errors, "warnings": warnings, "slides": len(identifiers)}, bundles


def parse_pairs(values, label):
    pairs = {}
    for value in values or []:
        if "=" not in value:
            raise BuildError(f"{label} requires KEY=VALUE: {value}")
        key, item = value.split("=", 1)
        if key in pairs:
            raise BuildError(f"Duplicate {label} key: {key}")
        pairs[key] = item
    return pairs


def selected_slides(selection, records):
    if selection == "all":
        return set(record["id"] for record in records)
    result = set()
    by_id = {record["id"]: record for record in records}
    for value in selection.split(","):
        value = value.strip()
        if value in by_id:
            result.add(value)
        elif re.fullmatch(r"\d+(?:-\d+)?", value):
            left, _, right = value.partition("-")
            first, last = int(left), int(right or left)
            if not 1 <= first <= last <= len(records):
                raise BuildError(f"Invalid slide range: {value}")
            result.update(record["id"] for record in records[first - 1:last])
        else:
            raise BuildError(f"Unknown slide selection: {value}")
    return result


def plan_build(args):
    source, output = Path(args.input).resolve(), Path(args.output).resolve()
    if source == output or source == state_path(output) or output.suffix.lower() != ".html":
        raise BuildError("Output must be a distinct .html path, not the Markdown input or state path.")
    text = read_text(source)
    parsed = parse_slides(text)
    design = Path(args.design).resolve() if args.design else ROOT / "DESIGN.md"
    design_text, theme = theme_css(design)
    title = args.title or source.stem
    compatibility = digest(VERSION + design_text + str(output.parent) + str(source.parent) + title + "".join(read_text(ASSETS / name) for name in ("presentation-template.html", "structure.css", "runtime.js")))
    old = load_state(output)
    conflicts, warnings = [], []
    if old and Path(old["input"]).resolve() != source:
        raise BuildError("State belongs to a different Markdown source. Use a new output path.")
    if output.exists():
        current_hash = digest(read_text(output))
        if not old and not args.replace_existing:
            conflicts.append({"type": "untracked-output", "message": "Output exists without state. Use another path, or explicitly approve --replace-existing (backs up first)."})
        elif old and current_hash != old["html_hash"] and not args.discard_edits:
            conflicts.append({"type": "uncaptured-edits", "message": "HTML has uncaptured edits. Run validate/capture first, or approve --discard-edits (backs up first)."})
    elif old:
        conflicts.append({"type": "missing-output", "message": "State exists without its HTML. Restore the deck, or use a new output path."})
    mappings = parse_pairs(args.map, "--map")
    resolutions = parse_pairs(args.resolve, "--resolve")
    old_records = old["slides"] if old else []
    by_id = {record["id"]: record for record in old_records}
    if any(not key.isdigit() or not 1 <= int(key) <= len(parsed) for key in mappings):
        raise BuildError("--map keys must be current slide numbers.")
    if any(identifier not in by_id for identifier in list(mappings.values()) + list(resolutions) + args.drop):
        raise BuildError("Mapping, resolution, or deletion refers to an unknown prior slide ID.")
    if len(set(mappings.values())) != len(mappings):
        raise BuildError("A prior slide cannot map to two current slides.")
    if any(value not in {"regenerate", "adapt"} for value in resolutions.values()):
        raise BuildError("--resolve values must be regenerate or adapt.")
    if set(args.drop) & set(mappings.values()):
        raise BuildError("Cannot map and drop the same prior slide.")
    used = set(args.drop) | set(mappings.values())
    matches = {int(number) - 1: by_id[identifier] for number, identifier in mappings.items()}
    exact_deck = old and old["source_file_hash"] == digest(text)
    if exact_deck:
        for position, prior in enumerate(old_records):
            if position not in matches and prior["id"] not in used:
                matches[position] = prior
                used.add(prior["id"])
    else:
        for position, slide in enumerate(parsed):
            if position in matches:
                continue
            current_peers = [i for i, item in enumerate(parsed) if i not in matches and item["source_hash"] == slide["source_hash"]]
            prior_peers = [item for item in old_records if item["id"] not in used and item["source_hash"] == slide["source_hash"]]
            if len(current_peers) == 1 and len(prior_peers) == 1:
                matches[position] = prior_peers[0]
                used.add(prior_peers[0]["id"])
    unmatched = [record for record in old_records if record["id"] not in used]
    for prior in unmatched:
        conflicts.append({"type": "unmatched-prior-slide", "id": prior["id"], "title": prior["title"], "message": "Explicitly map a current slide with --map NUMBER=ID, or approve deletion with --drop ID. Positional matching is forbidden."})
    records = []
    for position, slide in enumerate(parsed):
        prior = matches.get(position)
        identifier = prior["id"] if prior else "s-" + uuid.uuid4().hex[:12]
        markup, assets = rebase_markup(slide["markup"], source, output)
        custom_assets = [asset_record(Path(asset["path"])) for asset in prior.get("custom_assets", [])] if prior else []
        changed = bool(prior and (prior["source_hash"] != slide["source_hash"] or prior["assets"] != assets or prior.get("custom_assets", []) != custom_assets or old["compatibility"] != compatibility))
        if changed and identifier not in resolutions:
            conflicts.append({"type": "changed-slide", "slide": position + 1, "id": identifier, "title": slide["title"], "message": "Source, instruction, local assets, theme, or shell changed. Approve --resolve ID=regenerate or ID=adapt; old regions remain in history."})
        unchanged = prior and not changed
        permission = "instruction" if slide["instruction"].strip() else (prior["permission"] if unchanged else None)
        record = {key: slide[key] for key in ("raw", "markdown", "annotation", "instruction", "source_hash", "title", "line")}
        record.update({
            "id": identifier, "assets": assets,
            "custom_assets": prior.get("custom_assets", []) if unchanged else [],
            "permission": permission,
            "status": prior["status"] if unchanged else ("needs-agent" if permission else "needs-permission"),
            "baseline": {"markup": markup, "css": "", "script": "\n"},
            "bundle": copy.deepcopy(prior["bundle"]) if unchanged else {"markup": markup, "css": "", "script": "\n"},
            "fresh_bundle": not bool(unchanged),
        })
        if prior and changed:
            record["previous"] = copy.deepcopy(prior)
            record["resolution"] = resolutions.get(identifier)
        elif prior and "previous" in prior:
            record["previous"] = copy.deepcopy(prior["previous"])
            record["resolution"] = prior.get("resolution")
        records.append(record)
        for asset in assets:
            if asset["hash"] is None:
                warnings.append(f"Slide {position + 1}: missing local image {asset['path']}")
    heading_links(records)
    new_ids = {record["id"] for record in records}
    for identifier in resolutions:
        if identifier not in new_ids:
            raise BuildError(f"Resolution does not apply to a matched current slide: {identifier}")
    return {
        "input": str(source), "output": str(output), "title": title, "theme": theme,
        "design": str(design), "compatibility": compatibility, "source_file_hash": digest(text),
        "slides": records, "conflicts": conflicts, "warnings": warnings, "old": old,
    }


def build(args):
    plan = plan_build(args)
    summary = {
        "input": plan["input"], "output": plan["output"], "conflicts": plan["conflicts"], "warnings": plan["warnings"],
        "slides": [{"number": number, **{key: record[key] for key in ("id", "title", "instruction", "permission", "status")}} for number, record in enumerate(plan["slides"], 1)],
    }
    if args.dry_run or plan["conflicts"]:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2 if plan["conflicts"] else 0
    document = render_document(plan["slides"], plan["theme"], plan["title"])
    _, protected_hash = extract_slots(document, [record["id"] for record in plan["slides"]])
    old = plan["old"]
    history = copy.deepcopy(old.get("history", [])) if old else []
    if old:
        for record in old["slides"]:
            replacement = next((item for item in plan["slides"] if item["id"] == record["id"]), None)
            if replacement is None or replacement.get("previous") == record:
                history.append({"saved_at": utc_now(), "slide": copy.deepcopy(record)})
    state = {key: plan[key] for key in ("input", "output", "design", "title", "compatibility", "source_file_hash", "slides")}
    state.update({"version": STATE_VERSION, "builder": VERSION, "created_at": utc_now(), "html_hash": digest(document), "protected_hash": protected_hash, "history": history})
    validation, _ = validate_document(document, state)
    # Baseline missing images are surfaced as warnings; malformed restored edits still block a build.
    blocking = [error for error in validation["errors"] if ": missing local asset " not in error]
    if blocking:
        raise BuildError("Generated/restored deck failed validation: " + "\n".join(blocking))
    saved = backup(plan["output"])
    atomic_write(plan["output"], document)
    save_state(plan["output"], state)
    summary["backup"] = saved
    summary["state"] = str(state_path(plan["output"]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def require_deck(output):
    output = Path(output).resolve()
    state = load_state(output)
    if not state or not output.is_file():
        raise BuildError("This command requires an existing HTML deck and its state file.")
    return output, state, read_text(output)


def authorize(args):
    output, state, document = require_deck(args.output)
    if digest(document) != state["html_hash"]:
        raise BuildError("Capture existing HTML edits before changing recorded permissions.")
    selected = selected_slides(args.slides, state["slides"])
    for record in state["slides"]:
        if record["id"] not in selected:
            continue
        if record["instruction"].strip():
            continue  # Its annotation already supplies narrower permission.
        if args.mode == "preserve" and record["bundle"] != record["baseline"]:
            raise BuildError(f"{record['id']}: customized content already exists. Resolve its preservation separately.")
        record["permission"] = args.mode
        record["status"] = "complete" if args.mode == "preserve" else "needs-agent"
    save_state(output, state)
    print(json.dumps({"authorized": sorted(selected), "mode": args.mode}, indent=2))
    return 0


def custom_assets(bundle, base, source_assets):
    known = {asset["path"] for asset in source_assets}
    return [asset_record(path) for path in bundle_asset_paths(bundle, base) if str(path) not in known]


def capture(args):
    output, state, document = require_deck(args.output)
    result, bundles = validate_document(document, state)
    if result["errors"]:
        print(json.dumps(result, indent=2))
        return 2
    complete = selected_slides(args.complete, state["slides"]) if args.complete else set()
    for record in state["slides"]:
        identifier = record["id"]
        changed = bundles[identifier] != record["bundle"]
        if (changed or identifier in complete) and not record["permission"]:
            raise BuildError(f"{identifier}: customization requires recorded permission before capture.")
        if changed and record["permission"] == "preserve":
            raise BuildError(f"{identifier}: preserve mode forbids customized regions. Obtain and record another mode first.")
        if changed:
            state["history"].append({"saved_at": utc_now(), "slide": copy.deepcopy(record)})
            record["bundle"] = bundles[identifier]
            record["custom_assets"] = custom_assets(bundles[identifier], output.parent, record["assets"])
            record["status"] = "needs-agent"
        if identifier in complete:
            record["status"] = "complete"
    state["html_hash"] = digest(document)
    state["captured_at"] = utc_now()
    save_state(output, state)
    print(json.dumps({"captured": str(output), "complete": sorted(complete), "warnings": result["warnings"]}, indent=2))
    return 0


def validate(args):
    _, state, document = require_deck(args.output)
    result, _ = validate_document(document, state)
    result["uncaptured_edits"] = digest(document) != state["html_hash"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["errors"] else 0


def inspect(args):
    _, state, document = require_deck(args.output)
    result = {key: state[key] for key in ("input", "output", "design", "title", "builder")}
    result["uncaptured_edits"] = digest(document) != state["html_hash"]
    result["slides"] = []
    selected = selected_slides(args.slides, state["slides"]) if args.slides else {record["id"] for record in state["slides"]}
    for number, record in enumerate(state["slides"], 1):
        if record["id"] not in selected:
            continue
        item = {"number": number, **{key: record[key] for key in ("id", "title", "line", "annotation", "instruction", "markdown", "permission", "status")}}
        if args.history:
            item["bundle"] = record["bundle"]
            item["previous"] = record.get("previous")
        result["slides"].append(item)
    if args.history:
        result["history"] = state["history"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("build", help="Generate a baseline or restore compatible captured edits.")
    command.add_argument("input")
    command.add_argument("--output", required=True)
    command.add_argument("--title")
    command.add_argument("--design", help="Alternate DESIGN.md with the same theme interface.")
    command.add_argument("--dry-run", action="store_true")
    command.add_argument("--map", action="append", default=[], metavar="NUMBER=OLD_ID")
    command.add_argument("--drop", action="append", default=[], metavar="OLD_ID")
    command.add_argument("--resolve", action="append", default=[], metavar="OLD_ID=regenerate|adapt")
    command.add_argument("--replace-existing", action="store_true", help="Explicitly approve backing up/replacing HTML without state.")
    command.add_argument("--discard-edits", action="store_true", help="Explicitly approve backing up/replacing uncaptured HTML edits.")
    command.set_defaults(handler=build)
    command = sub.add_parser("authorize", help="Record the user's decision for unannotated slides.")
    command.add_argument("output")
    command.add_argument("--mode", required=True, choices=["preserve", "design", "rewrite"])
    command.add_argument("--slides", required=True, help="all, slide IDs, or comma-separated numbers/ranges")
    command.set_defaults(handler=authorize)
    command = sub.add_parser("capture", help="Save allowed HTML edits without regenerating the deck.")
    command.add_argument("output")
    command.add_argument("--complete", help="Reviewed slide IDs/numbers/ranges or all")
    command.set_defaults(handler=capture)
    command = sub.add_parser("validate", help="Check protected shell, slots, assets, and internal references.")
    command.add_argument("output")
    command.set_defaults(handler=validate)
    command = sub.add_parser("inspect", help="List source, permissions, work queue, and optional recovery regions.")
    command.add_argument("output")
    command.add_argument("--slides")
    command.add_argument("--history", action="store_true")
    command.set_defaults(handler=inspect)
    args = parser.parse_args()
    try:
        return args.handler(args)
    except (BuildError, OSError, UnicodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
