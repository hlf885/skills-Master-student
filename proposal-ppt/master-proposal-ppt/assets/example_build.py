#!/usr/bin/env python3
"""示例生成脚本 (v1.2.0): 用占位内容演示 8 到 10 分钟开题答辩 PPT 的页序、学术极简规则和按内容变化的版式。

用法: python3 example_build.py <Skill目录> [输出.pptx] [--theme 学术极简]
制作真实答辩 PPT 时, 复制本文件为 build_deck.py, 把占位文字换成开题报告中的内容, 把占位图换成
extract_docx.py 提取的图片和研究背景用的网络实拍图, 为每页写好讲稿和备查 (公式详解、可能的追问)。
版式说明见 references/03-layout-patterns.md, 审美规则见 references/08-aesthetics-and-style.md。
"""
import sys
import tempfile
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
THEME = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "学术极简"
if THEME in args:
    args.remove(THEME)
SKILL = Path(args[0]) if args else Path(__file__).resolve().parents[1]
OUT = Path(args[1]) if len(args) > 1 else Path("example_deck.pptx")
sys.path.insert(0, str(SKILL / "scripts"))
from swust_kit import Deck  # noqa: E402


def placeholder(path, w=1200, h=800):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), (241, 244, 248))
    dr = ImageDraw.Draw(im)
    dr.rectangle([4, 4, w - 5, h - 5], outline=(200, 208, 219), width=4)
    dr.line([0, 0, w, h], fill=(214, 220, 228), width=3)
    dr.line([0, h, w, 0], fill=(214, 220, 228), width=3)
    im.save(path)
    return path


tmp = Path(tempfile.mkdtemp())
IMG_A = placeholder(tmp / "a.png", 1200, 800)
IMG_T = placeholder(tmp / "t.png", 1000, 1100)
IMG_W = placeholder(tmp / "w.png", 2000, 900)

d = Deck(SKILL / "assets" / "swust_proposal_template.pptx")
d.set_theme(THEME)
T, N, H, L = d.text, d.notes, d.headline, d.line
X0, XW, Y0 = 1.6, 30.6, 5.0

# 1 封面 / 2 目录
s = d.cover(2026, "西南科技大学硕士", "基于某某方法的某类对象某某问题研究", title_size=34)
N(s, "各位老师好，我是（姓名），指导老师是（导师姓名）老师。我的开题题目是《……》。")
s = d.toc()
N(s, "下面我从立题依据、研究内容与目标、研究方案、创新点、研究基础与工作条件、研究计划六个方面汇报。")

