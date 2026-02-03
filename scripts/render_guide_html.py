#!/usr/bin/env python3
"""
Render a CBT guide YAML into HTML page.
Usage: python3 render_guide_html.py <guide_yaml> <output_dir>
"""
from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

import yaml


def esc(text: str) -> str:
    return html.escape(text or "")


def normalize_item(item) -> str:
    if isinstance(item, dict):
        if len(item) == 1:
            key, value = next(iter(item.items()))
            return f"{key}: {value}"
        return "; ".join(f"{k}: {v}" for k, v in item.items())
    return str(item)


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
    <div class=\"section-label\">CBT Guide</div>
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
    lis = "".join(f"<li>{esc(normalize_item(item))}</li>" for item in items)
    return f"<ul class=\"list\">{lis}</ul>"

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


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 render_guide_html.py <guide_yaml> <output_dir>")
        return 1

    guide_path = Path(sys.argv[1]).expanduser().resolve()
    output_dir = Path(sys.argv[2]).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    data = yaml.safe_load(guide_path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("id") or "CBT Guide"

    style_src = Path(__file__).resolve().parent.parent / "assets" / "style.css"
    if style_src.exists():
        shutil.copy(style_src, output_dir / "style.css")

    tags = data.get("tags") or []
    keywords = data.get("keywords") or []
    tag_html = "".join(f"<span class=\"tag\">{esc(tag)}</span>" for tag in tags)
    keyword_html = "".join(f"<span class=\"tag\">{esc(word)}</span>" for word in keywords)

    sections_html = []
    for section in data.get("sections") or []:
        body = "".join(
            f"<p>{esc(normalize_item(p))}</p>" for p in (section.get("body") or [])
        )
        tips_list = section.get("tips") or []
        highlights_list = section.get("highlights") or []
        tips = list_items(tips_list)
        highlights = list_items(highlights_list)
        practice_prompts = tips_list + highlights_list
        practice_fields = render_form_block(practice_prompts, "Practice", "practice")
        sections_html.append(
            "<div class=\"card\">"
            f"<h3>{esc(section.get('title') or 'Section')}</h3>"
            f"{body}"
            f"{tips}"
            f"{highlights}"
            f"{practice_fields}"
            "</div>"
        )

    resources_html = []
    for res in data.get("resources") or []:
        label = esc(res.get("title") or "Resource")
        url = esc(res.get("url") or "")
        if url:
            resources_html.append(f"<li><a href=\"{url}\" target=\"_blank\" rel=\"noopener\">{label}</a></li>")
        else:
            resources_html.append(f"<li>{label}</li>")

    body = f"""
<div class=\"card\">
  <div class=\"section-label\">Summary</div>
  <p>{esc(data.get("summary") or "")}</p>
  <div>{tag_html}</div>
  <div>{keyword_html}</div>
</div>
{''.join(sections_html)}
<div class=\"card\">
  <div class=\"section-label\">Progress Check</div>
  <ul class=\"list\">
    <li>I attempted at least one practice prompt.</li>
    <li>I can summarize what felt most useful.</li>
    <li>I chose one small next step to try.</li>
  </ul>
  <p class=\"note\">You do not have to be perfect to move on. The goal is honest effort and reflection.</p>
</div>
<div class=\"card\">
  <div class=\"section-label\">Resources</div>
  <ul class=\"list\">{''.join(resources_html) or '<li>No resources listed.</li>'}</ul>
</div>
<div class=\"footer\">Generated from {esc(guide_path.name)}</div>
"""

    write_html(output_dir / "index.html", title, body)
    print(f"Wrote HTML to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
