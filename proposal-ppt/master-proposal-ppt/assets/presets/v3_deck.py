#!/usr/bin/env python3
"""V3实例 风格: 一套用户反馈很好的完整开题答辩做法 (17 页, 8 到 10 分钟)。

它在 学术极简 规则之上, 把每一页用什么版式、元素放在哪里都定好了:
  3 研究背景      图墙加因果            4 研究对象      图加流程加四列难点
  5 现状一        演进图示              6 现状二        三线表加右侧小图与尚缺
  7 研究内容      整页大图              8 目标与问题    左右分栏细线
  9 技术路线      左图右步骤            10 研究一二     两图并排加公式
  11 研究三四     左图右两段公式        12 可行性       左三行右图
  13 创新点       三线表对比            14 研究基础     左图右大数字
  15 个人成果留白                       16 研究计划     三线表
用户选了 V3实例 后, 复制本文件, 把 DEMO 换成开题报告里的内容和图片路径即可; 页数或内容
不同时, 删改对应的页函数, 但保持相邻两页版式不同。

用法: python3 v3_deck.py <Skill目录> [输出.pptx] [--content my_v3_content.py]
    --content 指向定义了 CONTENT 字典 (结构同 DEMO) 的 python 文件。
"""
import runpy
import sys
import tempfile
from pathlib import Path

