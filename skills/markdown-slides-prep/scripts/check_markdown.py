#!/usr/bin/env python3
"""Check slide Markdown through the installed renderer without creating HTML or state."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

DEFAULT_BUILDER = Path(__file__).resolve().parents[2] / "markdown-slides" / "scripts" / "slide_builder.py"


def load_builder(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError(f"Renderer parser not found: {path}. Install markdown-slides alongside this skill, or pass --builder for a trusted installation.")
    spec = importlib.util.spec_from_file_location("markdown_slides_prep_backend", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot import renderer parser: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, SystemExit) as error:
        raise ValueError(f"Renderer dependencies unavailable: {error}. Use a Python environment with markdown-slides/scripts/requirements.txt installed.") from error
    if not all(hasattr(module, name) for name in ("parse_slides", "read_text", "local_path", "BeautifulSoup")):
        raise ValueError("This renderer does not expose the expected read-only parser interface. Check its current format contract.")
    return module


def check_markdown(source, builder_path=DEFAULT_BUILDER):
    source = Path(source).resolve()
    try:
        builder = load_builder(builder_path)
        parsed = builder.parse_slides(builder.read_text(source))
    except (ValueError, OSError, UnicodeError) as error:
        return {"valid": False, "input": str(source), "error": str(error)}
    except Exception as error:
        # Includes the renderer's BuildError without assuming its implementation class.
        if "builder" in locals() and isinstance(error, getattr(builder, "BuildError", ())):
            return {"valid": False, "input": str(source), "error": str(error)}
        raise
    slides, warnings = [], []
    for number, slide in enumerate(parsed, 1):
        slides.append({
            "number": number, "line": slide["line"], "title": slide["title"],
            "instruction": slide["instruction"],
            "has_markdown_body": bool(slide["markdown"].strip()),
        })
        if not slide["markdown"].strip():
            warnings.append(f"Slide {number}: no Markdown body; review whether generation is intentionally deferred.")
        soup = builder.BeautifulSoup(slide["markup"], "html.parser")
        for image in soup.find_all("img"):
            url = image.get("src", "")
            if not url:
                warnings.append(f"Slide {number}: image has no supported source URL.")
                continue
            path = builder.local_path(url, source.parent)
            if path is not None and not path.is_file():
                warnings.append(f"Slide {number}: missing local image {path}.")
    return {
        "valid": True, "input": str(source), "slide_count": len(slides),
        "slides": slides, "warnings": warnings,
        "checks": "Parser syntax and local image existence only. Content accuracy, visual fit, and user approval are not checked.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Markdown source to inspect without modifying it")
    parser.add_argument("--builder", type=Path, default=DEFAULT_BUILDER, help="Trusted slide_builder.py installation")
    args = parser.parse_args()
    result = check_markdown(args.input, args.builder)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
