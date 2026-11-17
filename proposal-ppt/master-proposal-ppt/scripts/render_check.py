#!/usr/bin/env python3
"""把 pptx 渲染成逐页 PNG 和总览拼图, 用于目检排版。

用法: python3 render_check.py deck.pptx [输出目录] [--dpi 60] [--cols 4]
依赖: LibreOffice(soffice)、pdftoppm、Pillow。
注意: LibreOffice 不渲染 Office Math, 公式页显示的是 LaTeX 回退图; 中文字体会被替换, 行宽与 PowerPoint 略有差异。
"""
import argparse
import glob
import os
import shutil
import subprocess
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("out", nargs="?", default="render_out")
    ap.add_argument("--dpi", type=int, default=60)
    ap.add_argument("--cols", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    src = os.path.join(a.out, "deck.pptx")
    shutil.copy(a.pptx, src)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", a.out, src],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    pdf = os.path.join(a.out, "deck.pdf")
    for f in glob.glob(os.path.join(a.out, "p-*.png")):
        os.remove(f)
    subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", pdf, os.path.join(a.out, "p")], check=True)
    files = sorted(glob.glob(os.path.join(a.out, "p-*.png")))
    ims = [Image.open(f) for f in files]
    w, h = ims[0].size
    for start in range(0, len(ims), a.cols * 3):
        chunk = ims[start:start + a.cols * 3]
        rows = (len(chunk) + a.cols - 1) // a.cols
        g = Image.new("RGB", (a.cols * w, rows * h), "white")
        for i, im in enumerate(chunk):
            g.paste(im, ((i % a.cols) * w, (i // a.cols) * h))
        g.save(os.path.join(a.out, f"grid_{start // (a.cols * 3) + 1}.png"))
    print(f"{len(files)} 页, 输出目录 {a.out}")


if __name__ == "__main__":
    main()