# ------------------------------------------------------------------ 示例内容 (虚构课题, 只演示版式)
DEMO = {
    "title": "基于视觉的焊缝缺陷自适应检测方法研究（示例）",
    "school": "西南科技大学硕士",
    "year": 2026,
    "date": "2026年11月",
    "note": "示例内容，虚构课题，仅演示版式",
    "background": {
        "head": "焊缝缺陷检测量大、工况多，人工评片难以满足批量复核要求",
        "figs": [("img", "图 示例：焊接产线"), ("img", "图 示例：焊缝外观"), ("img", "图 示例：射线底片评片"), ("img", "图 示例：在线检测装置")],
        "chain": [("产量提高、工况增多", "焊缝数量和类型增加"), ("人工评片因人而异", "效率低，难以批量复核"), ("需要自动检测", "并能随工况调整判据")],
        "credit": "实拍图来源：作者，许可（示例）",
        "say": "（讲稿：背景三句话，由产量和工况变化引出自动检测的需求，约 40 秒。）",
        "ref": "可能的追问\n问：……\n答：……（只用开题报告里的内容）",
    },
    "object": {
        "head": "本课题聚焦判别环节：换了工况，缺陷判据怎么跟着变",
        "figs": [("img", "图 示例：检测对象"), ("img", "图 示例：采集装置")],
        "flow_title": "检测流程",
        "flow": [("采集", "相机采集焊缝图像"), ("判别", "提取候选缺陷并判别"), ("复核", "人工复核可疑样本"), ("归档", "结果入库")],
        "flow_hl": 1,
        "scope": "本课题研究范围",
        "diffs": [("背景干扰", "焊缝纹理与缺陷相似"), ("样本不均", "缺陷样本远少于正常"), ("工况多变", "材料、光照随产线变化"), ("判据固定", "换工况需人工重调")],
        "define": "__自适应判别__　按工况估计判别阈值，新样本到来时增量更新",
        "say": "（讲稿：对象、流程、四个难点，约 50 秒。）",
    },
    "status1": {
        "head": "已有检测多依赖人工设定阈值，缺少能随工况自适应的检测方法",
        "stages": [("人工目检与抽检", "依赖经验，效率低", ["射线底片人工评片", "超声信号人工判读"]),
                   ("传统图像处理", "阈值与特征人工设定", ["边缘检测与形态学", "纹理特征加分类器"]),
                   ("按工况自适应检测", "判据随工况更新", ["本课题切入点"])],
        "gaps": ["评片结果因人而异，难以批量复核", "阈值换一种工况就要重新调", "工况变化后如何更新判据讨论少"],
        "foot": "代表工作详见开题报告 1.2 节",
        "say": "（讲稿：三个阶段与对应空白，约 50 秒。）",
    },
    "status2": {
        "head": "现有方法多在固定工况下评价，换工况后的判据更新讨论少",
        "rows": [["研究方向", "代表方法", "特点"],
                 ["缺陷检测", "阈值分割与形态学", "简单，依赖人工阈值"], ["", "特征提取加分类器", "需人工设计特征"], ["", "深度检测网络", "精度高，需大量标注"],
                 ["工况适应", "数据增强", "扩充样本，不改判据"], ["", "迁移学习", "需重新训练"], ["", "在线更新", "前提是新样本可靠"]],
        "figs": [("img", "方法示意一"), ("img", "方法示意二")],
        "gaps": ["多在固定工况下评价，换工况效果下降", "判据更新多靠重新训练，代价大"],
        "ours": "本课题：先定位焊缝区域，再按工况估计阈值，新样本到来时增量更新",
        "say": "（讲稿：两个方向的方法与局限，约 40 秒。）",
    },
    "content": {
        "head": "三项研究内容依次回答：缺陷在哪、怎么判、换了工况怎么办",
        "fig": ("flow", "研究内容框图"),
        "say": "（讲稿：逐项讲研究内容及衔接，约 40 秒。）",
    },
    "goals": {
        "head": "研究目标给出可检验的指标，三个关键问题对应三项技术难点",
        "goals": [("区域定位", "焊缝区域定位准确率__不低于 95%__"), ("候选提取", "候选召回率__高于常用方法__"),
                  ("自适应判别", "新工况漏检率__低于固定阈值方法__"), ("验证与成果", "完成产线数据验证，形成软件模块")],
        "keys": ["焊缝纹理背景下候选缺陷的可靠提取", "少样本条件下判别阈值的估计", "工况变化后判据的增量更新"],
        "say": "（讲稿：目标与关键问题，约 45 秒。）",
    },
    "route": {
        "head": "先定位、再提取、后判别，判据按工况估计并增量更新",
        "fig": ("flow", "技术路线"),
        "idea": ["缺陷检测 = 区域定位 + 候选提取 + 自适应判别", "判据随工况估计，新样本到来时增量更新"],
        "steps": ["采集多工况焊缝图像，建立数据集", "定位焊缝区域，提取候选缺陷", "按工况估计阈值，完成判别", "产线数据验证，对比与消融"],
        "say": "（讲稿：技术路线四步，约 35 秒。）",
    },
    "method12": {
        "subtitle": "研究一：区域定位　研究二：候选提取",
        "head": "先把搜索范围缩到焊缝区域，再在区域内提取候选缺陷",
        "figs": [("flow", "图 研究一流程"), ("flow", "图 研究二流程")],
        "formulas": [(r"R^{*}=\arg\max_{R}\ S(R)", "(3-1)", ["S(R) 为区域 R 的焊缝得分", "__只在焊缝区域内搜索，减少背景干扰__"]),
                     (r"s(x)=\sigma\!\left(w^{\top}\phi(x)\right)", "(3-2)", ["φ(x) 为候选区域特征，w 为判别权重"])],
        "say": "（讲稿：口语解释两项研究，不念符号，约 50 秒。）",
        "ref": "公式详解\n【式 3-1】每个符号的含义；为什么这样设计；取值怎么定。\n可能的追问\n问：……\n答：……",
    },
    "method34": {
        "subtitle": "研究三：自适应判别　实验验证",
        "head": "判据按工况估计并增量更新，用新工况漏检率检验",
        "fig": ("flow", "图 研究三流程"),
        "parts": [("研究三　自适应判别", r"\tau_c=\bar{s}_c-k\,\sigma_c", "(3-3)", ["阈值按工况的得分均值和标准差估计", "新样本到来时只更新该工况的阈值"]),
                  ("实验验证", r"\eta=\frac{N_{\mathrm{miss}}}{N}\times 100\%", "(3-4)", ["与常用方法对比，做消融实验", "在产线数据上验证"])],
        "say": "（讲稿：研究三与实验方案，约 45 秒。）",
        "ref": "公式详解\n【式 3-3】……\n可能的追问\n问：……\n答：……",
    },
    "feasible": {
        "head": "方法基础成熟，已有数据与采集条件",
        "rows": [("理论基础", "图像处理与模式识别方法成熟"), ("技术储备", "熟悉常用视觉库与深度学习框架"), ("研究条件", "合作单位提供产线数据与采集装置")],
        "fig": ("img", "图 示例：前期试验"),
        "say": "（讲稿：可行性三方面，约 35 秒。）",
    },
    "innovation": {
        "head": "两点创新分别解决：缺陷找得准不准，以及换了工况判据怎么更新",
        "rows": [["创新点", "已有方法", "本课题"],
                 [["1　焊缝区域约束的", "　 候选缺陷提取方法"], "全图搜索\n背景纹理干扰大", "先定位焊缝区域\n只在区域内提取候选"],
                 [["2　工况自适应的", "　 缺陷判别方法"], "固定阈值\n换工况需人工重调", "按工况估计阈值\n新样本到来增量更新"]],
        "foot": "创新点 1 对应研究内容（2），创新点 2 对应研究内容（3）",
        "say": "（讲稿：两点创新，约 35 秒。）",
    },
    "basis": {
        "subtitle": "研究基础：前期试验",
        "head": "固定阈值在新工况下漏检 18 张，判据需要随工况调整",
        "fig": ("bars", "图 各工况漏检张数"),
        "done": ["采集三种工况焊缝图像 120 张", "实现区域定位与候选提取", "完成固定阈值方法的对比试验"],
        "scan": "试验　3 种工况 × 40 张 = 120 张",
        "numbers": [("120", "测试样本"), ("18", "固定阈值漏检"), ("15%", "漏检比例")],
        "conclusion": "换到新工况后，原阈值漏检约 15%",
        "limit": "基于小样本，只用于说明问题存在",
        "say": "（讲稿：前期工作与结果，约 35 秒。）",
    },
    "plan": {
        "head": "按三项研究内容分阶段推进，2027 年底完成中期考核",
        "rows": [["时间", "研究内容", "预期效果"],
                 ["2026.10 至 2026.11", "文献调研，完成开题报告", "通过开题答辩"],
                 ["2026.12 至 2027.03", "研究内容（1）", "完成算法与仿真验证"],
                 ["2027.04 至 2027.08", "研究内容（2）", "完成算法与仿真验证"],
                 ["2027.09 至 2027.12", "研究内容（3）", "通过中期考核"],
                 ["2028.01 至 2028.03", "产线验证，撰写论文", "完成学位论文初稿"],
                 ["2028.04 至 2028.06", "修改完善学位论文", "通过毕业答辩"]],
        "say": "（讲稿：研究计划，约 15 秒。）",
    },
}


