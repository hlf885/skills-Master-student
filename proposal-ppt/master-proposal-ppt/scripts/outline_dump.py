#!/usr/bin/env python3
"""批量导出往届开题答辩 PPT 的逐页提纲, 用来学习本校的页面结构和篇幅。

用法: python3 outline_dump.py 目录或文件... [--stats]
每页输出: 页码、版式名、图片数、页内文字(截断)。--stats 只输出统计:
总页数、各部分页数、每页平均字数、含图页比例。
只用于学习结构; 不要把往届同学的原文复制进新 PPT 或上传到公开仓库。
"""
import glob
import os
import re
import sys
from collections import Counter

from pptx import Presentation

PARTS = ["立题依据", "研究内容", "研究方案", "创新", "研究基础", "研究计划"]


def files_of(args):
    out = []
    for a in args:
        if os.path.isdir(a):
            out += sorted(glob.glob(os.path.join(a, "*.pptx")))
        elif a.endswith(".pptx"):
            out.append(a)
    return out


def main():
    stats = "--stats" in sys.argv
    for f in files_of([a for a in sys.argv[1:] if a != "--stats"]):
        prs = Presentation(f)
        part_pages, chars, with_pic = Counter(), [], 0
        cur = None
        if not stats:
            print(f"##### {os.path.basename(f)}  共{len(prs.slides)}页")
        for i, s in enumerate(prs.slides, 1):
            texts, pics = [], 0
            for sh in s.shapes:
                if sh.shape_type == 13:
                    pics += 1
                if sh.has_text_frame and sh.text_frame.text.strip():
                    texts.append(sh.text_frame.text.strip().replace("\n", " / "))
            joined = " || ".join(texts)
            for p in PARTS:
                if re.sub(r"\s", "", joined).find(p) >= 0 and "PART" in joined:
                    cur = p
            if cur:
                part_pages[cur] += 1
            chars.append(len(re.sub(r"\s", "", joined)))
            with_pic += pics > 0
            if not stats:
                print(f" [{i:02d}] {s.slide_layout.name} 图{pics} | {joined[:260]}")
        if stats:
            print(f"{os.path.basename(f)}: {len(prs.slides)}页, 分部页数 {dict(part_pages)}, "
                  f"平均每页{sum(chars) // max(1, len(chars))}字, 含图页 {with_pic}/{len(prs.slides)}")


if __name__ == "__main__":
    main()
