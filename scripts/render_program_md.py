#!/usr/bin/env python3
"""
Render a CBT program YAML into a Markdown chat-UX preview.
Usage: python3 render_program_md.py <program_yaml> <output_md>
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def md_escape(text: str) -> str:
    return (text or "").replace("\r\n", "\n").strip()


def list_md(items: list[str]) -> str:
    if not items:
        return ""
    return "\n".join(f"- {md_escape(item)}" for item in items)


def render_module(module: dict, index: int) -> str:
    title = module.get("title") or f"Module {index}"
    overview = list_md(module.get("overview") or [])
    takeaways = list_md(module.get("takeaways") or [])
    exercises = module.get("exercises") or []
    homework = module.get("homework") or []

    parts = [f"## {md_escape(title)}"]
    if overview:
        parts.append("**Summary**")
        parts.append(overview)
    if takeaways:
        parts.append("**Key Takeaways**")
        parts.append(takeaways)

    if exercises:
        parts.append("**Exercises**")
        for idx, ex in enumerate(exercises, start=1):
            parts.append(f"{idx}. {md_escape(ex)}")
            parts.append("\nYour response:\n```")
            parts.append("\n```")

    if homework:
        parts.append("**Homework**")
        for idx, hw in enumerate(homework, start=1):
            parts.append(f"{idx}. {md_escape(hw)}")
            parts.append("\nYour response:\n```")
            parts.append("\n```")

    parts.append("**Progress Check (soft gate)**")
    parts.append("- I attempted the exercises or homework.")
    parts.append("- I can summarize what I learned.")
    parts.append("- I have a plan for when I will practice next.")

    return "\n\n".join(parts)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 render_program_md.py <program_yaml> <output_md>")
        return 1

    program_path = Path(sys.argv[1]).expanduser().resolve()
    output_md = Path(sys.argv[2]).expanduser().resolve()

    data = yaml.safe_load(program_path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("id") or "CBT Program"

    header = [
        f"# {md_escape(title)}",
        f"**Condition:** {md_escape(data.get('condition') or '')}",
        f"**Duration:** {md_escape(data.get('duration') or '')}",
    ]

    focus = data.get("focusAreas") or []
    if focus:
        header.append("**Focus Areas**")
        header.append(list_md(focus))

    modules = data.get("modules") or []
    module_blocks = [render_module(mod, idx + 1) for idx, mod in enumerate(modules)]

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n\n".join(header + module_blocks), encoding="utf-8")

    print(f"Wrote Markdown to {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
