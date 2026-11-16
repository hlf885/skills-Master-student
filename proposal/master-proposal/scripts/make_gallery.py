#!/usr/bin/env python3
"""重新生成 assets/figure-gallery/ 下各类图的示例图和总览图（画法有改动后运行）。

用法:
    python make_gallery.py            # 全部四类
    python make_gallery.py flowchart  # 只生成某一类
需要 Playwright + Chromium（渲染 PNG）与 Pillow（拼总览图）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from draw_figure import REGISTRY, resolve  # noqa: E402

GALLERY = HERE.parent / "assets" / "figure-gallery"
DIRS = {"research_content": "research-content", "technical_route": "technical-route",
        "architecture": "architecture", "flowchart": "flowchart"}


def overview(kind: str, folder: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    styles = REGISTRY[kind]
    font = None
    for cand in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "C:/Windows/Fonts/msyhbd.ttc",
                 "C:/Windows/Fonts/simhei.ttf"):
        if Path(cand).exists():
            font = ImageFont.truetype(cand, 34)
            break
    font = font or ImageFont.load_default()
    tw, th = 620, 440
    n = len(styles)
    cols = 3
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 20) + 20, rows * (th + 60) + 20), "white")
    d = ImageDraw.Draw(sheet)
    for k, (sid, (name, _)) in enumerate(styles.items()):
        p = folder / f"example_{sid}.png"
        if not p.exists():
            continue
        im = Image.open(p).convert("RGB")
        im.thumbnail((tw, th))
        x = 20 + (k % cols) * (tw + 20)
        y = 20 + (k // cols) * (th + 60)
        d.text((x, y), f"{sid} {name}", fill="#1F3864", font=font)
        sheet.paste(im, (x, y + 48))
        d.rectangle([x - 2, y + 46, x + im.width + 2, y + 48 + im.height + 2], outline="#BFBFBF", width=2)
    sheet.save(folder / "gallery-overview.png")


def main() -> int:
    kinds = sys.argv[1:] or list(DIRS)
    for kind in kinds:
        folder = GALLERY / DIRS[kind]
        spec = json.loads((folder / "content-example.json").read_text(encoding="utf-8"))
        content = resolve(spec["content"], folder)
        for sid, (name, fn) in REGISTRY[kind].items():
            if sid in ("R7", "R8") and not content.get("scene"):
                continue
            fn(content).to_png(folder / f"example_{sid}.png")
            print("wrote", folder / f"example_{sid}.png")
        overview(kind, folder)
        print("wrote", folder / "gallery-overview.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
