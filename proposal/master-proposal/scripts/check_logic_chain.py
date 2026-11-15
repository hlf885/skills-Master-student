#!/usr/bin/env python3
"""开题报告论证主线自检（只读，不修改文件）。配合 references/11-argument-chain.md 使用。

用法:
    python check_logic_chain.py 稿件.md [--keywords 数字孪生,受限空间|受限腔体,作业位姿] [--matrix 主线表.md]

稿件格式与 check_proposal.py 相同（assets/proposal-skeleton.md 的标题层级）。
题目取自“# 论文题目：……”一行；不给 --keywords 时只做粗拆，建议手动给出题目关键词。

输出：
  1. 首句串读：1.1、1.2 各小节、1.3 每段的第一句，按顺序列出，供连读检查；
  2. 关键词落点：题目关键词在 1.1、1.2、1.3、二、三、四中的出现次数；
  3. 结构检查：1.1 的边界段、核心概念定义、困难段、末段落回题目；1.2 各小节的分类句与小结；
     1.3 趋势条数与研究内容项数是否一致、趋势标题是否为“从……走向……”；2.3 关键问题个数；
  4. --matrix：生成论证主线表草稿（研究内容、趋势、关键问题、方法小节、创新点自动填入，
     困难、不足、前期数据留空待人工填写）。
只能检查形式；论证是否成立、文献是否支撑，必须人工判断。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_proposal import parse_sections, strip_md  # noqa: E402

ITEM_HEAD = r"(?:[（(]\d[）)])"


def paragraphs(body: str) -> list[str]:
    out = []
    for blk in re.split(r"\n\s*\n", body):
        b = blk.strip()
        if not b or b.startswith("#") or b.startswith("|") or b.startswith("!["):
            continue
        if re.match(r"^\$\$", b) or re.fullmatch(r"[（(]\d+-\d+[）)]", b):
            continue
        if re.match(r"^表\d", b) or re.match(r"^图\d", b):
            continue
        out.append(b)
    return out


def first_sentence(p: str) -> str:
    t = re.sub(r"\[@[^\]]+\]|\^?\[\d+(?:[-,，]\d+)*\]\^?", "", strip_md(p)).strip()
    m = re.match(r"^(.+?[。？！])", t)
    return (m.group(1) if m else t)[:120]


def items_of(body: str) -> list[str]:
    parts = re.split(rf"\n\s*(?={ITEM_HEAD})", "\n" + body)
    return [x.strip() for x in parts if re.match(ITEM_HEAD, x.strip())]


def item_title(it: str) -> str:
    line = it.splitlines()[0]
    line = re.sub(rf"^{ITEM_HEAD}\s*", "", line)
    return re.split(r"[。]", line)[0][:40]


def auto_keywords(title: str) -> list[str]:
    t = re.sub(r"^(基于|面向|考虑)", "", title)
    t = re.sub(r"(方法)?(的)?(研究|设计|实现)$", "", t)
    parts = [p for p in re.split(r"的|与|和|及", t) if len(p) >= 2]
    return parts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path)
    ap.add_argument("--keywords", help="题目关键词，逗号分隔；同义写法用竖线并列，如 受限空间|受限腔体")
    ap.add_argument("--matrix", type=Path, help="把论证主线表草稿写到此文件")
    args = ap.parse_args()

    md = args.file.read_text(encoding="utf-8")
    m = re.search(r"^#\s*论文题目[：:]\s*(.+)$", md, flags=re.M)
    title = m.group(1).strip() if m else ""
    secs = parse_sections(md)
    by_key = {k: (lvl, t, b) for lvl, k, t, b in secs if k}
    issues: list[str] = []

    print(f"== 论证主线自检：{args.file.name} ==")
    print(f"题目：{title or '（未找到“# 论文题目：”一行）'}")

    # ---------- 1. 首句串读 ----------
    print("\n[首句串读] 连起来读，应当是一篇通顺的摘要；接不上的地方就是断链处。")
    order = ["1.1"] + sorted([k for k in by_key if re.fullmatch(r"1\.2\.\d+", k)]) + ["1.3"]
    if "1.2" in by_key:
        intro = by_key["1.2"][2].split("\n###")[0]
        order.insert(1, "1.2-导语")
    for k in order:
        if k == "1.2-导语":
            body, name = intro, "1.2 导语"
        elif k in by_key:
            body = by_key[k][2]
            name = k + " " + re.sub(r"^[0-9.]+\s*", "", by_key[k][1])
        else:
            continue
        print(f"  ■ {name}")
        for i, p in enumerate(paragraphs(body), 1):
            print(f"    {i:>2}. {first_sentence(p)}")

    # ---------- 2. 关键词落点 ----------
    kws = [w.strip() for w in (args.keywords or "").split(",") if w.strip()] or auto_keywords(title)
    if kws:
        cols = ["1.1", "1.2", "1.3", "二", "三", "四"]
        print("\n[关键词落点] 题目中的每个关键词都应在 1.1、1.2、1.3、二中出现。")
        if not args.keywords:
            print("  （未给 --keywords，以下为按题目粗拆的结果，建议手动指定）")
        print("  " + "".join(c.rjust(6) for c in cols) + "   关键词")
        for w in kws:
            row = []
            for c in cols:
                n = sum(strip_md(by_key[c][2]).count(x) for x in w.split("|")) if c in by_key else 0
                row.append(n)
            print("  " + "".join(str(n).rjust(6) for n in row) + "   " + w)
            miss = [c for c, n in zip(cols[:4], row[:4]) if n == 0]
            if miss:
                issues.append(f"关键词“{w}”在 {'、'.join(miss)} 中没有出现：补上落点，或检查题目与内容是否对应。")

    # ---------- 3. 结构检查 ----------
    if "1.1" in by_key:
        ps = paragraphs(by_key["1.1"][2])
        txt = strip_md(by_key["1.1"][2])
        if not re.search(r"研究范围|不在.{0,6}范围|只针对|作为已知|已知输入|限定在", txt):
            issues.append("1.1 中没有找到研究边界段（只研究什么、哪些作为已知输入、哪些不在范围内）。")
        if not re.search(r"称为|定义为|简称", txt):
            issues.append("1.1 中没有找到核心概念的定义句（“本课题将……称为……”）。")
        if not re.search(r"困难|难点|难以|问题在于", txt):
            issues.append("1.1 中没有找到困难段：困难应来自场景事实，并能对应到研究内容。")
        if re.search(r"^[（(]\d[）)]", by_key["1.1"][2], flags=re.M):
            issues.append("1.1 中有（1）（2）编号段：困难、特点宜用自然段叙述，不编号。")
        if ps:
            last = strip_md(ps[-1])
            hit = sum(1 for w in kws if any(x in last for x in w.split("|"))) if kws else 0
            if title and title not in last and kws and hit * 2 < len(kws):
                issues.append("1.1 末段没有落回题目：宜写成“因此，以……为研究对象，开展＋题目全称……”，再写理论意义与工程意义。")
    subs = sorted([k for k in by_key if re.fullmatch(r"1\.2\.\d+", k)])
    if subs:
        intro_txt = strip_md(by_key["1.2"][2].split("\n###")[0]) if "1.2" in by_key else ""
        cn = "一二三四五六七八"
        mnum = re.search(r"([二三四五六七八])个方面", intro_txt)
        if mnum and cn.index(mnum.group(1)) + 1 != len(subs):
            issues.append(f"1.2 导语说有{mnum.group(1)}个方面，实际有 {len(subs)} 个小节。")
        for k in subs:
            ps = paragraphs(by_key[k][2])
            body = strip_md(by_key[k][2])
            if not re.search(r"可分为|分为|归纳为|层次|几类|[两三四五]类|[两三四五]种", body):
                issues.append(f"{k} 没有找到分类句（“按照……，已有方法大体可分为 n 类”），容易写成文献罗列。")
            if ps:
                last = strip_md(ps[-1])
                if not re.search(r"但|不足|较少|尚未|少见|没有|仍", last):
                    issues.append(f"{k} 最后一段没有写不足：小节应以“总体来看……但……”收尾，不足对应研究内容。")
    n_trend = n_rc = 0
    if "1.3" in by_key:
        trends = items_of(by_key["1.3"][2])
        n_trend = len(trends)
        for t in trends:
            head = item_title(t)
            if not re.search(r"从.+?(走向|转向|扩展到|发展到|向)", head):
                issues.append(f"1.3 趋势“{head}”不是“从 A 走向 B”的写法，A 宜取自 1.2 小结。")
    if "2.1" in by_key:
        rcs = items_of(by_key["2.1"][2])
        n_rc = len(rcs)
    if n_trend and n_rc and n_trend != n_rc:
        issues.append(f"1.3 有 {n_trend} 条趋势，2.1 有 {n_rc} 项研究内容：应一一对应、顺序一致。")
    kps = items_of(by_key["2.3"][2]) if "2.3" in by_key else []
    if "2.3" in by_key and not 2 <= len(kps) <= 3:
        issues.append(f"2.3 识别到 {len(kps)} 个关键问题，通常为 2–3 个。")

    print("\n[结构检查]")
    if issues:
        for s in issues:
            print(f"  - {s}")
    else:
        print("  未发现形式问题。仍需按 11 号文件第六节人工做删段测试和反向追溯。")

    # ---------- 4. 主线表草稿 ----------
    if args.matrix:
        trends = [item_title(t) for t in items_of(by_key["1.3"][2])] if "1.3" in by_key else []
        rcs = [item_title(t) for t in items_of(by_key["2.1"][2])] if "2.1" in by_key else []
        kp = [item_title(t) for t in kps]
        m32 = [re.sub(r"^[0-9.]+\s*", "", by_key[k][1]) for k in sorted(k for k in by_key if re.fullmatch(r"3\.2\.\d+", k))]
        inn = [re.sub(r"^[0-9.]+\s*", "", by_key[k][1]) for k in sorted(k for k in by_key if re.fullmatch(r"4\.\d+", k))]
        lines = [
            f"# 论证主线表：{title}",
            "",
            "先填“1.1 困难”和“1.2 不足”两列（事实），再核对其余各列是否由它们推出。任何一格填不出来就是断链。",
            "关键问题、方法小节、创新点按顺序自动列出，需人工调整到对应的行。",
            "",
            "| 研究内容 | 1.1 困难（场景事实） | 1.2 不足（文献事实） | 1.3 趋势 | 2.3 关键问题 | 3.2 方法 | 四 创新点 | 五 前期数据 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        n = max(len(rcs), len(trends), 1)
        for i in range(n):
            def g(a):
                return a[i] if i < len(a) else ""
            lines.append(f"| {g(rcs)} |  |  | {g(trends)} | {g(kp)} | {g(m32)} | {g(inn)} |  |")
        args.matrix.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\n[主线表] 草稿已写到 {args.matrix}")
    print("\n说明：本脚本只检查形式；论证是否成立、文献是否支撑须人工判断。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
