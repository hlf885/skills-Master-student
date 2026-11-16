#!/usr/bin/env python3
"""按画图规格文件生成开题自绘图（1.7.0 新增）。

用法:
    python draw_figure.py spec.json -o 输出目录 [--formats svg,png,vba] [--style R8]
    python draw_figure.py spec.json -o 输出目录 --all-styles      # 同一份内容按该类图的全部画法各出一张，供用户挑选

spec.json:
    {"type": "research_content", "style": "R8", "name": "fig2-1", "content": {...}}
type 可取 research_content（研究内容图，R1–R9）、technical_route（技术路线图，T1–T5）、
architecture（架构与框架图，A1–A6）、flowchart（算法流程图，F1–F6），见 references/12-figure-styles.md。
content 中的相对路径（如场景图）相对 spec.json 所在目录。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from figstyles import architecture, flowchart, research_content, technical_route  # noqa: E402

REGISTRY = {"research_content": research_content.STYLES, "technical_route": technical_route.STYLES,
            "architecture": architecture.STYLES, "flowchart": flowchart.STYLES}


def resolve(content: dict, base: Path) -> dict:
    c = dict(content)
    if c.get("scene"):
        p = Path(c["scene"])
        c["scene"] = str(p if p.is_absolute() else (base / p).resolve())
    return c


def draw(kind: str, style: str, content: dict, out: Path, name: str, formats: list[str]) -> list[Path]:
    styles = REGISTRY[kind]
    if style not in styles:
        raise SystemExit(f"未知画法 {style}，可选：{', '.join(styles)}")
    label, fn = styles[style]
    if style in ("R7", "R8") and not content.get("scene"):
        raise SystemExit(f"{style}（{label}）需要场景图：在 content.scene 中给出图片路径")
    fig = fn(content)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{name}_{style}"
    done = []
    if "svg" in formats:
        p = out / f"{stem}.svg"
        p.write_text(fig.to_svg(), encoding="utf-8")
        done.append(p)
    if "png" in formats:
        p = out / f"{stem}.png"
        fig.to_png(p)
        done.append(p)
    if "vba" in formats:
        p = out / f"{stem}.bas"
        p.write_text(fig.to_vba(title=f"{name} {style}"), encoding="utf-8")
        done.append(p)
        if content.get("scene"):
            import shutil
            shutil.copy(content["scene"], out / Path(content["scene"]).name)
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path("figures"))
    ap.add_argument("--formats", default="svg,png", help="svg、png、vba 任选，逗号分隔；由用户决定要哪几种")
    ap.add_argument("--style", help="覆盖 spec 中的画法")
    ap.add_argument("--all-styles", action="store_true", help="按该类图的全部画法各出一张（有场景图时才画 R7、R8）")
    args = ap.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    kind = spec.get("type", "research_content")
    content = resolve(spec["content"], args.spec.parent)
    formats = [x.strip() for x in args.formats.split(",") if x.strip()]
    name = spec.get("name", "figure")
    styles = list(REGISTRY[kind]) if args.all_styles else [args.style or spec.get("style", "R8")]
    for st in styles:
        if st in ("R7", "R8") and not content.get("scene"):
            print(f"跳过 {st}：没有场景图")
            continue
        for p in draw(kind, st, content, args.out, name, formats):
            print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
