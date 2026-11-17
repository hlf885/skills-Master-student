#!/usr/bin/env python3
"""示例生成脚本: 用占位内容演示 swust_kit 的全部常用版式。

用法: python3 example_build.py <Skill目录> [输出.pptx]
制作真实答辩 PPT 时, 复制本文件为 build_deck.py, 把占位文字换成开题报告中的内容,
把占位图换成开题报告中提取出的图片(extract_docx.py 输出的 img/ 目录)。
"""
import sys
import tempfile
from pathlib import Path

SKILL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("example_deck.pptx")
sys.path.insert(0, str(SKILL / "scripts"))
from swust_kit import Deck, BLUE, DARK, GRAY, LIGHT, LIGHT2, RED  # noqa: E402


def placeholder(path, w=1200, h=800, label="示意图"):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), (232, 239, 248))
    dr = ImageDraw.Draw(im)
    dr.rectangle([8, 8, w - 9, h - 9], outline=(39, 79, 127), width=6)
    dr.line([0, 0, w, h], fill=(180, 195, 215), width=4)
    dr.line([0, h, w, 0], fill=(180, 195, 215), width=4)
    im.save(path)
    return path


tmp = Path(tempfile.mkdtemp())
IMG_A = placeholder(tmp / "a.png", 1200, 900)
IMG_B = placeholder(tmp / "b.png", 1600, 1100)

d = Deck(SKILL / "assets" / "swust_proposal_template.pptx")
T = d.text

d.cover(2026, "西南科技大学硕士", "基于某某方法的某类对象某某问题研究", title_size=34)
d.toc()

# ---------------- 立题依据
d.part(1, "立 题 依 据")
s = d.content(1, "立题依据", "研究背景")
T(s, 1.4, 3.4, 16.6, 13.6, [
    "__行业需求：__一句话写清国家或行业层面的需求（取自开题报告1.1）",
    "__对象现状：__一句话写清研究对象面临的问题，关键处用**红色强调**",
    "__技术约束：__一句话写清为什么只能用本课题的手段解决",
], size=18, bullet="▶", spacing=1.35, space_after=16)
d.picture(s, IMG_A, 18.6, 3.4, 6.7, 9.0, caption="对象图一")
d.picture(s, IMG_A, 25.6, 3.4, 6.9, 9.0, caption="对象图二")
d.bar(s, 18.6, 13.4, 13.9, 1.6, "一句话结论", size=17)

s = d.content(1, "立题依据", "研究目的")
d.box(s, 1.4, 3.4, 31.1, 2.2, fill=LIGHT, line=DARK)
T(s, 1.7, 3.5, 30.5, 2.0, ["__核心概念：__给出本课题核心概念的定义（与开题报告一致）"], size=16, anchor="m")
for i, t in enumerate(["难点一", "难点二", "难点三", "难点四"]):
    d.card(s, 1.4 + i * 7.85, 6.4, 7.45, 6.9, t, ["每张卡片 40 字以内，写清这个难点是什么、为什么难"], size=17, title_size=18, spacing=1.4)
d.arrow(s, 16.3, 13.45, 1.2, 0.8, "down")
d.box(s, 1.4, 14.4, 31.1, 2.6, fill=None, line=RED, dash=True)
T(s, 1.7, 14.5, 30.5, 2.4, ["问题归纳：把上面的难点归结为一个**可研究的科学问题**"], size=16, anchor="m")

s = d.content(1, "立题依据", "国内外研究现状：方向一")
d.table(s, 1.4, 3.4, 20.6, [
    ["方法类别", "代表工作", "优点", "局限"],
    ["类别一", "代表做法", "优点", "局限"],
    ["类别二", "代表做法", "优点", "局限"],
    ["类别三", "代表做法", "优点", "局限"],
], col_w=[4.4, 6.0, 4.2, 6.0], row_h=1.6, size=14, head_size=15)
d.picture(s, IMG_A, 22.5, 3.4, 10.0, 6.4, caption="代表性工作示意（注明来源）", cap_size=11)
for i, g in enumerate(["不足一，关键处**红色**", "不足二", "不足三"]):
    xx = 1.4 + i * 10.45
    d.circle_num(s, xx, 12.75, 1.0, i + 1)
    d.box(s, xx + 1.2, 12.55, 8.9, 4.4, fill=LIGHT2, line=RED, dash=True)
    T(s, xx + 1.35, 12.65, 8.6, 4.2, [g], size=16, anchor="m")