# ------------------------------------------------------------------ 示例图 (真实使用时换成开题报告里的图片路径)
def _demo_fig(kind, tmp, idx, color="274F7F"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    names = {x.name for x in font_manager.fontManager.ttflist}
    for f in ("Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", "SimHei", "WenQuanYi Micro Hei"):
        if f in names:
            plt.rcParams["font.family"] = f
            break
    out = tmp / f"demo_{kind}_{idx}.png"
    if kind == "bars":
        fig, ax = plt.subplots(figsize=(5.2, 3.8), dpi=200)
        vals = [3, 18, 11]
        ax.bar(["工况 A", "工况 B", "工况 C"], vals, color=[f"#{color}" if v == max(vals) else "#C8D0DB" for v in vals], width=0.55)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.6, str(v), ha="center", fontsize=13)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(left=False, labelleft=False, labelsize=13)
    elif kind == "flow":
        fig, ax = plt.subplots(figsize=(6, 4.6), dpi=200)
        ax.axis("off")
        boxes = ["输入", "步骤一", "步骤二", "步骤三", "输出"]
        for i, b in enumerate(boxes):
            y = 0.9 - i * 0.2
            ax.add_patch(plt.Rectangle((0.25, y - 0.06), 0.5, 0.12, fill=False, ec="#4B5563", lw=1.2))
            ax.text(0.5, y, b, ha="center", va="center", fontsize=13, color="#1F2933")
            if i < len(boxes) - 1:
                ax.annotate("", xy=(0.5, y - 0.14), xytext=(0.5, y - 0.065), arrowprops=dict(arrowstyle="->", color="#6B7280"))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    else:
        fig, ax = plt.subplots(figsize=(4.8, 3.4), dpi=200)
        ax.set_facecolor("#E6EBF1")
        ax.text(0.5, 0.5, "示例图片", ha="center", va="center", fontsize=16, color="#8A94A3", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
    fig.savefig(out, bbox_inches="tight", transparent=(kind != "img"))
    plt.close(fig)
    return out


class _Img:
    """把 ('img'|'flow'|'bars', 图注) 换成示例图; 若第一项是存在的文件路径则直接用。"""

    def __init__(self, tmp):
        self.tmp, self.n = tmp, 0

    def __call__(self, spec):
        kind, cap = spec
        self.n += 1
        if Path(kind).exists():
            return Path(kind), cap
        return _demo_fig(kind, self.tmp, self.n), cap


# ------------------------------------------------------------------ 逐页版式
def build(d, C, out, img):
    T, N, H, L = d.text, d.notes, d.headline, d.line
    X0, XW, Y0 = 1.6, 30.6, 5.0
    NAVY, INK, MUTE, RULE, ACC, TINT = d.NAVY_HEX, d.INK, d.MUTE, d.RULE, d.ACC, d.TINT

    def label(s, x, y, t, color=MUTE, w=12):
        T(s, x, y, w, 0.7, [t], size=14, color=color, bold=True, fit_check=False)

    def fig(s, spec, x, y, w, h, cap=True, **kw):
        p, c = img(spec)
        return d.fig(s, p, x, y, w, h, cap=c if cap else None, align="c", **kw)

    s = d.cover(C["year"], C["school"], C["title"], title_size=34)
    N(s, f"各位老师好，我是（姓名），指导老师是（导师姓名）老师。我的开题题目是《{C['title']}》。")
    s = d.toc()
    N(s, "下面我从立题依据、研究内容与目标、研究方案、创新点、研究基础与工作条件、研究计划六个方面汇报。")

    # 3 研究背景: 图墙加因果
    c = C["background"]
    s = d.content(1, "立题依据", "研究背景")
    H(s, c["head"])
    for i, sp in enumerate(c["figs"][:4]):
        fig(s, sp, X0 + (i % 2) * 10.0, Y0 + (i // 2) * 6.0, 9.6, 5.6 if i < 2 else 5.9)
    L(s, 22.3, Y0 + 0.2, 22.3, 16.6, color=RULE)
    for i, (a, b) in enumerate(c["chain"]):
        y = 5.6 + i * 3.7
        last = i == len(c["chain"]) - 1
        T(s, 23.0, y, 9.4, 1.0, [a], size=20, color=NAVY if last else INK, bold=True, fit_check=False)
        T(s, 23.0, y + 1.05, 9.4, 0.9, [b], size=17, color=MUTE, fit_check=False)
        if not last:
            T(s, 23.0, y + 2.05, 2.0, 1.2, ["↓"], size=22, color="9AA3AE", fit_check=False)
    T(s, X0, 17.45, XW, 0.5, [c["credit"]], size=8, color="9AA3AE", fit_check=False)
    N(s, c["say"], ref=c.get("ref"))

    # 4 研究对象: 图加流程加四列难点
    c = C["object"]
    s = d.content(1, "立题依据", "研究对象与问题提出")
    H(s, c["head"])
    fig(s, c["figs"][0], X0, Y0, 9.8, 6.9)
    fig(s, c["figs"][1], 11.8, Y0, 9.8, 6.9)
    label(s, 22.8, Y0, c["flow_title"])
    for i, (a, b) in enumerate(c["flow"]):
        y = Y0 + 0.9 + i * 1.5
        hl = i == c["flow_hl"]
        T(s, 22.8, y, 2.0, 1.0, [a], size=18, color=NAVY if hl else MUTE, bold=True, fit_check=False)
        T(s, 24.8, y, 7.6, 1.0, [b], size=16, color=INK if hl else MUTE, bold=hl, fit_check=False)
    T(s, 24.8, Y0 + 0.9 + c["flow_hl"] * 1.5 + 0.75, 7.6, 0.7, [c["scope"]], size=12, color=ACC, fit_check=False)
    L(s, X0, 12.65, X0 + XW, 12.65, color=RULE)
    for i, (t, e) in enumerate(c["diffs"]):
        x = X0 + i * 7.75
        T(s, x, 12.95, 7.2, 0.9, [t], size=19, color=INK, bold=True, fit_check=False)
        T(s, x, 13.9, 7.2, 1.5, [e], size=16, color=MUTE)
        if i:
            L(s, x - 0.3, 13.0, x - 0.3, 15.2, color=RULE)
    T(s, X0, 15.6, XW, 1.8, [c["define"]], size=17, color=INK)
    N(s, c["say"], ref=c.get("ref"))

    # 5 现状一: 演进图示
    c = C["status1"]
    s = d.content(1, "立题依据", "国内外研究现状")
    H(s, c["head"])
    n = len(c["stages"])
    for i, (a, b, ex) in enumerate(c["stages"]):
        hl = i == n - 1
        x = X0 + i * 10.5
        d.box(s, x, 5.4, 9.6, 4.8, fill=NAVY if hl else TINT, line=None, radius=False)
        T(s, x + 0.5, 5.75, 8.7, 1.2, [a], size=21, color="FFFFFF" if hl else INK, bold=True, fit_check=False)
        T(s, x + 0.5, 7.05, 8.7, 1.0, [b], size=17, color="DCE4EE" if hl else MUTE, fit_check=False)
        T(s, x + 0.5, 8.3, 8.7, 1.8, ex, size=15 if hl else 14, color="FFFFFF" if hl else MUTE, bold=hl, space_after=0, fit_check=False)
        if i < n - 1:
            T(s, x + 9.6, 6.9, 0.9, 1.4, ["›"], size=36, color="9AA3AE", align="c", anchor="m", fit_check=False)
    L(s, X0, 11.2, X0 + XW, 11.2, color=RULE)
    label(s, X0, 11.55, "尚缺", color=ACC)
    for i, g in enumerate(c["gaps"]):
        T(s, X0 + i * 10.5, 12.3, 9.6, 2.4, [g], size=18, color=INK)
    if c.get("foot"):
        T(s, X0, 15.6, XW, 1.0, [c["foot"]], size=13, color=MUTE, fit_check=False)
    N(s, c["say"], ref=c.get("ref"))

    # 6 现状二: 三线表加右侧小图与尚缺
    c = C["status2"]
    s = d.content(1, "立题依据", "国内外研究现状")
    H(s, c["head"])
    nr = len(c["rows"])
    d.rule_table(s, X0, Y0 + 0.1, [4.0, 10.6, 7.4], c["rows"], [1.0] + [min(1.45, 9.6 / (nr - 1))] * (nr - 1), size=17, head_size=14)
    fig(s, c["figs"][0], 24.6, Y0 + 0.1, 3.7, 4.1, cap_size=11)
    fig(s, c["figs"][1], 28.5, Y0 + 0.1, 3.7, 4.1, cap_size=11)
    label(s, 24.6, 9.7, "尚缺", color=ACC)
    T(s, 24.6, 10.4, 7.6, 5.3, c["gaps"], size=16, color=INK, bullet="·", spacing=1.2, space_after=6)
    L(s, X0, 15.75, X0 + XW, 15.75, color=RULE)
    T(s, X0, 16.0, XW, 1.0, [c["ours"]], size=18, color=NAVY, bold=True, fit_check=False)
    N(s, c["say"], ref=c.get("ref"))

    # 7 研究内容: 整页大图
    c = C["content"]
    s = d.content(2, "研究内容与目标", "研究内容")
    H(s, c["head"])
    fig(s, c["fig"], X0, Y0, XW, 12.6, cap=False)
    N(s, c["say"], ref=c.get("ref"))

    # 8 目标与关键问题: 左右分栏细线
    c = C["goals"]
    s = d.content(2, "研究内容与目标", "研究目标与拟解决的关键问题")
    H(s, c["head"])
    label(s, X0, Y0, "研究目标")
    for i, (t, e) in enumerate(c["goals"]):
        y = Y0 + 0.9 + i * 2.85
        if i:
            L(s, X0, y - 0.2, 16.2, y - 0.2, color=RULE)
        T(s, X0, y, 3.9, 2.4, [t], size=18, color=INK, bold=True, anchor="m", fit_check=False)
        T(s, 5.6, y, 10.6, 2.4, [e], size=18, color=INK, anchor="m")
    L(s, 17.1, Y0, 17.1, 17.0, color=RULE)
    label(s, 17.9, Y0, "拟解决的关键问题")
    for i, k in enumerate(c["keys"]):
        y = Y0 + 0.9 + i * 3.8
        if i:
            L(s, 17.9, y - 0.2, X0 + XW, y - 0.2, color=RULE)
        T(s, 17.9, y, 2.2, 3.3, [f"问题{i + 1}"], size=15, color=ACC, bold=True, anchor="m", fit_check=False)
        T(s, 20.2, y, 12.0, 3.3, [k], size=19, color=INK, bold=True, anchor="m")
    N(s, c["say"], ref=c.get("ref"))

    # 9 技术路线: 左图右步骤
    c = C["route"]
    s = d.content(3, "研究方案", "技术路线")
    H(s, c["head"])
    fig(s, c["fig"], X0, Y0, 15.6, 12.5, cap=False)
    L(s, 17.9, Y0, 17.9, 17.0, color=RULE)
    label(s, 18.6, Y0, "基本思路")
    T(s, 18.6, Y0 + 0.8, 13.6, 2.8, c["idea"], size=17, color=NAVY, bold=True, space_after=4)
    for i, t in enumerate(c["steps"]):
        y = 9.0 + i * 2.05
        L(s, 18.6, y - 0.25, X0 + XW, y - 0.25, color=RULE)
        T(s, 18.6, y, 1.2, 1.4, [str(i + 1)], size=24, color=NAVY, bold=True, anchor="m", fit_check=False)
        T(s, 19.9, y, 12.3, 1.4, [t], size=18, color=INK, anchor="m")
    N(s, c["say"], ref=c.get("ref"))

    # 10 研究一二: 两图并排加公式
    c = C["method12"]
    s = d.content(3, "研究方案", c["subtitle"])
    H(s, c["head"])
    fig(s, c["figs"][0], X0, Y0, 14.8, 8.2)
    fig(s, c["figs"][1], 17.4, Y0, 14.8, 8.2)
    L(s, 16.5, Y0, 16.5, 17.2, color=RULE)
    for k, (tex, lab, lines) in enumerate(c["formulas"][:2]):
        x = 2.0 if k == 0 else 17.8
        w, h = d.formula(s, x, 13.6, tex, size=20, label=lab)
        T(s, x - 0.4, 13.8 + h + 0.2, 14.6, 2.6, lines, size=16, color=INK, space_after=4)
    N(s, c["say"], ref=c.get("ref"))

    # 11 研究三四: 左图右两段公式
    c = C["method34"]
    s = d.content(3, "研究方案", c["subtitle"])
    H(s, c["head"])
    fig(s, c["fig"], X0, Y0, 14.4, 12.4)
    L(s, 16.6, Y0, 16.6, 17.2, color=RULE)
    XR, WR, y = 17.3, 14.9, Y0
    for k, (lab, tex, num, pts) in enumerate(c["parts"][:2]):
        if k:
            L(s, XR, y, XR + WR, y, color=RULE)
            y += 0.3
        label(s, XR, y, lab, w=WR)
        w, h = d.formula(s, XR + 0.2, y + 0.85, tex, size=18, max_w=13.0, label=num)
        y = y + 1.1 + h
        T(s, XR, y, WR, 3.4, pts, size=17, color=INK, bullet="·", spacing=1.15, space_after=4)
        y += 3.6
    N(s, c["say"], ref=c.get("ref"))

    # 12 可行性: 左三行右图
    c = C["feasible"]
    s = d.content(3, "研究方案", "可行性分析")
    H(s, c["head"])
    for i, (t, e) in enumerate(c["rows"]):
        y = Y0 + 0.4 + i * 4.0
        if i:
            L(s, X0, y - 0.3, 16.6, y - 0.3, color=RULE)
        T(s, X0, y, 3.6, 3.2, [t], size=19, color=NAVY, bold=True, anchor="m", fit_check=False)
        T(s, 5.4, y, 11.2, 3.2, [e], size=18, color=INK, anchor="m")
    fig(s, c["fig"], 17.8, Y0 + 1.8, 14.4, 10.5)
    N(s, c["say"], ref=c.get("ref"))

    # 13 创新点: 三线表对比
    c = C["innovation"]
    s = d.content(4, "创新点", "本课题可能的创新之处")
    H(s, c["head"])
    nr = len(c["rows"])
    d.rule_table(s, X0, Y0 + 0.3, [10.8, 9.8, 10.0], c["rows"], [1.2] + [min(4.3, 9.0 / (nr - 1))] * (nr - 1),
                 size=19, head_size=15, colors=[INK, MUTE, NAVY])
    if c.get("foot"):
        T(s, X0, 15.8, XW, 0.9, [c["foot"]], size=15, color=MUTE, fit_check=False)
    N(s, c["say"], ref=c.get("ref"))

    # 14 研究基础: 左图右大数字
    c = C["basis"]
    s = d.content(5, "研究基础与工作条件", c["subtitle"])
    H(s, c["head"])
    fig(s, c["fig"], X0, Y0, 14.6, 12.4)
    L(s, 16.9, Y0, 16.9, 17.2, color=RULE)
    label(s, 17.6, Y0, "已完成")
    T(s, 17.6, Y0 + 0.8, 14.6, 4.0, c["done"], size=17, color=INK, bullet="·", spacing=1.2, space_after=6)
    L(s, 17.6, 10.1, X0 + XW, 10.1, color=RULE)
    label(s, 17.6, 10.35, c["scan"], w=14.6)
    m = len(c["numbers"])
    for i, (num, t) in enumerate(c["numbers"]):
        d.big_number(s, 17.6 + i * 5.0, 11.2, 4.8, num, t, color=NAVY if i == m - 1 else (MUTE if i == 0 else INK), size=40)
    T(s, 17.6, 14.6, 14.6, 1.0, [c["conclusion"]], size=18, color=INK, bold=True, fit_check=False)
    T(s, 17.6, 15.6, 14.6, 1.0, [c["limit"]], size=13, color=MUTE, fit_check=False)
    N(s, c["say"], ref=c.get("ref"))

    # 15 个人成果留白
    s = d.blank_page(5, "研究基础与工作条件", "研究基础：个人成果")
    N(s, "（此页留白：粘贴个人成果后在这里补充讲稿，约 30 秒。）")

    # 16 研究计划: 三线表
    c = C["plan"]
    s = d.content(6, "研究计划", "学位论文工作计划")
    H(s, c["head"])
    nr = len(c["rows"])
    d.rule_table(s, X0, Y0 + 0.1, [6.2, 14.6, 9.8], c["rows"], [1.0] + [min(1.55, 11.0 / (nr - 1))] * (nr - 1),
                 size=17, head_size=14, first_bold=False)
    N(s, c["say"], ref=c.get("ref"))

    s = d.end(C["year"], C["school"], date=C["date"])
    N(s, "以上是我的开题汇报，请各位老师批评指正，谢谢。")
    d.save(out)
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    content = None
    if "--content" in argv:
        i = argv.index("--content")
        content = runpy.run_path(argv[i + 1])["CONTENT"]
        del argv[i:i + 2]
    skill = Path(argv[0]) if argv else Path(__file__).resolve().parents[2]
    out = Path(argv[1]) if len(argv) > 1 else Path("v3_deck_example.pptx")
    sys.path.insert(0, str(skill / "scripts"))
    from swust_kit import Deck  # noqa
    d = Deck(skill / "assets" / "swust_proposal_template.pptx")
    d.set_theme("V3实例")
    build(d, content or DEMO, out, _Img(Path(tempfile.mkdtemp())))
    print("saved", out)
    d.notes_report()
    return out


if __name__ == "__main__":
    main()
