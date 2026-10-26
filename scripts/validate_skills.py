#!/usr/bin/env python3
"""Validate the skills collection (used locally and in CI).

Checks:
  * every <project>/<skill>/SKILL.md has YAML front matter with name == folder name,
    a non-empty description (<= 1024 chars) and metadata.version;
  * README.md, README_EN.md and CHANGELOG.md exist in each skill; CHANGELOG mentions the version;
  * the three project folders each have a README.md;
  * relative links in all Markdown files resolve;
  * Python scripts compile; smoke tests run on tests/*.md when check_proposal.py exists.
Exit code 0 = OK, 1 = problems found.
"""
from __future__ import annotations

import py_compile
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ["proposal", "mid-term", "thesis"]
problems: list[str] = []


def front_matter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not m:
        return {}
    fm: dict = {}
    block = m.group(1)
    name = re.search(r"^name:\s*(\S+)\s*$", block, flags=re.M)
    if name:
        fm["name"] = name.group(1)
    desc = re.search(r"^description:[ \t]*(>-?|\|-?)?[ \t]*\n?((?:[ \t]+.*\n?)*|.*)", block, flags=re.M)
    if desc:
        fm["description"] = " ".join(x.strip() for x in desc.group(2).splitlines()).strip()
    ver = re.search(r"^\s+version:\s*\"?([\w.\-]+)\"?\s*$", block, flags=re.M)
    if ver:
        fm["version"] = ver.group(1)
    return fm


def check_links(md: Path) -> None:
    text = md.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        path = (md.parent / target.split("#")[0]).resolve()
        if not path.exists():
            problems.append(f"{md.relative_to(ROOT)}: broken link -> {target}")


def main() -> int:
    for proj in PROJECTS:
        if not (ROOT / proj / "README.md").exists():
            problems.append(f"{proj}/README.md missing")
    skills = sorted(ROOT.glob("*/*/SKILL.md"))
    for sk in skills:
        folder = sk.parent
        rel = folder.relative_to(ROOT)
        if folder.parent.name not in PROJECTS:
            problems.append(f"{rel}: skill must live under one of {PROJECTS}")
        fm = front_matter(sk.read_text(encoding="utf-8"))
        if fm.get("name") != folder.name:
            problems.append(f"{rel}: name '{fm.get('name')}' != folder '{folder.name}'")
        if not fm.get("description"):
            problems.append(f"{rel}: description missing")
        elif len(fm["description"]) > 1024:
            problems.append(f"{rel}: description longer than 1024 characters ({len(fm['description'])})")
        if not fm.get("version"):
            problems.append(f"{rel}: metadata.version missing")
        for req in ("README.md", "README_EN.md", "CHANGELOG.md"):
            if not (folder / req).exists():
                problems.append(f"{rel}: {req} missing")
        cl = folder / "CHANGELOG.md"
        if cl.exists() and fm.get("version") and f"[{fm['version']}]" not in cl.read_text(encoding="utf-8"):
            problems.append(f"{rel}: CHANGELOG.md has no entry for version {fm['version']}")
        for py in folder.glob("scripts/*.py"):
            try:
                py_compile.compile(str(py), doraise=True)
            except py_compile.PyCompileError as e:
                problems.append(f"{py.relative_to(ROOT)}: {e.msg}")
        checker = folder / "scripts" / "check_proposal.py"
        for sample in folder.glob("tests/*.md"):
            if checker.exists():
                r = subprocess.run([sys.executable, str(checker), str(sample)], capture_output=True, text=True)
                if r.returncode not in (0, 1) or "Traceback" in r.stderr:
                    problems.append(f"{sample.relative_to(ROOT)}: check_proposal.py crashed\n{r.stderr[-800:]}")
        visio = folder / "scripts" / "visio_macro.py"
        spec = folder / "assets" / "figure-spec-example.json"
        if visio.exists() and spec.exists():
            out = Path(__import__("tempfile").gettempdir()) / "validate_fig.bas"
            r = subprocess.run([sys.executable, str(visio), str(spec), "-o", str(out)], capture_output=True, text=True)
            if r.returncode != 0:
                problems.append(f"{visio.relative_to(ROOT)}: failed on example spec\n{r.stderr[-800:]}")
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts:
            continue
        check_links(md)

    print(f"skills found: {len(skills)}")
    for s in skills:
        print(f"  - {s.parent.relative_to(ROOT)}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  * {p}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