# 3 L1 图墙加因果
s = d.content(1, "立题依据", "研究背景")
H(s, "一句结论：为什么这个问题现在必须解决")
for i in range(4):
    d.fig(s, IMG_A, X0 + (i % 2) * 10.0, Y0 + (i // 2) * 6.0, 9.6, 5.6, cap=f"图 占位图 {i + 1}", align="c")
L(s, 22.3, Y0 + 0.2, 22.3, 16.6, color=d.RULE)
for i, (a, b) in enumerate([("背景变化一", "一行解释"), ("由此带来的需求", "一行解释"), ("本课题要解决的事", "一行解释")]):
    y = 5.6 + i * 3.7
    T(s, 23.0, y, 9.4, 1.0, [a], size=20, color=d.NAVY_HEX if i == 2 else d.INK, bold=True, fit_check=False)
    T(s, 23.0, y + 1.05, 9.4, 0.9, [b], size=17, color=d.MUTE, fit_check=False)
    if i < 2:
        T(s, 23.0, y + 2.05, 2.0, 1.2, ["↓"], size=22, color="9AA3AE", fit_check=False)
T(s, X0, 17.45, XW, 0.5, ["网络实拍图来源：作者，许可"], size=8, color="9AA3AE", fit_check=False)
N(s, "（讲稿：背景、需求、本课题要解决的事，约 40 秒。）", ref="可能的追问\n问：……\n答：……（只用开题报告里的内容）")

# 4 L3 演进图示
s = d.content(1, "立题依据", "国内外研究现状")
H(s, "一句结论：已有工作做到哪一步，空白在哪里")
for i, (a, b, hl) in enumerate([("阶段一", "做法与特点", False), ("阶段二", "做法与特点", False), ("本课题切入点", "要做到什么", True)]):
    x = X0 + i * 10.5
    d.box(s, x, 5.4, 9.6, 4.6, fill=d.NAVY_HEX if hl else d.TINT, line=None, radius=False)
    T(s, x + 0.5, 5.75, 8.7, 1.2, [a], size=21, color="FFFFFF" if hl else d.INK, bold=True, fit_check=False)
    T(s, x + 0.5, 7.05, 8.7, 1.0, [b], size=17, color="DCE4EE" if hl else d.MUTE, fit_check=False)
    if i < 2:
        T(s, x + 9.6, 6.9, 0.9, 1.4, ["›"], size=36, color="9AA3AE", align="c", anchor="m", fit_check=False)
L(s, X0, 11.2, X0 + XW, 11.2, color=d.RULE)
T(s, X0, 11.55, 6, 0.7, ["尚缺"], size=14, color=d.ACC, bold=True, fit_check=False)
for i in range(3):
    T(s, X0 + i * 10.5, 12.3, 9.6, 2.4, ["与上方阶段对应的一条研究空白"], size=18, color=d.INK)
N(s, "（讲稿：两类做法、各自不足、本课题切入点，约 50 秒。）")

# 5 L4 三线表
s = d.content(1, "立题依据", "国内外研究现状")
H(s, "一句结论：几类方法各有什么局限")
d.rule_table(s, X0, Y0 + 0.1, [4.0, 10.6, 7.4], [
    ["研究方向", "代表方法", "特点"],
    ["方向一", "方法 A", "优点与局限"], ["", "方法 B", "优点与局限"],
    ["方向二", "方法 C", "优点与局限"], ["", "方法 D", "优点与局限"]],
    [1.0] + [1.6] * 4, size=17, head_size=14)
d.fig(s, IMG_A, 24.6, Y0 + 0.1, 7.6, 5.0, cap="图 代表性方法示意", align="c")
L(s, X0, 15.75, X0 + XW, 15.75, color=d.RULE)
T(s, X0, 16.0, XW, 1.0, ["本课题：一句话说明怎么做"], size=18, color=d.NAVY_HEX, bold=True, fit_check=False)
N(s, "（讲稿：按方向讲方法与局限，约 40 秒。）")

# 6 L5 整页大图
s = d.content(2, "研究内容与目标", "研究内容")
H(s, "一句结论：几项研究内容分别回答什么问题")
d.fig(s, IMG_W, X0, Y0, XW, 12.6, align="c")
N(s, "（讲稿：逐项讲研究内容及其衔接，约 40 秒。）")

# 7 L8 分栏细线
s = d.content(2, "研究内容与目标", "研究目标与拟解决的关键问题")
H(s, "一句结论：目标怎么检验，难点在哪里")
T(s, X0, Y0, 12, 0.7, ["研究目标"], size=14, color=d.MUTE, bold=True, fit_check=False)
for i in range(4):
    y = Y0 + 0.9 + i * 2.85
    if i:
        L(s, X0, y - 0.2, 16.2, y - 0.2, color=d.RULE)
    T(s, X0, y, 3.9, 2.4, [f"目标{i + 1}"], size=18, color=d.INK, bold=True, anchor="m", fit_check=False)
    T(s, 5.6, y, 10.6, 2.4, ["指标写成 __可检验的数字__"], size=18, color=d.INK, anchor="m")
L(s, 17.1, Y0, 17.1, 17.0, color=d.RULE)
T(s, 17.9, Y0, 12, 0.7, ["拟解决的关键问题"], size=14, color=d.MUTE, bold=True, fit_check=False)
for i in range(3):
    y = Y0 + 0.9 + i * 3.8
    if i:
        L(s, 17.9, y - 0.2, X0 + XW, y - 0.2, color=d.RULE)
    T(s, 17.9, y, 2.2, 3.3, [f"问题{i + 1}"], size=15, color=d.ACC, bold=True, anchor="m", fit_check=False)
    T(s, 20.2, y, 12.0, 3.3, ["关键问题的短句表述"], size=19, color=d.INK, bold=True, anchor="m")
N(s, "（讲稿：目标与关键问题，约 45 秒。）", ref="关键问题各自难在哪里：……")

# 8 L6 左图右步骤
s = d.content(3, "研究方案", "技术路线")
H(s, "一句结论：总体思路是什么")
d.fig(s, IMG_T, X0, Y0, 15.6, 12.5, align="c")
L(s, 17.9, Y0, 17.9, 17.0, color=d.RULE)
T(s, 18.6, Y0, 12, 0.7, ["基本思路"], size=14, color=d.MUTE, bold=True, fit_check=False)
T(s, 18.6, Y0 + 0.8, 13.6, 2.8, ["一两行写清总体思路"], size=17, color=d.NAVY_HEX, bold=True)
for i in range(4):
    y = 9.0 + i * 2.05
    L(s, 18.6, y - 0.25, X0 + XW, y - 0.25, color=d.RULE)
    T(s, 18.6, y, 1.2, 1.4, [str(i + 1)], size=24, color=d.NAVY_HEX, bold=True, anchor="m", fit_check=False)
    T(s, 19.9, y, 12.3, 1.4, ["步骤短句"], size=18, color=d.INK, anchor="m")
N(s, "（讲稿：技术路线，约 35 秒。）")

# 9 L7 图加公式
s = d.content(3, "研究方案", "研究一：××　研究二：××")
H(s, "一句结论：两项研究分别怎么做")
d.fig(s, IMG_A, X0, Y0, 14.8, 8.2, cap="图 研究一流程", align="c")
d.fig(s, IMG_A, 17.4, Y0, 14.8, 8.2, cap="图 研究二流程", align="c")
L(s, 16.5, Y0, 16.5, 17.2, color=d.RULE)
d.formula(s, 2.0, 13.6, r"y=f(x;\theta)", size=20, label="(3-1)")
T(s, X0, 15.1, 14.6, 2.0, ["一行说明公式在做什么"], size=16, color=d.INK)
d.formula(s, 17.8, 13.6, r"\theta^{*}=\arg\min_{\theta}\ J(\theta)", size=20, label="(3-2)")
T(s, 17.4, 15.1, 14.8, 2.0, ["一行说明公式在做什么"], size=16, color=d.INK)
N(s, "（讲稿：口语解释两项研究，不念符号，约 50 秒。）",
  ref="公式详解\n【式 3-1】每个符号的含义；为什么这样设计；取值怎么定。\n可能的追问\n问：……\n答：……")

# 10 L4 三线表 (创新点)
s = d.content(4, "创新点", "本课题可能的创新之处")
H(s, "一句结论：创新分别解决什么")
d.rule_table(s, X0, Y0 + 0.3, [10.8, 9.8, 10.0], [
    ["创新点", "已有方法", "本课题"],
    ["1　创新点一名称", "已有做法", "本课题做法"],
    ["2　创新点二名称", "已有做法", "本课题做法"]],
    [1.2, 4.3, 4.3], size=19, head_size=15, colors=[d.INK, d.MUTE, d.NAVY_HEX])
N(s, "（讲稿：两点创新，约 35 秒。）")

# 11 L9 大数字加图
s = d.content(5, "研究基础与工作条件", "研究基础：前期工作")
H(s, "一句结论：前期结果说明了什么")
d.fig(s, IMG_T, X0, Y0, 14.6, 12.4, cap="图 前期结果", align="c")
L(s, 16.9, Y0, 16.9, 17.2, color=d.RULE)
T(s, 17.6, Y0 + 0.8, 14.6, 4.0, ["已完成工作一", "已完成工作二", "已完成工作三"], size=17, color=d.INK, bullet="·", spacing=1.2, space_after=6)
L(s, 17.6, 10.1, X0 + XW, 10.1, color=d.RULE)
for i, (n, t) in enumerate([("000", "数字一"), ("000", "数字二"), ("00", "最重要的数字")]):
    d.big_number(s, 17.6 + i * 5.0, 11.2, 4.8, n, t, color=d.NAVY_HEX if i == 2 else d.INK)
T(s, 17.6, 14.6, 14.6, 1.0, ["一句结论"], size=18, color=d.INK, bold=True, fit_check=False)
T(s, 17.6, 15.6, 14.6, 1.0, ["限定语，如 基于临时模型"], size=13, color=d.MUTE, fit_check=False)
N(s, "（讲稿：前期工作与结果，约 35 秒。）")

# 12 留白页
s = d.blank_page(5, "研究基础与工作条件", "研究基础：个人成果")
N(s, "（此页留白：粘贴个人成果后补充讲稿，约 30 秒。）")

# 13 计划
s = d.content(6, "研究计划", "学位论文工作计划")
H(s, "一句结论：按什么节奏推进，何时中期、何时答辩")
d.rule_table(s, X0, Y0 + 0.1, [6.2, 14.6, 9.8], [["时间", "研究内容", "预期效果"]] + [["0000.00 至 0000.00", "内容", "效果"]] * 6,
             [1.0] + [1.6] * 6, size=17, head_size=14, first_bold=False)
N(s, "（讲稿：研究计划，约 15 秒。）")

# 14 结束
s = d.end(2026, "西南科技大学硕士", date="2026年11月")
N(s, "以上是我的开题汇报，请各位老师批评指正，谢谢。")

d.save(OUT)
print("saved", OUT)
d.notes_report()
