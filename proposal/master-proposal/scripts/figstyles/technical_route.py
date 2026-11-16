"""技术路线图（图3-1 类）的画法。每个函数接收内容字典，返回 figkit.Fig。

内容字典字段（见 assets/figure-gallery/technical-route/content-example.json）：
  problem 核心问题  goal 研究目标  feedback 反馈内容
  stages  研究阶段（3–5 个），每个：name 阶段名  content 研究内容名  methods 方法（2–3 条短语）
          output 阶段成果  time 时间段  verify 对应的验证内容（T4 用）
  spaces  空间分层（T3 用）：[{name, items:[...]}]，自上而下；space_links：[[上层序号, 下层序号, 向下标注, 向上标注], ...]
  milestones  里程碑（T5 用）：[{name, after: 第几个工作包之后}]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figkit import Fig  # noqa: E402
from figstyles.research_content import _banner, wrap, W  # noqa: E402


# T1 三栏式（学习模板：研究阶段｜研究内容与方法｜阶段成果）
def t1(C):
    st = C["stages"]
    n = len(st)
    f = Fig(W, 500)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    cx0, cw0 = 10, 92
    cx1, cw1 = 112, 330
    cx2, cw2 = 452, 128
    f.box(cx0, 48, cw0, 26, ["研究阶段"], fill="dblue", stroke="dblue", color="white", bold=True, size=12.5, rx=4)
    f.box(cx1, 48, cw1, 26, ["研究内容与方法"], fill="dblue", stroke="dblue", color="white", bold=True, size=12.5,
          rx=4)
    f.box(cx2, 48, cw2, 26, ["阶段成果"], fill="dblue", stroke="dblue", color="white", bold=True, size=12.5, rx=4)
    y, rh, g = 84, 74, 12
    for i, s in enumerate(st):
        f.box(cx0, y, cw0, rh, wrap(s["name"], 4), fill="lblue", stroke="blue", size=12.5, bold=True, color="dblue")
        f.box(cx1, y, cw1, rh, [], fill="white", stroke="blue", sw=1.4)
        f.text(cx1 + cw1 / 2, y + 15, s["content"], size=13, bold=True, color="blue", red=red)
        mw = (cw1 - 16 - 8 * (len(s["methods"]) - 1)) / len(s["methods"])
        for k, m in enumerate(s["methods"]):
            f.box(cx1 + 8 + k * (mw + 8), y + 30, mw, 36, wrap(m, 8), fill="lorange", stroke="orange", sw=1.1,
                  size=11.5, rx=5)
        f.box(cx2, y, cw2, rh, wrap(s["output"], 8), fill="lgreen", stroke="green", size=12, bold=True,
              color="green")
        f.line([(cx1 + cw1, y + rh / 2), (cx2 - 1, y + rh / 2)], color="green", sw=1.4)
        if i < n - 1:
            for x in (cx0 + cw0 / 2, cx1 + cw1 / 2):
                f.line([(x, y + rh), (x, y + rh + g - 1)], color="dblue", sw=1.6)
        y += rh + g
    yl = y - g
    fx = cx2 + cw2 + 8
    f.line([(cx2 + cw2, yl - rh / 2), (fx, yl - rh / 2), (fx, 84 + rh / 2), (cx2 + cw2 + 1, 84 + rh / 2)],
           color="orange", sw=1.6, dash="5,3")
    f.text(fx + 7, (84 + yl) / 2, C.get("feedback_short", C["feedback"][:6]), size=10.5, bold=True, color="orange",
           vertical=True)
    _banner(f, yl + 10, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = yl + 52
    return f


# T2 竖向主干流程式（学习模板：开始 → 各步骤 → 结束，侧边虚框标外部对象，左侧括号标反馈）
def t2(C):
    st = C["stages"]
    f = Fig(W, 520)
    red = C.get("red", [])
    cx, bw, bh = 300, 230, 40
    f.box(cx - 40, 8, 80, 26, ["开始"], fill="white", stroke="dblue", sw=1.4, rx=13, size=12.5)
    y = 50
    ys = []
    for i, s in enumerate(st):
        f.box(cx - bw / 2, y, bw, bh, [s["content"]], fill="lblue", stroke="blue", sw=1.6, size=13, bold=True,
              color="dblue", red=red)
        f.line([(cx, y - 15), (cx, y - 1)], color="dblue", sw=1.5)
        ys.append(y)
        # 方法分支
        mw = 112
        f.box(cx + bw / 2 + 30, y + 2, mw + 30, bh - 4, wrap("、".join(s["methods"][:2]), 11), fill="white",
              stroke="gray", sw=1.0, dash="4,3", size=10.5, rx=4)
        f.line([(cx + bw / 2, y + bh / 2), (cx + bw / 2 + 29, y + bh / 2)], color="gray", sw=1.0)
        f.box(cx - bw / 2 - 140, y + 6, 118, bh - 12, [s["output"]], fill="lgreen", stroke="green", sw=1.0, rx=12,
              size=11, bold=True, color="green")
        f.line([(cx - bw / 2, y + bh / 2), (cx - bw / 2 - 21, y + bh / 2)], color="green", sw=1.2)
        y += bh + 30
    f.line([(cx, y - 30), (cx, y - 15)], color="dblue", sw=1.5)
    f.box(cx - 40, y - 14, 80, 26, ["结束"], fill="white", stroke="dblue", sw=1.4, rx=13, size=12.5)
    xb = cx - bw / 2 - 156
    f.line([(xb + 6, ys[-1] + bh / 2), (xb, ys[-1] + bh / 2), (xb, ys[0] + bh / 2), (xb + 6, ys[0] + bh / 2)],
           color="orange", sw=1.6)
    f.text(xb - 9, (ys[0] + ys[-1]) / 2 + bh / 2, C.get("feedback_short", C["feedback"][:8]), size=11, bold=True,
           color="orange", vertical=True)
    f.text(cx + bw / 2 + 75, 30, "主要方法", size=11, color="gray")
    f.text(cx - bw / 2 - 81, 30, "阶段成果", size=11, color="green")
    f.H = y + 22
    return f


# T3 空间分层式（学习模板：物理空间、孪生空间、算法层三条横带，带间写数据与指令）
def t3(C):
    sp = C["spaces"]
    f = Fig(W, 460)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    y, bh, g = 52, 82, 36
    cols = ["lorange", "lblue", "lgreen", "lgray"]
    strokes = ["orange", "blue", "green", "gray"]
    tops = []
    for i, s in enumerate(sp):
        f.box(10, y, W - 20, bh, [], fill="none", stroke=strokes[i % 4], sw=1.4, rx=8, dash="6,4")
        f.box(16, y + 8, 30, bh - 16, list(s["name"]), fill=cols[i % 4], stroke=strokes[i % 4], sw=1.2, rx=4,
              size=12, bold=True, gap=1.15)
        its = s["items"]
        iw = (W - 74 - 10 * (len(its) - 1)) / len(its)
        for k, t in enumerate(its):
            f.box(56 + k * (iw + 10), y + 18, iw, bh - 36, wrap(t, 8), fill="white", stroke=strokes[i % 4], sw=1.2,
                  size=11.5, red=red)
        tops.append(y)
        y += bh + g
    for a, b, down, up in C.get("space_links", []):
        ya, yb = tops[a] + bh, tops[b]
        f.line([(220, ya + 1), (220, yb - 1)], color="blue", sw=1.6)
        f.text(214, (ya + yb) / 2, down, size=11, bold=True, color="blue", anchor="end")
        f.line([(385, yb - 1), (385, ya + 1)], color="orange", sw=1.6)
        f.text(391, (ya + yb) / 2, up, size=11, bold=True, color="orange", anchor="start")
    yl = y - g
    _banner(f, yl + 10, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = yl + 52
    return f


# T4 V 模型（德国 VDI 2206 机电系统开发指南：左侧逐级分解设计，右侧逐级集成验证）
def t4(C):
    st = C["stages"]
    n = len(st)
    f = Fig(W, 420)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    bw, bh, dy = 168, 46, 66
    top = 74
    left = [(14 + i * 40, top + i * dy) for i in range(n - 1)]
    right = [(W - 14 - bw - i * 40, top + i * dy) for i in range(n - 1)]
    for i in range(n - 1):
        s = st[i]
        x, y = left[i]
        f.box(x, y, bw, bh, [s["content"], s["methods"][0]], fill="lblue", stroke="blue", sw=1.5, size=11.5,
              red=red)
        f.num(x + 2, y + 2, i + 1, r=9)
        xr, yr = right[i]
        f.box(xr, yr, bw, bh, wrap(s.get("verify", ""), 12), fill="lgreen", stroke="green", sw=1.5, size=11.5)
        f.line([(x + bw + 2, y + bh / 2), (xr - 2, yr + bh / 2)], color="gray", sw=1.0, dash="4,3", both=True)
        if i < n - 2:
            f.line([(x + 20, y + bh), (left[i + 1][0] + 20, left[i + 1][1] - 1)], color="blue", sw=1.6)
            f.line([(right[i + 1][0] + bw - 20, right[i + 1][1]), (xr + bw - 20, yr + bh + 1)], color="green", sw=1.6)
    s = st[-1]
    bx = (W - 220) / 2
    by = top + (n - 1) * dy
    f.box(bx, by, 220, bh, [s["content"], s["methods"][0]], fill="lorange", stroke="orange", sw=1.6, size=11.5,
          red=red)
    f.num(bx + 2, by + 2, n, r=9)
    lx, ly = left[-1]
    rx, ry = right[-1]
    f.line([(lx + 20, ly + bh), (bx + 20, by - 1)], color="blue", sw=1.6)
    f.line([(bx + 200, by), (rx + bw - 20, ry + bh + 1)], color="green", sw=1.6)
    f.text(left[0][0] + 6, top - 12, "分解与设计", size=11.5, bold=True, color="blue", anchor="start")
    f.text(right[0][0] + bw - 6, top - 12, "集成与验证", size=11.5, bold=True, color="green", anchor="end")
    f.text(W / 2, top - 12, "虚线：右侧验证对应左侧设计", size=10.5, color="gray")
    gy = by + bh + 16
    _banner(f, gy, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = gy + 42
    return f


# T5 工作包与里程碑式（欧洲科研项目和博士研究计划常用的工作包结构，带时间轴和里程碑）
def t5(C):
    st = C["stages"]
    n = len(st)
    f = Fig(W, 400)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    x0, x1 = 112, W - 14
    f.line([(x0, 300), (x1, 300)], color="gray", sw=1.4)
    f.text(56, 300, "时间", size=11.5, bold=True, color="gray")
    seg = (x1 - x0) / n
    for i, s in enumerate(st):
        y = 56 + i * 58
        f.box(10, y, 96, 44, [f"WP{i + 1}", s["name"]], fill="dblue", stroke="dblue", color="white", size=11.5,
              bold=True, rx=5, gap=1.25)
        xs = x0 + i * seg * 0.9
        w = seg * 1.25
        f.box(xs, y + 2, min(w, x1 - xs), 40, [s["content"], "成果：" + s["output"]], fill="lblue", stroke="blue",
              sw=1.4, size=11, red=red, rx=5, gap=1.3)
        f.text(xs + 4, y + 50, s.get("time", ""), size=10, color="gray", anchor="start")
        if i < n - 1:
            nx = x0 + (i + 1) * seg * 0.9
            f.line([(nx + 10, y + 40), (nx + 10, y + 61)], color="blue", sw=1.4)
    for m in C.get("milestones", []):
        mx = x0 + m["after"] * seg * 0.9 + (seg * 0.35 if m["after"] else 0)
        f.circle(mx, 300, 6, fill="orange", stroke="white")
        f.text(mx, 316, m["name"], size=11, bold=True, color="orange")
    _banner(f, 332, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = 374
    return f


STYLES = {
    "T1": ("三栏式", t1), "T2": ("竖向主干流程式", t2), "T3": ("空间分层式", t3), "T4": ("V模型", t4),
    "T5": ("工作包与里程碑式", t5),
}
