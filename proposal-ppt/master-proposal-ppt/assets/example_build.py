#!/usr/bin/env python3
"""示例生成脚本: 用占位内容演示 8 到 10 分钟开题答辩 PPT 的页序、常用版式和备注讲稿。

用法: python3 example_build.py <Skill目录> [输出.pptx]
制作真实答辩 PPT 时, 复制本文件为 build_deck.py, 把占位文字换成开题报告中的内容,
把占位图换成开题报告中提取出的图片(extract_docx.py 输出的 img/ 目录)和研究背景用的网络实拍图,
并为每页写好备注讲稿。运行结束会打印每页备注字数和预计时长。
"""
import sys
import tempfile
from pathlib import Path

SKILL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("example_deck.pptx")
sys.path.insert(0, str(SKILL / "scripts"))
from swust_kit import Deck, BLUE, DARK, GRAY, LIGHT, LIGHT2, RED  # noqa: E402


def placeholder(path, w=1200, h=800):
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
IMG_W = placeholder(tmp / "w.png", 1800, 650)

d = Deck(SKILL / "assets" / "swust_proposal_template.pptx")
T, N = d.text, d.notes

# 1 封面
s = d.cover(2026, "西南科技大学硕士", "基于某某方法的某类对象某某问题研究", title_size=34)
N(s, "各位老师好，我是（姓名），指导老师是（导师姓名）老师。我的开题题目是《……》。")
# 2 目录（8 到 10 分钟版不用 PART 过渡页）
s = d.toc()
N(s, "下面我从立题依据、研究内容与目标、研究方案、创新点、研究基础与工作条件、研究计划六个方面进行汇报。")

# 3 研究背景：图墙 + 关键词链 + 网络实拍图（页底注明来源与许可）
s = d.content(1, "立题依据", "研究背景")
d.picture(s, IMG_A, 1.4, 3.3, 9.8, 6.6, caption="开题报告中的对象图")
d.picture(s, IMG_A, 11.5, 3.3, 9.8, 6.6, caption="开题报告中的部件图")
d.picture(s, IMG_A, 1.4, 10.2, 9.8, 6.4, caption="网络实拍图一（装置名）")
d.picture(s, IMG_A, 11.5, 10.2, 9.8, 6.4, caption="网络实拍图二（装置名）")
d.chain(s, 22.0, 3.3, 10.5, ["原因一\n短句", "原因二\n短句", "结论\n短句"], h=1.7, gap=0.6, fills=[BLUE, BLUE, RED])
d.picture(s, IMG_W, 22.0, 10.4, 10.5, 5.0, caption="网络实拍图三（装置名）")
T(s, 1.4, 16.75, 30.5, 0.5, ["实拍图来源：Wikimedia Commons。图一：作者，许可；图二：作者，许可；图三：作者，许可"], size=8, color=GRAY, fit_check=False)
N(s, "第一句说行业需求，第二句说对象现状，第三句结合左图说明对象，第四句结合实拍图说明为什么只能用本课题的手段。")

# 4 研究现状：分类条
s = d.content(1, "立题依据", "国内外研究现状")
d.class_row(s, 3.3, ["方向一", ""], ["做法一：代表工作，评价", "做法二：代表工作，评价"], "不足：一句话")
d.class_row(s, 7.5, ["方向二", ""], ["做法一：代表工作，评价", "做法二：代表工作，评价", "做法三：代表工作，评价"], "不足：一句话")
d.picture(s, IMG_A, 24.0, 3.3, 8.5, 8.4, caption="代表性工作（注明来源）", cap_size=11)
d.bar(s, 1.4, 14.0, 31.1, 2.85, ["本课题拟……（切入点，一句话）"], size=17, fill=LIGHT, color=DARK, radius=True)
N(s, "按方向介绍已有做法和各自的不足，最后一句落到本课题的切入点。")

# 5 研究目标与关键问题：双栏
s = d.content(2, "研究内容与目标", "研究目标与拟解决的关键问题")
d.bar(s, 1.4, 3.3, 15.3, 1.0, "研究目标", size=17)
for i in range(4):
    yy = 4.6 + i * 3.1
    d.circle_num(s, 1.4, yy + 0.65, 1.1, i + 1, fill=BLUE)
    d.box(s, 2.7, yy, 14.0, 2.75, fill=LIGHT2, line=BLUE, dash=True)
    T(s, 2.9, yy, 13.6, 2.75, [f"__目标{i + 1}__", "含量化指标的一句话"], size=15, anchor="m", space_after=2)
d.bar(s, 17.2, 3.3, 15.3, 1.0, "拟解决的关键问题", size=17, fill=RED)
for i in range(3):
    yy = 4.6 + i * 4.15
    d.bar(s, 17.2, yy, 2.4, 3.8, f"问题{i + 1}", size=15, fill=DARK)
    d.box(s, 19.7, yy, 12.8, 3.8, fill=LIGHT2, line=RED, dash=True)
    T(s, 19.9, yy, 12.4, 3.8, ["关键问题全称"], size=16, anchor="m")
N(s, "逐条念研究目标及其指标，再念三个关键问题。")

# 6 研究方案：两项研究一页 + 可编辑公式
s = d.content(3, "研究方案", "研究一：××　研究二：××")
d.picture(s, IMG_B, 1.4, 3.2, 15.2, 10.8, caption="研究一：方法流程图")
d.picture(s, IMG_B, 17.2, 3.2, 15.3, 10.8, caption="研究二：方法流程图")
d.formula(s, 2.0, 14.6, r"M_c=\left\{Y\in S\mid \Phi_c(Y)=1\right\}", size=17)
d.formula(s, 17.8, 14.6, r"\Pi^{*}=\underset{\Pi}{\mathrm{lexmin}}\left(f_1,\ f_2\right)", size=17)
N(s, "按左右两张图分别讲研究一和研究二，每项三到四句。")

# 7 研究基础：关键数字色块
s = d.content(5, "研究基础与工作条件", "研究基础：前期工作")
d.picture(s, IMG_A, 1.4, 3.3, 15.0, 13.6, caption="前期工作截图")
for i, (a, b, c) in enumerate([("不可行", "142", GRAY), ("部分可行", "278", BLUE), ("可行", "30", RED)]):
    d.bar(s, 17.1 + i * 5.2, 9.8, 5.0, 2.4, [b, a], size=17, fill=c)
N(s, "说明已完成的工作和关键数字，并保留开题报告中的限定说明。")

# 8 研究基础：个人成果留白页（只有页眉，内容区空白）
s = d.blank_page(5, "研究基础与工作条件", "研究基础：个人成果")
N(s, "（此页留白：粘贴比赛获奖、论文、专利等个人成果后，在这里补充对应讲稿，约30秒。）")

# 9 研究计划
s = d.content(6, "研究计划", "学位论文工作计划")
d.table(s, 1.4, 3.4, 31.1, [["时间", "研究内容", "预期效果"]] +
        [[f"阶段{i + 1}", "与开题报告工作计划表一致", "预期效果"] for i in range(6)],
        col_w=[4.6, 16.0, 10.5], row_h=1.68, size=15, head_size=16, align_cols="cll", bold_first_col=True)
N(s, "研究计划如表。")

s = d.end(2026, "西南科技大学硕士", date="2026年11月")
N(s, "以上是我的开题汇报，请各位老师批评指正，谢谢。")
d.save(OUT)
print("saved", OUT)
d.notes_report()
