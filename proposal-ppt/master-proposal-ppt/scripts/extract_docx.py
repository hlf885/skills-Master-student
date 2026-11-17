#!/usr/bin/env python3
"""从开题报告 docx 中按文档顺序提取文字、表格和图片, 供制作答辩 PPT 使用。

用法: python3 extract_docx.py 开题报告.docx 输出目录
输出:
  输出目录/text.txt   段落与表格(表格行用 | 分隔), [IMG n] 标出图片位置, [MATH] 标出含公式段落
  输出目录/img/       图片按文档出现顺序命名为 01.png、02.jpg ……
  输出目录/math.txt   每个公式的 LaTeX 近似(由 pandoc 转换, 需安装 pandoc; 没有则跳过)
开题报告常把全文写在一个大表格里, 本脚本会进入单元格逐段输出。
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    (out / "img").mkdir(parents=True, exist_ok=True)
    doc = Document(str(src))
    rels = doc.part.rels
    lines, n_img = [], 0

    def para_text(p):
        nonlocal n_img
        t = "".join(x.text or "" for x in p.iter(qn("w:t")))
        tags = []
        for b in p.iter(qn("a:blip")):
            rid = b.get(qn("r:embed"))
            if rid in rels:
                n_img += 1
                part = rels[rid].target_part
                ext = Path(part.partname).suffix
                (out / "img" / f"{n_img:02d}{ext}").write_bytes(part.blob)
                tags.append(f"[IMG {n_img:02d}]")
        if any(True for _ in p.iter(qn("m:oMath"))):
            tags.append("[MATH]")
        return " ".join(tags + [t]).strip()

    def walk(el, depth=0):
        for c in el.iterchildren():
            if c.tag == qn("w:p"):
                t = para_text(c)
                if t:
                    lines.append(t)
            elif c.tag == qn("w:tbl"):
                for tr in c.iterchildren(qn("w:tr")):
                    cells = []
                    for tc in tr.iterchildren(qn("w:tc")):
                        inner = []
                        for p in tc.iterchildren():
                            if p.tag == qn("w:p"):
                                t = para_text(p)
                                if t:
                                    inner.append(t)
                            elif p.tag == qn("w:tbl"):
                                sub = []
                                walk_tbl(p, sub)
                                inner.extend(sub)
                        cells.append("\n".join(inner))
                    if len(cells) == 1 or sum(len(x) for x in cells) > 400:
                        lines.extend(x for x in cells if x)
                    else:
                        lines.append(" | ".join(x.replace("\n", " ") for x in cells))

    def walk_tbl(tbl, sink):
        for tr in tbl.iterchildren(qn("w:tr")):
            row = []
            for tc in tr.iterchildren(qn("w:tc")):
                row.append(" ".join(para_text(p) for p in tc.iterchildren(qn("w:p"))).strip())
            sink.append(" | ".join(row))

    walk(doc.element.body)
    (out / "text.txt").write_text("\n".join(lines), encoding="utf-8")

    if shutil.which("pandoc"):
        r = subprocess.run(["pandoc", str(src), "-t", "plain", "--wrap=none"], capture_output=True, text=True)
        eqs = re.findall(r"(\\[a-zA-Z]+\{.*?\}.*?#\\left\(\s*\\text\{[\d\-]+\}\s*\\right\))", r.stdout)
        (out / "math.txt").write_text("\n\n".join(e.strip(" |") for e in eqs), encoding="utf-8")
    print(f"文字 {len(lines)} 段, 图片 {n_img} 张 -> {out}")


if __name__ == "__main__":
    main()
