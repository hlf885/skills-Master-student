#!/usr/bin/env python3
"""从一份师兄师姐的开题答辩 PPT 中抽出干净的学校模板。

用法:
    python3 make_template.py <源PPT.pptx> <输出模板.pptx> [--school 西南科技大学]

源 PPT 需要是本校常用的开题答辩版式(封面 / 目录 / PART 过渡页 / 内容页 / 结束页)。
脚本按版式名称自动找出这五类骨架页,只保留它们,并清除其中属于原作者的内容:
- 封面: 题目改成 论文题目,学校占位改成 --school 给定的名称,表格右列清空
- 目录、PART 页: 保留原样(文字由 swust_kit 在生成时改写)
- 内容页: 只保留四个页眉元素(部分编号、部分名称、页小标题、页码),其余全部删除
- 结束页: 学校占位改名,日期清空

不同学校的模板版式名称可能不同,可用 --map 手工指定页码,例如 --map cover=1,toc=2,part=3,content=4,end=22
"""
from __future__ import annotations

import argparse
import re
import sys
from pptx import Presentation

KEEP_CONTENT_NAMES = ("文本框 2", "灯片编号占位符 1", "矩形 11", "文本框 10")


def find_roles(prs):
    roles = {}
    for i, s in enumerate(prs.slides):
        lname = s.slide_layout.name
        text = " ".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
        if i == 0:
            roles.setdefault("cover", i)
        elif "目" in text and "录" in text or re.search(r"立\s*题\s*依\s*据.*研\s*究\s*计\s*划", text):
            roles.setdefault("toc", i)
        elif text.strip().startswith("PART"):
            roles.setdefault("part", i)
        elif "批评" in text or "指正" in text or "感谢" in text:
            roles["end"] = i
        elif lname == prs.slides[3].slide_layout.name:
            roles.setdefault("content", i)
    return roles


def drop_slide(prs, idx):
    lst = prs.slides._sldIdLst
    sid = lst[idx]
    prs.part.drop_rel(sid.rId)
    lst.remove(sid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--school", default="西南科技大学")
    ap.add_argument("--map", default="")
    a = ap.parse_args()

    prs = Presentation(a.src)
    roles = find_roles(prs)
    if a.map:
        for kv in a.map.split(","):
            k, v = kv.split("=")
            roles[k] = int(v) - 1
    need = ["cover", "toc", "part", "content", "end"]
    miss = [k for k in need if k not in roles]
    if miss:
        sys.exit(f"找不到骨架页: {miss},请用 --map 指定")
    order = [roles[k] for k in need]
    print("骨架页(1起):", {k: roles[k] + 1 for k in need})

    # 清理内容页: 只留页眉四件
    cs = prs.slides[roles["content"]]
    for sh in list(cs.shapes):
        if sh.name not in KEEP_CONTENT_NAMES or (sh.left is not None and sh.left < 0):
            sh._element.getparent().remove(sh._element)

    # 封面与结束页: 学校名、题目、日期
    for key in ("cover", "end"):
        s = prs.slides[roles[key]]
        for sh in s.shapes:
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if re.fullmatch(r"#+", r.text.strip() or "x"):
                            r.text = a.school + "硕士"
                if key == "cover" and len(sh.text_frame.paragraphs) >= 3:
                    runs = sh.text_frame.paragraphs[2].runs
                    if runs:
                        runs[0].text = "论文题目"
                        for r in runs[1:]:
                            r.text = ""
            if sh.has_table:
                for row in sh.table.rows:
                    row.cells[1].text = ""

    # 删除非骨架页(从后往前)
    for i in sorted(set(range(len(prs.slides))) - set(order), reverse=True):
        drop_slide(prs, i)
    # 按 need 顺序重排
    lst = prs.slides._sldIdLst
    ids = list(lst)
    pos = sorted(order)
    for k in need:
        el = ids[pos.index(roles[k])]
        lst.remove(el)
        lst.append(el)
    prs.save(a.dst)
    print("已保存", a.dst)


if __name__ == "__main__":
    main()
