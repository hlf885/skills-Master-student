#!/usr/bin/env python3
"""风格样页: 用同一组内容, 按几套整套风格各出 4 张样页, 渲染成图让用户挑。

为什么先出样页: 风格是用户的审美决定, 说不清, 看了才知道。先用 4 张有代表性的页面
(演进图示、三线表对比、图加公式、大数字结果) 把每套风格摆出来, 用户选定后再做整套。
每套风格内部 4 张页面的版式各不相同, 这正是整套 PPT 的样子: 规则统一, 版式按内容变化。

用法:
  python3 style_gallery.py <本Skill目录> <输出目录> [--styles V3实例,学术极简,期刊黑白,...] [--content my_content.py] [--render]
  V3实例 是整套配方型风格, 样页取自 assets/presets/v3_deck.py 生成的 17 页示例; 用自己的内容看效果时,
  直接运行 v3_deck.py --content 自己的内容文件。
  --content 指向一个 python 文件, 里面定义与下方 DEMO 同结构的 CONTENT 字典 (用用户开题报告里的真实内容替换)。
  不给 --content 时用中性示例内容 (虚构课题, 只演示版式, 页面上标注 示例内容)。
  --render 需要 LibreOffice 与 pdftoppm, 输出 每套风格一张 2x2 拼图 PNG。
"""
import argparse
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

DEMO = {
    "note": "示例内容，虚构课题，仅演示版式",
    "evolution": {
        "part": (1, "立题依据", "国内外研究现状"),
        "head": "已有检测多依赖人工设定阈值，缺少能随工况自适应的检测方法",
        "stages": [("人工目检与抽检", "依赖经验，效率低", ["射线底片人工评片", "超声信号人工判读"]),
                   ("传统图像处理", "阈值与特征人工设定", ["边缘检测与形态学", "纹理特征加分类器"]),
                   ("按工况自适应检测", "判据随工况更新", ["本课题切入点"])],
        "gaps": ["评片结果因人而异，难以批量复核", "阈值换一种工况就要重新调", "工况变化后如何更新判据讨论少"],
    },
    "compare": {
        "part": (4, "创新点", "本课题可能的创新之处"),
        "head": "两点创新分别解决：缺陷找得准不准，以及换了工况判据怎么更新",
        "rows": [["创新点", "已有方法", "本课题"],
                 [["1　焊缝区域约束的", "　 候选缺陷提取方法"], "全图搜索\n背景纹理干扰大", "先定位焊缝区域\n只在区域内提取候选"],
                 [["2　工况自适应的", "　 缺陷判别方法"], "固定阈值\n换工况需人工重调", "按工况估计阈值\n新样本到来增量更新"]],
    },
    "method": {
        "part": (3, "研究方案", "研究二：自适应判别"),
        "head": "判别分三步：定位焊缝区域、提取候选缺陷、按工况自适应确定阈值",
        "latex": r"s(x)=\sigma\!\left(w^{\top}\phi(x)\right)\ \ge\ \tau_c",
        "points": ["φ(x) 为候选区域特征，w 为判别权重", "阈值 τ 按工况分别估计，由该工况样本确定", "新工况样本到来时只更新该工况的阈值，不重新训练"],
        "figure_title": "研究二流程",
    },
    "result": {
        "part": (5, "研究基础与工作条件", "研究基础：前期试验"),
        "head": "固定阈值在新工况下漏检明显，判据需要随工况调整",
        "numbers": [("120", "测试样本"), ("18", "固定阈值漏检"), ("15%", "漏检比例")],
        "conclusion": "换到新工况后，原阈值漏检 18 张，约占 15%",
        "bars": (["工况 A", "工况 B", "工况 C"], [3, 18, 11]),
        "bar_title": "各工况漏检张数",
    },
}


def _cjk(plt):
    from matplotlib import font_manager
    names = {x.name for x in font_manager.fontManager.ttflist}
    for f in ("Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", "SimHei", "WenQuanYi Micro Hei"):
        if f in names:
            plt.rcParams["font.family"] = f
            break
    plt.rcParams["axes.unicode_minus"] = False


