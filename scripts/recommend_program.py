#!/usr/bin/env python3
"""
Recommend CBT programs based on a free-text query.
Usage: python3 recommend_program.py "<query>" [--limit 5]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return {w for w in words if len(w) > 2}


def score_program(query_tokens: set[str], program: dict) -> int:
    fields = []
    for key in ("title", "condition", "summary"):
        value = program.get(key)
        if value:
            fields.append(str(value))
    focus = program.get("focusAreas") or []
    fields.extend(str(item) for item in focus)

    haystack = " ".join(fields).lower()
    score = 0
    for token in query_tokens:
        if token in haystack:
            score += 2
    # boost for exact phrase match in title/condition
    title = (program.get("title") or "").lower()
    condition = (program.get("condition") or "").lower()
    for token in query_tokens:
        if token in title or token in condition:
            score += 2
    return score


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="User query describing their issue")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    programs_dir = root / "references" / "cbt-programs"

    query_tokens = tokenize(args.query)
    if not query_tokens:
        print("No usable keywords in query. Please provide a more specific description.")
        return 1

    results = []
    for path in programs_dir.glob("*.yaml"):
        program = yaml.safe_load(path.read_text(encoding="utf-8"))
        pid = program.get("id") or path.stem
        score = score_program(query_tokens, program)
        if score > 0:
            results.append((score, program.get("title") or pid, pid, program.get("summary") or ""))

    results.sort(reverse=True)
    print("Top program matches:\n")
    for score, title, pid, summary in results[: args.limit]:
        print(f"- {title} ({pid})")
        if summary:
            print(f"  {summary}")
    if not results:
        print("No direct matches found. Consider browsing the full program list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
