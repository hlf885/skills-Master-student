"""算法流程图（如图3-4、图3-5）的画法。每个函数接收内容字典，返回 figkit.Fig。

内容字典字段（见 assets/figure-gallery/flowchart/content-example.json）：
  steps     顺序步骤（F1）：每项为字符串，或判断 {"cond": 条件, "loop_to": 回到第几步(从0计), "yes": "是", "no": "否"}
  offline / online  离线、在线两段步骤（F2），store 为两段之间共享的离线结果
  lanes     泳道名称（F3）；flow：[[泳道序号, 步骤文字], ...] 按执行顺序
  pipeline  数据流水线（F4）：[{"kind": "data"|"proc", "t": 文字}, ...]
  control   控制框图（F5）：{ref, forward:[...], output, feedback:[...], disturbance}
  funnel    逐级筛选（F6）：[{"t": 检查名称, "n": 剩余数量}, ...]，result 为最终输出
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figkit import Fig  # noqa: E402
from figstyles.research_content import wrap, W  # noqa: E402


def _diamond(f, cx, cy, w, h, t, size=11.5):
    # 用折线画菱形（Visio 宏中同样是折线），文字放中间
    f.line([(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy), (cx, cy - h / 2)], color="orange",
           sw=1.6, arrow=False)
    f.lines(cx, cy, wrap(t, 7), size=size, color="black")


# F1 标准程序流程图（学习模板：开始、处理框、判断菱形、循环、结束，符号同 GB/T 1526、ISO 5807）
def f1(C):
    S = C["steps"]
    f = Fig(W, 600)
    cx, bw, bh, g = 260, 220, 36, 22
    f.box(cx - 45, 8, 90, 28, ["开始"], fill="white", stroke="dblue", sw=1.5, rx=14, size=12.5)
    y = 36 + g
    centers = []
    prev = 36
    for i, s in enumerate(S):
        if isinstance(s, dict):
            h = 64
            f.line([(cx, prev), (cx, y - 1)], color="dblue", sw=1.5)
            _diamond(f, cx, y + h / 2, 200, h, s["cond"])
            centers.append((y, h, True))
            j = s["loop_to"]
            ty = centers[j][0] + centers[j][1] / 2
            xr = cx + 170
            f.line([(cx + 100, y + h / 2), (xr, y + h / 2), (xr, ty), (cx + bw / 2 + 1, ty)], color="orange", sw=1.5)
            f.text(cx + 104, y + h / 2 + 11, s.get("no", "否"), size=11, bold=True, color="orange", anchor="start")
            f.text(cx + 8, y + h + 9, s.get("yes", "是"), size=11, bold=True, color="green", anchor="start")
            prev = y + h
            y += h + g
        else:
            f.line([(cx, prev), (cx, y - 1)], color="dblue", sw=1.5)
            f.box(cx - bw / 2, y, bw, bh, wrap(s, 15), fill="lblue", stroke="blue", sw=1.5, size=12, rx=4)
            centers.append((y, bh, False))
            prev = y + bh
            y += bh + g
    f.line([(cx, prev), (cx, y - 1)], color="dblue", sw=1.5)
    f.box(cx - 45, y, 90, 28, ["结束"], fill="white", stroke="dblue", sw=1.5, rx=14, size=12.5)
    f.H = y + 38
    return f


# F2 离线—在线分区式（离线预计算一次，在线查询与检查，中间是离线结果库）
def f2(C):
    off, on = C["offline"], C["online"]
    f = Fig(W, 460)
    lx, rx, bw = 14, 330, 260
    f.box(lx - 4, 8, bw + 8, 400, [], fill="none", stroke="gray", sw=1.3, rx=10, dash="6,4")
    f.text(lx + bw / 2, 24, "离线阶段（每类任务计算一次）", size=12.5, bold=True, color="gray")
    f.box(rx - 4, 8, bw + 8, 400, [], fill="none", stroke="blue", sw=1.3, rx=10, dash="6,4")
    f.text(rx + bw / 2, 24, "在线阶段（每次任务或场景变化时）", size=12.5, bold=True, color="blue")
    bh, g = 40, 22
    y = 44
    for i, s in enumerate(off):
        f.box(lx + 20, y, bw - 40, bh, wrap(s, 13), fill="lgray", stroke="gray", sw=1.4, size=11.5, rx=5)
        if i:
            f.line([(lx + bw / 2, y - g), (lx + bw / 2, y - 1)], color="gray", sw=1.4)
        y += bh + g
    sy = y + 6
    f.box(lx + 30, sy, bw - 60, 44, [C["store"]], fill="lgreen", stroke="green", sw=1.8, size=12, bold=True,
          color="green", rx=22)
    f.line([(lx + bw / 2, y - g), (lx + bw / 2, sy - 1)], color="gray", sw=1.4)
    y = 44
    ys = []
    for i, s in enumerate(on):
        f.box(rx + 20, y, bw - 40, bh, wrap(s, 13), fill="lblue", stroke="blue", sw=1.4, size=11.5, rx=5)
        ys.append(y)
        if i:
            f.line([(rx + bw / 2, y - g), (rx + bw / 2, y - 1)], color="blue", sw=1.4)
        y += bh + g
    k = min(C.get("query_step", 1), len(on) - 1)
    f.line([(lx + bw - 30, sy + 22), (rx + 6, sy + 22), (rx + 6, ys[k] + bh / 2), (rx + 19, ys[k] + bh / 2)],
           color="green", sw=1.6)
    f.text((lx + bw + rx) / 2 - 4, sy + 12, "在线调用", size=11, bold=True, color="green")
    if C.get("update"):
        yl = ys[-1] + bh / 2
        f.line([(rx + bw - 20, yl), (rx + bw - 6, yl), (rx + bw - 6, ys[1] + bh / 2), (rx + bw - 19, ys[1] + bh / 2)],
               color="orange", sw=1.5)
        f.text(rx + bw / 2, ys[-1] + bh + 14, "（" + C["update"] + "）", size=10.5, bold=True, color="orange")
    f.H = 418
    return f


# F3 泳道式（BPMN 与 UML 活动图的泳道画法：按执行者或模块分道，箭头跨道表示交接）
def f3(C):
    lanes, flow = C["lanes"], C["flow"]
    n = len(lanes)
    f = Fig(W, 420)
    lh = 92
    for i, nm in enumerate(lanes):
        y = 8 + i * lh
        f.box(10, y, W - 20, lh, [], fill="lgray" if i % 2 else "white", stroke="gray", sw=1.0, rx=0)
        f.box(10, y, 30, lh, list(nm), fill="lblue", stroke="gray", sw=1.0, rx=0, size=12, bold=True, color="dblue",
              gap=1.15)
    m = len(flow)
    step = (W - 70) / m
    bw, bh = min(step - 16, 96), 46
    prev = None
    for k, (li, t) in enumerate(flow):
        x = 48 + k * step + (step - bw) / 2
        y = 8 + li * lh + (lh - bh) / 2
        f.box(x, y, bw, bh, wrap(t, 6), fill="white", stroke="blue", sw=1.4, size=11, rx=5)
        if prev:
            px, py = prev
            if abs(py - y) < 1:
                f.line([(px + bw, py + bh / 2), (x - 1, y + bh / 2)], color="dblue", sw=1.4)
            else:
                mx = x - 8
                f.line([(px + bw, py + bh / 2), (mx, py + bh / 2), (mx, y + bh / 2), (x - 1, y + bh / 2)],
                       color="orange" if y < py else "dblue", sw=1.4)
        prev = (x, y)
    f.H = 8 + n * lh + 10
    return f


# F4 数据流水线式（学习模板中网络结构图的画法：数据与处理交替，从左到右）
def f4(C):
    P = C["pipeline"]
    f = Fig(W, 200)
    n = len(P)
    g = 18
    bw = (W - 20 - g * (n - 1)) / n
    for k, it in enumerate(P):
        x = 10 + k * (bw + g)
        if it["kind"] == "data":
            f.box(x, 60, bw, 60, wrap(it["t"], 4), fill="lgreen", stroke="green", sw=1.4, size=11.5, rx=14)
        else:
            f.box(x, 50, bw, 80, wrap(it["t"], 4), fill="lblue", stroke="blue", sw=1.8, size=12, bold=True, rx=4)
        if k:
            f.line([(x - g + 1, 90), (x - 1, 90)], color="dblue", sw=1.6)
    f.box(10, 150, 80, 22, ["数据"], fill="lgreen", stroke="green", sw=1.2, rx=11, size=11)
    f.box(100, 150, 80, 22, ["处理"], fill="lblue", stroke="blue", sw=1.4, rx=4, size=11)
    f.H = 182
    return f


# F5 控制框图式（学习模板中视觉伺服流程图的画法：求和点、前向通道、反馈通道）
def f5(C):
    K = C["control"]
    f = Fig(W, 230)
    y = 80
    f.text(40, y - 14, K["ref"], size=11.5, bold=True, color="dblue")
    f.line([(10, y), (82, y)], color="dblue", sw=1.6)
    f.circle(94, y, 12, fill="white", stroke="dblue", sw=1.6)
    f.text(94, y, "+", size=12, bold=True, color="dblue")
    fw = K["forward"]
    n = len(fw)
    x0, x1 = 130, W - 90
    bw = (x1 - x0 - 30 * (n - 1)) / n
    f.line([(106, y), (x0 - 1, y)], color="dblue", sw=1.6)
    for k, t in enumerate(fw):
        x = x0 + k * (bw + 30)
        f.box(x, y - 22, bw, 44, wrap(t, 6), fill="lblue", stroke="blue", sw=1.6, size=11.5, rx=4)
        if k:
            f.line([(x - 29, y), (x - 1, y)], color="dblue", sw=1.6)
    f.line([(x1, y), (W - 10, y)], color="dblue", sw=1.6)
    f.text(W - 50, y - 14, K["output"], size=11.5, bold=True, color="dblue")
    fx = x1 + 30
    fb = K["feedback"]
    m = len(fb)
    bw2 = 120
    xs = [fx - (k + 1) * (bw2 + 40) for k in range(m)]
    f.line([(fx, y), (fx, 170), (xs[0] + bw2 + 1, 170)], color="orange", sw=1.6)
    for k, t in enumerate(fb):
        x = xs[k]
        f.box(x, 148, bw2, 44, wrap(t, 7), fill="lorange", stroke="orange", sw=1.6, size=11.5, rx=4)
        if k < m - 1:
            f.line([(x, 170), (xs[k + 1] + bw2 + 1, 170)], color="orange", sw=1.6)
    f.line([(xs[-1], 170), (94, 170), (94, y + 13)], color="orange", sw=1.6)
    f.text(84, y + 26, "−", size=13, bold=True, color="orange")
    if K.get("disturbance"):
        dx = x0 + (n - 1) * (bw + 30) + bw / 2
        f.text(dx, 22, K["disturbance"], size=11, color="gray")
        f.line([(dx, 32), (dx, y - 23)], color="gray", sw=1.2, dash="4,3")
    f.H = 210
    return f


# F6 逐级筛选漏斗式（由粗到细：代价低的检查在前，代价高的检查在后，每级标剩余数量）
def f6(C):
    L = C["funnel"]
    n = len(L)
    f = Fig(W, 420)
    top_w, bot_w = W - 150, 170
    h, g = 50, 10
    for k, it in enumerate(L):
        w = top_w - (top_w - bot_w) * k / max(n - 1, 1)
        x = (W - w) / 2
        y = 10 + k * (h + g)
        fill = ["lgray", "lblue", "lblue", "lgreen", "lgreen"][min(k, 4)]
        f.box(x, y, w, h, [it["t"]], fill=fill, stroke="blue" if k else "gray", sw=1.6, size=12.5, bold=(k == n - 1),
              rx=6)
        f.box(x + w + 8 if x + w + 70 < W else x - 70, y + 12, 62, 26, [it["n"]], fill="white", stroke="orange",
              sw=1.2, size=12, bold=True, color="orange", rx=13)
        if k < n - 1:
            f.line([(W / 2, y + h), (W / 2, y + h + g - 1)], color="dblue", sw=1.6)
    yb = 10 + n * (h + g)
    if C.get("result"):
        f.line([(W / 2, yb - g), (W / 2, yb + 8)], color="green", sw=1.8)
        f.box(W / 2 - 120, yb + 9, 240, 38, [C["result"]], fill="lgreen", stroke="green", sw=1.8, size=12.5, bold=True,
              color="green", rx=19)
        yb += 52
    if C.get("cost_note"):
        f.text(W / 2, yb + 6, C["cost_note"], size=10.5, color="gray")
        yb += 16
    f.H = yb + 6
    return f


STYLES = {
    "F1": ("标准程序流程图", f1), "F2": ("离线在线分区式", f2), "F3": ("泳道式", f3), "F4": ("数据流水线式", f4),
    "F5": ("控制框图式", f5), "F6": ("逐级筛选漏斗式", f6),
}
