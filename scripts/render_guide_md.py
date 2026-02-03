#!/usr/bin/env python3
"""
Render a CBT guide YAML into a Markdown chat-UX preview.
Usage: python3 render_guide_md.py <guide_yaml> <output_md>
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def md_escape(text: str) -> str:
    return (text or "").replace("\r\n", "\n").strip()


def normalize_item(item) -> str:
    if isinstance(item, dict):
        if len(item) == 1:
            key, value = next(iter(item.items()))
            return f"{key}: {value}"
        return "; ".join(f"{k}: {v}" for k, v in item.items())
    return str(item)


def list_md(items: list[str]) -> str:
    if not items:
        return ""
    return "\n".join(f"- {md_escape(normalize_item(item))}" for item in items)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 render_guide_md.py <guide_yaml> <output_md>")
        return 1

    guide_path = Path(sys.argv[1]).expanduser().resolve()
    output_md = Path(sys.argv[2]).expanduser().resolve()

    data = yaml.safe_load(guide_path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("id") or "CBT Guide"

    lines = [f"# {md_escape(title)}", f"**Summary:** {md_escape(data.get('summary') or '')}"]

    tags = data.get("tags") or []
    if tags:
        lines.append("**Tags**")
        lines.append(list_md(tags))

    keywords = data.get("keywords") or []
    if keywords:
        lines.append("**Keywords**")
        lines.append(list_md(keywords))

    sections = data.get("sections") or []
    for section in sections:
        lines.append(f"## {md_escape(section.get('title') or 'Section')}")
        for paragraph in section.get("body") or []:
            lines.append(md_escape(normalize_item(paragraph)))

        prompts = (section.get("tips") or []) + (section.get("highlights") or [])
        if prompts:
            lines.append("**Practice Prompts**")
            for idx, prompt in enumerate(prompts, start=1):
                lines.append(f"{idx}. {md_escape(normalize_item(prompt))}")
                lines.append("\nYour response:\n```")
                lines.append("\n```")

    lines.append("**Progress Check (soft gate)**")
    lines.append("- I attempted at least one practice prompt.")
    lines.append("- I can summarize what felt most useful.")
    lines.append("- I chose one small next step to try.")

    resources = data.get("resources") or []
    if resources:
        lines.append("**Resources**")
        for res in resources:
            label = md_escape(res.get("title") or "Resource")
            url = md_escape(res.get("url") or "")
            if url:
                lines.append(f"- {label}: {url}")
            else:
                lines.append(f"- {label}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n\n".join(lines), encoding="utf-8")

    print(f"Wrote Markdown to {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
