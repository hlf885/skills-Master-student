#!/usr/bin/env python3
"""Package a skill folder into a zip for claude.ai / Claude Cowork upload.

Usage:
    python scripts/package_skill.py proposal/master-proposal [-o dist/]

The zip contains <skill-name>/SKILL.md at its root level, as the upload page expects.
Caches and OS junk files are excluded. The version from SKILL.md is added to the
file name, e.g. dist/master-proposal-v1.0.0.zip.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skill_dir", type=Path)
    ap.add_argument("-o", "--outdir", type=Path, default=Path("dist"))
    args = ap.parse_args()

    skill = args.skill_dir.resolve()
    md = skill / "SKILL.md"
    if not md.exists():
        sys.exit(f"SKILL.md not found in {skill}")
    text = md.read_text(encoding="utf-8")
    name = re.search(r"^name:\s*(\S+)", text, flags=re.M)
    ver = re.search(r"^\s+version:\s*\"?([\w.\-]+)\"?", text, flags=re.M)
    if not name or name.group(1) != skill.name:
        sys.exit("name in SKILL.md must match the folder name")
    version = ver.group(1) if ver else "0.0.0"

    args.outdir.mkdir(parents=True, exist_ok=True)
    out = args.outdir / f"{skill.name}-v{version}.zip"
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(skill.rglob("*")):
            if p.is_dir() or p.name in EXCLUDE_FILES or EXCLUDE_DIRS & set(p.relative_to(skill).parts):
                continue
            zf.write(p, Path(skill.name) / p.relative_to(skill))
            count += 1
    print(f"wrote {out} ({count} files, version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
