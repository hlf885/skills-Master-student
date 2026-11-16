"""架构与框架图（如图3-3 系统或模型架构）的画法。每个函数接收内容字典，返回 figkit.Fig。

内容字典字段（见 assets/figure-gallery/architecture/content-example.json）：
  title    图的主题（可选，只用于 A2、A6 的中心）
  layers   分层（A1）：[{name, items:[...]}]，自上而下
  physical / virtual / data / service  四要素（A2、A3、A4）：{name, items:[...]}
  up / down  虚实之间的连接：up 为实体到虚拟（如状态数据），down 为虚拟到实体（如控制指令）
  comm      通信层名称（A4）
  nodes / edges  模块与数据流（A5）：nodes [{id, name, group}]，edges [[from, to, 标注]]，groups [{id, name}]
  loop      闭环自主架构（A6）：{monitor, analyze, plan, execute, knowledge, sensors, effectors}
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figkit import Fig  # noqa: E402
from figstyles.research_content import wrap, W  # noqa: E402

FILLS = ["lblue", "lgreen", "lorange", "lgray"]
STROKES = ["blue", "green", "orange", "gray"]


def _row(f, x, y, w, h, items, stroke, size=11.5, red=()):
    iw = (w - 8 * (len(items) - 1)) / len(items)
    for k, t in enumerate(items):
        f.box(x + k * (iw + 8), y, iw, h, wrap(t, 7), fill="white", stroke=stroke, sw=1.1, size=size, rx=5, red=red)


# A1 分层堆叠式（学习模板与作者图3-3：自上而下应用、模型、数据、物理，层间双向箭头）
def a1(C):
    L = C["layers"]
    f = Fig(W, 460)
    red = C.get("red", [])
    y, h, g = 8, 70, 26
    tops = []
    for i, lay in enumerate(L):
        col = i % 4
        f.box(10, y, W - 20, h, [], fill=FILLS[col], stroke=STROKES[col], sw=1.5, rx=8)
        f.box(18, y + 10, 34, h - 20, list(lay["name"]), fill="none", stroke="none", size=12.5, bold=True,
              color="dblue", gap=1.15)
        _row(f, 60, y + 14, W - 82, h - 28, lay["items"], STROKES[col], red=red)
        tops.append(y)
        y += h + g
    for i in range(len(L) - 1):
        ya, yb = tops[i] + h, tops[i + 1]
        f.line([(W / 2 - 40, yb - 1), (W / 2 - 40, ya + 1)], color="dblue", sw=1.6)
        f.line([(W / 2 + 40, ya + 1), (W / 2 + 40, yb - 1)], color="dblue", sw=1.6)
        lk = C.get("layer_links", [])
        if i < len(lk):
            f.text(W / 2 - 48, (ya + yb) / 2, lk[i][0], size=10.5, color="dblue", anchor="end")
            f.text(W / 2 + 48, (ya + yb) / 2, lk[i][1], size=10.5, color="dblue", anchor="start")
    f.H = y - g + 8
    return f


# A2 四要素环形（学习模板中的数字孪生五维模型画法：孪生数据居中，物理实体、虚拟模型、服务围绕，连接为双向箭头）
def a2(C):
    f = Fig(W, 430)
    cx, cy = W / 2, 210
    f.circle(cx, cy, 168, fill="none", stroke="lblue", sw=26)
    f.circle(cx, cy, 58, fill="lgreen", stroke="green", sw=1.8)
    f.lines(cx, cy - 10, wrap(C["data"]["name"], 4), size=14, bold=True, color="green")
    f.lines(cx, cy + 22, wrap("、".join(C["data"]["items"][:2]), 6), size=10.5, color="#262626")
    pos = [("physical", cx - 176, cy + 70, "orange", "lorange"), ("virtual", cx + 176, cy + 70, "blue", "lblue"),
           ("service", cx, cy - 150, "dblue", "white")]
    for key, x, y, st, fl in pos:
        d = C[key]
        bw, bh = 150, 86
        f.box(x - bw / 2, y - bh / 2, bw, bh, [], fill=fl, stroke=st, sw=1.8, rx=10)
        f.text(x, y - bh / 2 + 15, d["name"], size=13.5, bold=True, color=st)
        f.lines(x, y + 12, [wrap(t, 9)[0] for t in d["items"][:3]], size=11, color="#262626", gap=1.35)
        # 与中心的双向连接
        dx, dy = cx - x, cy - y
        import math
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        f.line([(x + ux * 58, y + uy * 50), (cx - ux * 62, cy - uy * 62)], color="gray", sw=1.6, both=True)
    f.line([(cx - 100, cy + 108), (cx + 100, cy + 108)], color="gray", sw=1.6, both=True)
    f.text(cx, cy + 122, C.get("up", "") + " / " + C.get("down", ""), size=11, color="gray")
    f.text(cx, 418, "（环带表示各要素之间的连接，中心为孪生数据）", size=10.5, color="gray")
    f.H = 430
    return f


# A3 虚实左右映射式（Grieves 提出的数字孪生三要素：物理实体、虚拟模型及二者之间的数据连接）
def a3(C):
    f = Fig(W, 330)
    red = C.get("red", [])
    bw, bh = 220, 230
    for x, key, st, fl in ((10, "physical", "orange", "lorange"), (W - 10 - bw, "virtual", "blue", "lblue")):
        d = C[key]
        f.box(x, 40, bw, bh, [], fill=fl, stroke=st, sw=1.8, rx=10)
        f.text(x + bw / 2, 22, d["name"], size=14, bold=True, color=st)
        for k, t in enumerate(d["items"][:5]):
            f.box(x + 14, 54 + k * 42, bw - 28, 32, [t], fill="white", stroke=st, sw=1.1, size=11.5, rx=5, red=red)
    mx0, mx1 = 10 + bw, W - 10 - bw
    f.line([(mx0 + 4, 110), (mx1 - 4, 110)], color="orange", sw=2.4)
    f.text((mx0 + mx1) / 2, 96, C.get("up", "状态数据"), size=12, bold=True, color="orange")
    f.line([(mx1 - 4, 200), (mx0 + 4, 200)], color="blue", sw=2.4)
    f.text((mx0 + mx1) / 2, 214, C.get("down", "控制指令"), size=12, bold=True, color="blue")
    if C.get("data"):
        d = C["data"]
        f.box(mx0 + 14, 130, mx1 - mx0 - 28, 50, wrap(d["name"] + "：" + "、".join(d["items"][:2]), 9),
              fill="lgreen", stroke="green", sw=1.4, size=11, rx=6)
    f.text(W / 2, 300, "（左为物理实体，右为虚拟模型，中间为双向数据连接）", size=10.5, color="gray")
    f.H = 320
    return f


# A4 上虚下实分区式（学习模板：上方为虚拟端软件模块，下方为实体端设备，中间为通信层）
def a4(C):
    f = Fig(W, 420)
    red = C.get("red", [])
    v, p = C["virtual"], C["physical"]
    f.box(10, 10, W - 20, 150, [], fill="lblue", stroke="blue", sw=1.6, rx=10, dash="6,4")
    f.text(24, 26, v["name"], size=13.5, bold=True, color="blue", anchor="start")
    its = v["items"]
    n = len(its)
    iw = (W - 60 - 10 * (n - 1)) / n
    for k, t in enumerate(its):
        f.box(30 + k * (iw + 10), 46, iw, 96, wrap(t, 6), fill="white", stroke="blue", sw=1.2, size=11.5, rx=6,
              red=red)
    f.box(150, 186, W - 300, 34, [C.get("comm", "通信层")], fill="lgreen", stroke="green", sw=1.6, size=12.5,
          bold=True, color="green", rx=17)
    f.box(10, 246, W - 20, 150, [], fill="lorange", stroke="orange", sw=1.6, rx=10, dash="6,4")
    f.text(24, 262, p["name"], size=13.5, bold=True, color="orange", anchor="start")
    its = p["items"]
    n = len(its)
    iw = (W - 60 - 10 * (n - 1)) / n
    for k, t in enumerate(its):
        f.box(30 + k * (iw + 10), 282, iw, 96, wrap(t, 6), fill="white", stroke="orange", sw=1.2, size=11.5, rx=6,
              red=red)
    for x, up in ((120, True), (W - 120, False)):
        if up:
            f.line([(x, 245), (x, 161)], color="orange", sw=1.8)
            f.text(x - 8, 203, C.get("up", ""), size=11, bold=True, color="orange", anchor="end")
        else:
            f.line([(x, 161), (x, 245)], color="blue", sw=1.8)
            f.text(x + 8, 203, C.get("down", ""), size=11, bold=True, color="blue", anchor="start")
    f.H = 404
    return f


# A5 模块与数据流式（机器人系统常用的模块框图：节点为模块，箭头上写传递的数据）
def a5(C):
    f = Fig(W, 380)
    red = C.get("red", [])
    groups = {g["id"]: g for g in C.get("groups", [])}
    cols = {}
    for nd in C["nodes"]:
        cols.setdefault(nd["group"], []).append(nd)
    gids = [g["id"] for g in C.get("groups", [])] or list(cols)
    ng = len(gids)
    G = 74
    gw = (W - 20 - G * (ng - 1)) / ng
    pos = {}
    for gi, gid in enumerate(gids):
        x = 10 + gi * (gw + G)
        f.box(x, 10, gw, 340, [], fill="none", stroke=STROKES[gi % 4], sw=1.3, rx=8, dash="5,4")
        f.text(x + gw / 2, 26, groups.get(gid, {}).get("name", gid), size=12.5, bold=True, color=STROKES[gi % 4])
        nds = cols.get(gid, [])
        bh = 52
        gap = (300 - len(nds) * bh) / (len(nds) + 1)
        for k, nd in enumerate(nds):
            y = 44 + gap + k * (bh + gap)
            f.box(x + 10, y, gw - 20, bh, wrap(nd["name"], 7), fill=FILLS[gi % 4], stroke=STROKES[gi % 4], sw=1.5,
                  size=12, bold=True, rx=6, red=red)
            pos[nd["id"]] = (x + 10, y, gw - 20, bh)
    # 同一目标的多条入线在目标边上错开
    inc = {}
    for a, b, lab in C["edges"]:
        inc.setdefault(b, []).append(a)
    for a, b, lab in C["edges"]:
        xa, ya, wa, ha = pos[a]
        xb, yb, wb, hb = pos[b]
        k, m = inc[b].index(a), len(inc[b])
        ty = yb + hb * (k + 1) / (m + 1)
        if xb > xa + wa:
            p0, p1 = (xa + wa, ya + ha / 2), (xb - 1, ty)
            mx = p1[0] - 12
            f.line([p0, (mx, p0[1]), (mx, p1[1]), p1], color="dblue", sw=1.4)
            f.text(p0[0] + 3, p0[1] - 8, lab, size=10, color="dblue", anchor="start")
        elif xb + wb < xa:
            p0, p1 = (xa, ya + ha * 0.75), (xb + wb + 1, ty)
            mx = p1[0] + 12
            f.line([p0, (mx, p0[1]), (mx, p1[1]), p1], color="orange", sw=1.4)
            f.text(p0[0] - 3, p0[1] + 9, lab, size=10, color="orange", anchor="end")
        else:
            p0, p1 = (xa + wa / 2, ya + ha), (xb + wb / 2, yb - 1)
            f.line([p0, p1], color="dblue", sw=1.4)
            f.text(p0[0] + 6, (p0[1] + p1[1]) / 2, lab, size=10, color="dblue", anchor="start")
    f.H = 360
    return f


# A6 闭环自主架构（IBM 自主计算提出的 MAPE-K 环：监测、分析、规划、执行围绕共享知识）
def a6(C):
    lp = C["loop"]
    f = Fig(W, 400)
    cx, cy = W / 2 + 20, 140
    bw, bh, dx, dy = 160, 56, 130, 80
    P = {"monitor": (cx - dx, cy - dy), "analyze": (cx + dx, cy - dy), "plan": (cx + dx, cy + dy),
         "execute": (cx - dx, cy + dy)}
    names = {"monitor": "监测", "analyze": "分析", "plan": "规划", "execute": "执行"}
    for key, (x, y) in P.items():
        f.box(x - bw / 2, y - bh / 2, bw, bh, [names[key], lp[key]], fill="lblue", stroke="blue", sw=1.8, rx=10,
              size=12)
    f.box(cx - 75, cy - 27, 150, 54, ["知识", lp["knowledge"]], fill="lgreen", stroke="green", sw=1.6, rx=27,
          size=11.5)
    f.line([(cx - dx + bw / 2, cy - dy), (cx + dx - bw / 2 - 1, cy - dy)], color="blue", sw=2)
    f.line([(cx + dx, cy - dy + bh / 2), (cx + dx, cy + dy - bh / 2 - 1)], color="blue", sw=2)
    f.line([(cx + dx - bw / 2, cy + dy), (cx - dx + bw / 2 + 1, cy + dy)], color="blue", sw=2)
    for (x, y) in P.values():
        sx = x + (bw / 2 if x < cx else -bw / 2) * 0.55
        sy = y + (bh / 2 if y < cy else -bh / 2)
        tx = cx + (-45 if x < cx else 45)
        ty = cy + (-27 if y < cy else 27)
        f.line([(sx, sy), (tx, ty)], color="green", sw=1.0, arrow=False, dash="3,3")
    py = cy + dy + bh / 2 + 44
    f.box(10, py, W - 20, 46, [C.get("physical", {}).get("name", "物理实体") + "：" + lp.get("sensors", "") + "（测量），"
                              + lp.get("effectors", "") + "（执行）"], fill="lorange", stroke="orange", sw=1.6, rx=8,
          size=12)
    lx = 22
    f.line([(lx, py - 1), (lx, cy - dy), (cx - dx - bw / 2 - 1, cy - dy)], color="orange", sw=1.8)
    f.text(lx + 10, cy, "测量数据", size=11, bold=True, color="orange", vertical=True)
    f.line([(cx - dx, cy + dy + bh / 2), (cx - dx, py - 1)], color="orange", sw=1.8)
    f.text(cx - dx + 8, cy + dy + bh / 2 + 22, "动作指令", size=11, bold=True, color="orange", anchor="start")
    f.H = py + 56
    return f


STYLES = {
    "A1": ("分层堆叠式", a1), "A2": ("四要素环形", a2), "A3": ("虚实左右映射式", a3), "A4": ("上虚下实分区式", a4),
    "A5": ("模块与数据流式", a5), "A6": ("闭环自主架构", a6),
}