def demo_figures(tmp):
    """示例内容用的两张图: 流程示意和柱状图。真实使用时换成开题报告里的图。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _cjk(plt)
    fig, ax = plt.subplots(figsize=(6, 4.6), dpi=200)
    ax.axis("off")
    boxes = ["输入图像", "焊缝区域定位", "候选缺陷提取", "按工况自适应判别", "缺陷类别与位置"]
    for i, b in enumerate(boxes):
        y = 0.9 - i * 0.2
        ax.add_patch(plt.Rectangle((0.2, y - 0.06), 0.6, 0.12, fill=False, ec="#4B5563", lw=1.2))
        ax.text(0.5, y, b, ha="center", va="center", fontsize=13, color="#1F2933")
        if i < len(boxes) - 1:
            ax.annotate("", xy=(0.5, y - 0.14), xytext=(0.5, y - 0.065), arrowprops=dict(arrowstyle="->", color="#6B7280"))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    flow = tmp / "demo_flow.png"
    fig.savefig(flow, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return flow


def bar_png(tmp, labels, vals, color, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _cjk(plt)
    fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=200)
    ax.bar(labels, vals, color=[f"#{color}" if v == max(vals) else "#C8D0DB" for v in vals], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.03, str(v), ha="center", fontsize=13, color="#1F2933")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(left=False, labelleft=False, labelsize=13)
    out = tmp / f"bar_{name}.png"
    fig.savefig(out, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return out


def tag(d, s, style, layout):
    d.text(s, 22.0, 17.55, 10.2, 0.6, [f"风格：{style}　版式：{layout}"], size=10, color="9AA3AE", align="r", fit_check=False)


def page_evolution(d, th, c, style, note):
    s = d.content(*c["part"])
    d.headline(s, c["head"])
    big = th["head"] > 24
    tint = th["panels"] == "tint"
    y0 = 5.6 if big else 5.4
    n = len(c["stages"])
    for i, (a, b, ex) in enumerate(c["stages"]):
        hl = i == n - 1
        x = 1.6 + i * 10.5
        d.box(s, x, y0, 9.6, 4.6, fill=th["hl"] if hl else d.TINT, line=None, radius=False)
        d.text(s, x + 0.5, y0 + 0.35, 8.7, 1.2, [a], size=21, color="FFFFFF" if hl else d.INK, bold=True, fit_check=False)
        d.text(s, x + 0.5, y0 + 1.6, 8.7, 1.0, [b], size=17, color="E5EAF0" if hl else d.MUTE, fit_check=False)
        if not big:
            d.text(s, x + 0.5, y0 + 2.8, 8.7, 1.6, ex, size=15 if hl else 14, color="FFFFFF" if hl else d.MUTE, bold=hl, space_after=0, fit_check=False)
        if i < n - 1:
            d.text(s, x + 9.6, y0 + 1.5, 0.9, 1.4, ["›"], size=36, color="9AA3AE", align="c", anchor="m", fit_check=False)
    gy = y0 + 5.6
    if not tint:
        d.line(s, 1.6, gy, 32.2, gy, color=d.RULE)
    d.text(s, 1.6, gy + 0.3, 6, 0.7, ["尚缺"], size=14, color=th["gap"], bold=True, fit_check=False)
    for i, g in enumerate(c["gaps"]):
        x = 1.6 + i * 10.5
        if tint:
            d.box(s, x, gy + 1.0, 9.6, 2.6, fill=d.TINT, line=None, radius=False)
        d.text(s, x + (0.4 if tint else 0), gy + 1.1, 9.6 - (0.8 if tint else 0), 2.4, [g],
               size=th["body"], color=d.INK, anchor="m" if tint else "t")
    d.text(s, 1.6, 17.55, 12, 0.6, [note], size=10, color="9AA3AE", fit_check=False)
    tag(d, s, style, "演进图示")


def page_compare(d, th, c, style, note):
    s = d.content(*c["part"])
    d.headline(s, c["head"])
    rows = c["rows"]
    widths = [10.8, 9.8, 10.0]
    mode = th["panels"]
    if mode in ("tint", "dark"):
        for ci, hd in enumerate(rows[0]):
            x = 1.6 + sum(widths[:ci])
            d.text(s, x + 0.2, 5.2, widths[ci] - 0.4, 0.8, [hd], size=14, color=d.MUTE, bold=True, fit_check=False)
        if mode == "dark":
            d.line(s, 1.6, 6.05, 1.6 + sum(widths[:2]), 6.05, color=d.INK, width=0.75)
        for ri, row in enumerate(rows[1:]):
            y = 6.2 + ri * 4.8
            for ci, cell in enumerate(row):
                x = 1.6 + sum(widths[:ci])
                if mode == "tint":
                    d.box(s, x + 0.1, y, widths[ci] - 0.2, 4.3, fill=d.TINT if ci < 2 else "DCE6F0", line=None, radius=False)
                    col = [d.INK, d.MUTE, th["hl"]][ci]
                else:
                    if ci == 2:
                        d.box(s, x + 0.1, y, widths[ci] - 0.2, 4.3, fill=th["hl"], line=None, radius=False)
                    col = [d.INK, d.MUTE, "FFFFFF"][ci]
                d.text(s, x + 0.5, y, widths[ci] - 1.0, 4.3, cell.split("\n") if isinstance(cell, str) else cell,
                       size=19, color=col, bold=ci != 1, anchor="m", fit_check=False)
            if mode == "dark":
                d.line(s, 1.6, y + 4.55, 1.6 + sum(widths[:2]), y + 4.55, color=d.RULE)
    else:
        size = 21 if th["head"] > 24 else 19
        d.rule_table(s, 1.6, 5.4, widths, rows, [1.2, 4.4, 4.4], size=size, head_size=15, colors=[d.INK, d.MUTE, th["hl"]])
    d.text(s, 1.6, 17.55, 12, 0.6, [note], size=10, color="9AA3AE", fit_check=False)
    tag(d, s, style, {"tint": "底块对比", "dark": "反白对比"}.get(mode, "三线表对比"))


def page_method(d, th, c, style, note, flow):
    s = d.content(*c["part"])
    d.headline(s, c["head"])
    d.fig(s, flow, 1.6, 5.0, 14.0, 12.2, cap=f"图 {c['figure_title']}", align="c")
    x = 17.4
    mode = th["panels"]
    if mode == "tint":
        d.box(s, x - 0.4, 5.0, 15.2, 12.0, fill=d.TINT, line=None, radius=False)
    else:
        d.line(s, 16.6, 5.0, 16.6, 17.0, color=d.RULE)
    d.text(s, x, 5.3, 14, 0.7, ["判别准则"], size=14, color=d.MUTE, bold=True, fit_check=False)
    w, h = d.formula(s, x + 0.2, 6.2, c["latex"], size=22 if th["head"] > 24 else 20, max_w=14)
    pts = c["points"][:2] if th["head"] > 24 else c["points"]
    if mode == "dark":
        d.text(s, x, 7.0 + h, 14.2, 4.5, pts[:-1], size=th["body"], color=d.INK, bullet="·", spacing=1.25, space_after=10)
        d.box(s, x, 12.6, 14.8, 3.6, fill=th["hl"], line=None, radius=False)
        d.text(s, x + 0.6, 12.6, 13.6, 3.6, [pts[-1]], size=th["body"] + 1, color="FFFFFF", bold=True, anchor="m")
    else:
        d.text(s, x, 7.0 + h, 14.2, 7.5, pts, size=th["body"], color=d.INK, bullet="·", spacing=1.25, space_after=10)
    d.text(s, 1.6, 17.55, 12, 0.6, [note], size=10, color="9AA3AE", fit_check=False)
    tag(d, s, style, "图加公式")


def page_result(d, th, c, style, note, bar):
    s = d.content(*c["part"])
    d.headline(s, c["head"])
    mode = th["panels"]
    big = th["head"] > 24
    if mode == "dark":
        d.box(s, 1.6, 5.2, 15.6, 4.6, fill=th["hl"], line=None, radius=False)
    for i, (n, t) in enumerate(c["numbers"]):
        x = 1.6 + i * 5.2
        if mode == "tint":
            d.box(s, x, 5.2, 4.9, 4.6, fill=d.TINT, line=None, radius=False)
        if mode == "dark":
            col, lc = ("FFFFFF" if i == len(c["numbers"]) - 1 else "C9D3E0"), "C9D3E0"
        else:
            col, lc = (th["hl"] if i == len(c["numbers"]) - 1 else (d.MUTE if i == 0 else d.INK)), None
        d.big_number(s, x + 0.45, 5.6, 4.6, n, t, color=col, size=46 if big else 40, label_color=lc)
    if mode == "none":
        d.line(s, 1.6, 10.4, 17.2, 10.4, color=d.RULE)
    d.text(s, 1.6, 10.8, 15.6, 3.6, [c["conclusion"]], size=24 if big else th["body"] + 1, color=d.INK, bold=True, spacing=1.2)
    d.fig(s, bar, 18.2, 5.0, 14.0, 11.6, cap=f"图 {c['bar_title']}", align="c")
    d.text(s, 1.6, 17.55, 12, 0.6, [note], size=10, color="9AA3AE", fit_check=False)
    tag(d, s, style, "大数字加图")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--styles", default="V3实例,学术极简,期刊黑白,浅色分区,深色重点,大字结论")
    ap.add_argument("--content", default=None)
    ap.add_argument("--template", default=None)
    ap.add_argument("--render", action="store_true")
    a = ap.parse_args()
    skill = Path(a.skill_dir)
    sys.path.insert(0, str(skill / "scripts"))
    from swust_kit import Deck, THEMES  # noqa
    content = runpy.run_path(a.content)["CONTENT"] if a.content else DEMO
    note = content.get("note", "")
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    flow = Path(content["method"]["figure"]) if content["method"].get("figure") else demo_figures(tmp)
    tpl = a.template or (skill / "assets" / "swust_proposal_template.pptx")
    made = []
    for style in a.styles.split(","):
        if THEMES[style].get("preset"):
            # 整套配方型风格: 用配方生成整套示例, 取有代表性的 4 页做样页
            preset = runpy.run_path(str(skill / THEMES[style]["preset"]))
            d = Deck(tpl)
            d.set_theme(style)
            p = out / f"风格样页_{style}.pptx"
            preset["build"](d, preset["DEMO"], p, preset["_Img"](tmp))
            made.append((style, p))
            print("saved", p, "|", THEMES[style]["desc"])
            continue
        d = Deck(tpl)
        th = d.set_theme(style)
        r = content["result"]
        bar = Path(r["figure"]) if r.get("figure") else bar_png(tmp, *r["bars"], th["hl"], style)
        page_evolution(d, th, content["evolution"], style, note)
        page_compare(d, th, content["compare"], style, note)
        page_method(d, th, content["method"], style, note, flow)
        page_result(d, th, r, style, note, bar)
        p = out / f"风格样页_{style}.pptx"
        d.save(p)
        made.append((style, p))
        print("saved", p, "|", THEMES[style]["desc"])
    if a.render:
        from PIL import Image
        for style, p in made:
            rd = tmp / style
            rd.mkdir()
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(rd), str(p)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            pdf = next(rd.glob("*.pdf"))
            subprocess.run(["pdftoppm", "-r", "60", "-png", str(pdf), str(rd / "p")], check=True)
            ims = [Image.open(x) for x in sorted(rd.glob("p-*.png"))]
            if THEMES[style].get("preset"):
                ims = [ims[i] for i in (2, 4, 9, 13)]  # 研究背景、现状演进、研究一二、研究基础
            w, h = ims[0].size
            g = Image.new("RGB", (w * 2 + 12, h * 2 + 12), "white")
            for j, im in enumerate(ims[:4]):
                g.paste(im, ((j % 2) * (w + 12), (j // 2) * (h + 12)))
            g.save(out / f"风格样页_{style}.png")
            print("rendered", out / f"风格样页_{style}.png")


if __name__ == "__main__":
    main()