# ---------------- 研究内容与目标
d.part(2, "研究内容与目标")
s = d.content(2, "研究内容与目标", "研究内容")
for i in range(4):
    xx = 1.4 + i * 7.85
    d.box(s, xx, 3.4, 7.45, 13.6, fill=LIGHT2, line=DARK, dash=True)
    d.circle_num(s, xx + 3.1, 3.6, 1.2, i + 1, size=18)
    d.bar(s, xx + 0.2, 5.0, 7.05, 2.3, f"研究内容{i + 1}全称", size=15)
    T(s, xx + 0.25, 7.6, 6.95, 6.6, ["一句话写做什么，50 字以内"], size=17, spacing=1.45)
    d.bar(s, xx + 0.2, 14.4, 7.05, 2.3, ["产出", "这一项交给下一项的结果"], size=14, fill=BLUE)
    if i < 3:
        d.arrow(s, xx + 7.47, 9.8, 0.36, 0.7)

# ---------------- 研究方案
d.part(3, "研 究 方 案")
s = d.content(3, "研究方案", "研究一：方法名称")
d.picture(s, IMG_B, 1.4, 3.3, 14.6, 13.7, caption="方法流程图")
d.bar(s, 16.5, 3.3, 16.0, 0.85, "核心定义", size=14, align="l")
w, h = d.formula(s, 16.8, 4.35, r"M_c=\left\{Y\in S\mid \Phi_c(Y)=1\right\}", size=16, label="(3-1)")
T(s, 16.5, 4.55 + h, 16.0, 1.6, ["说明公式中各符号的含义，一两行"], size=13)
y = 6.4 + h
d.bar(s, 16.5, y, 16.0, 0.85, "优化目标", size=14, align="l")
w, h = d.formula(s, 16.8, y + 1.0, r"\Pi^{*}=\underset{\Pi}{\mathrm{lexmin}}\left(f_1(\Pi),\ f_2(\Pi)\right)", size=15, label="(3-2)")

# ---------------- 创新点
d.part(4, "创  新  点")
s = d.content(4, "创新点", "本课题可能的创新之处")
for i in range(2):
    yy = 3.4 + i * 6.9
    d.circle_num(s, 1.4, yy, 1.3, i + 1, size=20)
    d.bar(s, 2.9, yy, 29.6, 1.3, f"拟提出一种××方法（创新点{i + 1}）", size=17, align="l")
    d.box(s, 2.9, yy + 1.5, 29.6, 4.9, fill=LIGHT2, line=DARK, dash=True)
    T(s, 3.1, yy + 1.6, 29.2, 4.7, ["做法：一两句话", "区别：与已有方法相比的**区别点**"], size=17, anchor="m")

# ---------------- 研究基础
d.part(5, "研究基础与工作条件")
s = d.content(5, "研究基础与工作条件", "研究基础")
T(s, 1.4, 3.3, 17.0, 13.7, ["只写开题报告第五部分已经完成的工作", "数字与开题报告一致", "保留限定说明"],
  size=16, bullet="•", spacing=1.35, space_after=8)
d.picture(s, IMG_A, 19.0, 3.3, 13.5, 13.7, caption="已完成工作截图")

# ---------------- 研究计划
d.part(6, "研 究 计 划")
s = d.content(6, "研究计划", "学位论文工作计划")
d.table(s, 1.4, 3.4, 31.1, [["时间", "研究内容", "预期效果"]] +
        [[f"阶段{i + 1}", "与开题报告工作计划表一致", "预期效果"] for i in range(6)],
        col_w=[4.6, 15.5, 11.0], row_h=1.68, size=14, head_size=16, align_cols="cll", bold_first_col=True)

d.end(2026, "西南科技大学硕士", date="2026年11月")
d.save(OUT)
print("saved", OUT)
