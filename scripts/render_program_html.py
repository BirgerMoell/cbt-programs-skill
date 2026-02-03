#!/usr/bin/env python3
"""
Render a CBT program YAML into HTML pages.
Usage: python3 render_program_html.py <program_yaml> <output_dir>
"""
from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

import yaml


def esc(text: str) -> str:
    return html.escape(text or "")


def slugify(text: str) -> str:
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in (" ", "-", "_"):
            keep.append("-")
    slug = "".join(keep)
    slug = "-".join([s for s in slug.split("-") if s])
    return slug or "module"


def write_html(path: Path, title: str, body: str) -> None:
    page = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{esc(title)}</title>
  <link rel=\"stylesheet\" href=\"style.css\" />
</head>
<body>
  <header>
    <div class=\"section-label\">CBT Program</div>
    <h1>{esc(title)}</h1>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
"""
    path.write_text(page, encoding="utf-8")


def list_items(items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{esc(item)}</li>" for item in items)
    return f"<ul class=\"list\">{lis}</ul>"


def render_module(module: dict, module_index: int, exercises: list[str]) -> str:
    overview = list_items(module.get("overview") or [])
    takeaways = list_items(module.get("takeaways") or [])

    narrative_blocks = []
    narrative = module.get("narrative") or []
    for idx, section in enumerate(narrative):
        title = esc(section.get("section") or f"Section {idx + 1}")
        paragraphs = section.get("paragraphs") or []
        para_html = "".join(f"<p>{esc(p)}</p>" for p in paragraphs)
        narrative_blocks.append(
            f"<div class=\"card\"><h3>{title}</h3>{para_html}</div>"
        )

        exercise_after = section.get("exerciseAfter")
        if isinstance(exercise_after, int) and 0 <= exercise_after < len(exercises):
            exercise_text = esc(exercises[exercise_after])
            narrative_blocks.append(
                "<div class=\"card\">"
                f"<div class=\"section-label\">Exercise {exercise_after + 1}</div>"
                f"<p>{exercise_text}</p>"
                "</div>"
            )

    exercise_list = list_items(exercises)
    homework_list = list_items(module.get("homework") or [])

    return """<div class=\"card\">
  <div class=\"section-label\">Overview</div>
  {overview}
</div>
<div class=\"card\">
  <div class=\"section-label\">Key Takeaways</div>
  {takeaways}
</div>
{narrative_blocks}
<div class=\"card\">
  <div class=\"section-label\">Exercises</div>
  {exercise_list}
</div>
<div class=\"card\">
  <div class=\"section-label\">Homework</div>
  {homework_list}
</div>
""".format(
        overview=overview or "<p>No overview provided.</p>",
        takeaways=takeaways or "<p>No takeaways provided.</p>",
        narrative_blocks="".join(narrative_blocks) or "<div class=\"card\"><p>No narrative sections.</p></div>",
        exercise_list=exercise_list or "<p>No exercises listed.</p>",
        homework_list=homework_list or "<p>No homework listed.</p>",
    )


def render_form_block(items: list[str], label: str, prefix: str) -> str:
    if not items:
        return ""
    fields = []
    for idx, item in enumerate(items, start=1):
        field_id = f"{prefix}-{idx}"
        fields.append(
            "<label for=\"{fid}\"><strong>{label} {idx}.</strong> {text}</label>"
            "<textarea id=\"{fid}\" name=\"{fid}\" placeholder=\"Write your response here...\"></textarea>".format(
                fid=field_id,
                label=esc(label),
                idx=idx,
                text=esc(item),
            )
        )
    return "<div class=\"form-block\">" + "".join(fields) + "</div>"


def render_module_form(module: dict) -> str:
    exercises = module.get("exercises") or []
    homework = module.get("homework") or []
    return """<div class=\"card\">
  <div class=\"section-label\">Exercise & Homework Journal</div>
  <p>Use this space to draft your responses. You can paste your answers back into chat for feedback.</p>
  {exercise_fields}
  {homework_fields}
</div>
<div class=\"card\">
  <div class=\"section-label\">Progress Check</div>
  <ul class=\"list\">
    <li>I attempted the exercises and homework.</li>
    <li>I can summarize what I learned in 2-3 sentences.</li>
    <li>I have a plan for when I will practice next.</li>
  </ul>
  <p class=\"note\">You do not have to be perfect to move on. The goal is honest effort and reflection.</p>
</div>
""".format(
        exercise_fields=render_form_block(exercises, "Exercise", "exercise")
        or "<p>No exercises listed for this module.</p>",
        homework_fields=render_form_block(homework, "Homework", "homework")
        or "<p>No homework listed for this module.</p>",
    )


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 render_program_html.py <program_yaml> <output_dir>")
        return 1

    program_path = Path(sys.argv[1]).expanduser().resolve()
    output_dir = Path(sys.argv[2]).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    data = yaml.safe_load(program_path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("id") or "CBT Program"

    style_src = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if style_src.exists():
        shutil.copy(style_src, output_dir / "style.css")

    program_summary = "".join(
        f"<span class=\"tag\">{esc(tag)}</span>" for tag in (data.get("focusAreas") or [])
    )

    module_links = []
    module_cards = []
    modules = data.get("modules") or []

    for idx, module in enumerate(modules, start=1):
        module_title = module.get("title") or f"Module {idx}"
        slug = slugify(module_title)
        module_filename = f"{idx:02d}-{slug}.html"
        module_links.append(
            f"<li><a href=\"{module_filename}\">{esc(module_title)}</a></li>"
        )
        module_cards.append(
            "<div class=\"module-card\">"
            f"<div class=\"section-label\">Module {idx}</div>"
            f"<a href=\"{module_filename}\">{esc(module_title)}</a>"
            "</div>"
        )

        exercises = module.get("exercises") or []
        module_body = render_module(module, idx, exercises) + render_module_form(module)
        write_html(output_dir / module_filename, module_title, module_body)

    program_body = f"""
<div class=\"card\">
  <div class=\"section-label\">Summary</div>
  <p>{esc(data.get("summary") or "")}</p>
  <p><strong>Condition:</strong> {esc(data.get("condition") or "")}</p>
  <p><strong>Duration:</strong> {esc(data.get("duration") or "")}</p>
  <div>{program_summary}</div>
</div>
<div class=\"card\">
  <div class=\"section-label\">Modules</div>
  <div class=\"module-grid\">{''.join(module_cards)}</div>
</div>
<div class=\"card\">
  <div class=\"section-label\">Module Links</div>
  <ul class=\"list\">{''.join(module_links)}</ul>
</div>
<div class=\"footer\">Generated from {esc(program_path.name)}</div>
"""
    write_html(output_dir / "index.html", title, program_body)

    print(f"Wrote HTML to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
