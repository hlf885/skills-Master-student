"""研究内容图（图2-1 类）的九种画法。每个函数接收内容字典，返回 figkit.Fig。

内容字典字段（见 assets/figure-gallery/research-content/content-example.json）：
  problem   核心问题（一句话）            goal      研究目标（一句话）
  core      核心对象或概念（2–6 字，R5、R6 圆心用）
  findings  发现的问题（2–3 条，R1 用）     key_problems  关键问题（2–3 条，R1 用）
  feedback  闭环反馈的内容（R2、R3、R5、R6、R8 用）
  scene     场景图路径（R7、R8 用），scene_marks: [[编号, x比例, y比例], ...] 标在场景图上的位置
  scene_caption 场景图下方的说明
  items     研究内容（3–4 项），每项字段：
      name 名称（≤8 字）  short 一句话（≤12 字）  output 产出（≤7 字）  concept 概念词（2–4 字）
      issue 存在问题（≤12 字）  method 关键方法（≤12 字）  result 预期结果（≤12 字）
      question 研究问题（≤22 字，R9 用）  chapter 对应章节名（R9 用）  kp 对应关键问题编号（可选）
  red       需要标红的重点词列表（可选）
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from figkit import Fig  # noqa: E402

W = 605


def wrap(t: str, n: int) -> list[str]:
    """按字数折行：先算需要几行，再平均分配每行字数，避免最后一行只剩一两个字，标点不放行首。"""
    import math
    if len(t) <= n:
        return [t]
    k = math.ceil(len(t) / n)
    per = math.ceil(len(t) / k)
    out, cur = [], ""
    for ch in t:
        if len(cur) >= per and ch not in "，。、；：）》”":
            out.append(cur)
            cur = ""
        cur += ch
    if cur:
        out.append(cur)
    return out


def fit(text: str, width: float, size: float, min_size: float = 11) -> float:
    """一行放不下时缩小字号，最小 min_size。"""
    need = len(text) * size * 1.02 + 24
    return size if need <= width else max(min_size, (width - 24) / (len(text) * 1.02))


def _banner(f: Fig, y, label, text, fill, stroke, red=(), h=34, size=14, x=10, w=W - 20):
    t = f"{label}：{text}"
    f.box(x, y, w, h, [t], fill=fill, stroke=stroke, sw=1.8, size=round(fit(t, w, size), 1), bold=True, red=red)


def _img_size(path, w):
    try:
        from PIL import Image
        iw, ih = Image.open(path).size
        return w, w * ih / iw
    except Exception:
        return w, w * 0.75


# R1 分层框图（师兄师姐开题常用）
def r1(C):
    its = C["items"]
    n = len(its)
    f = Fig(W, 452)
    lx, x0, x1 = 10, 62, W - 10
    layers = [("发现\n问题", "yellow", 8, 66), ("研究\n目标", "blue", 86, 54), ("研究\n内容", "blue", 152, 120),
              ("关键\n问题", "yellow", 284, 66)]
    for lab, col, y, h in layers:
        f.box(lx, y, W - 20, h, [], fill="none", stroke=col, sw=1.4, rx=10, dash="6,4")
        f.box(lx + 6, y + h / 2 - 20, 40, 40, lab.split("\n"), fill="none", stroke="none", size=13, bold=True,
              color="dblue", gap=1.25)
    red = C.get("red", [])
    fs = C["findings"]
    bw = (x1 - x0 - 10 * (len(fs) - 1)) / len(fs)
    for i, t in enumerate(fs):
        f.box(x0 + i * (bw + 10), 18, bw - 4, 46, wrap(t, 11), fill="lorange", stroke="orange", size=12.5, red=red)
    f.box(x0, 96, x1 - x0 - 4, 34, [C["goal"]], fill="lblue", stroke="blue", size=13.5, bold=True, red=red)
    bw = (x1 - x0 - 10 * (n - 1)) / n
    for i, it in enumerate(its):
        x = x0 + i * (bw + 10)
        f.box(x, 162, bw - 4, 30, [f"研究内容{i + 1}"], fill="blue", stroke="blue", size=12.5, bold=True,
              color="white", rx=6)
        f.box(x, 194, bw - 4, 70, wrap(it["name"], 7) + wrap(it["short"], 9), fill="white", stroke="blue",
              size=12, red=red, rx=6)
        if i < n - 1:
            f.line([(x + bw - 4, 229), (x + bw + 6, 229)], color="blue", sw=1.6)
    ks = C["key_problems"]
    bw2 = (x1 - x0 - 10 * (len(ks) - 1)) / len(ks)
    for i, t in enumerate(ks):
        f.box(x0 + i * (bw2 + 10), 294, bw2 - 4, 46, wrap(t, 11), fill="lorange", stroke="orange", size=12.5, red=red)
    mid = (x0 + x1) / 2
    for ya, yb in ((74, 86), (140, 152), (272, 284)):
        f.line([(mid, ya), (mid, yb + 6)], color="dblue", sw=2.2)
    f.text(W / 2, 372, "（层与层之间自上而下对应：问题 → 目标 → 内容 → 关键问题）", size=11.5, color="gray")
    f.H = 390
    return f


# R2 五层四列（问题—内容—方法—结果，一列一项，外圈反馈闭环）
def r2(C):
    its = C["items"]
    n = len(its)
    f = Fig(W, 500)
    red = C.get("red", [])
    x0, x1 = 58, W - 48
    bw = (x1 - x0 - 8 * (n - 1)) / n
    xs = [x0 + i * (bw + 8) for i in range(n)]
    _banner(f, 8, "工程问题", C["problem"], "lorange", "orange", red, h=32, size=13, x=x0, w=x1 - x0)
    rows = [("存在\n问题", "issue", "lorange", "orange", 56), ("研究\n内容", "name", "lblue", "blue", 136),
            ("关键\n方法", "method", "white", "gray", 216), ("预期\n结果", "result", "lgreen", "green", 296)]
    for lab, key, fill, stroke, y in rows:
        f.box(10, y - 4, W - 40, 68, [], fill="none", stroke="yellow" if key in ("issue", "method") else "blue",
              sw=1.2, rx=8, dash="5,4")
        f.box(14, y + 10, 40, 40, lab.split("\n"), fill="none", stroke="none", size=12.5, bold=True, color="dblue",
              gap=1.25)
        for i, it in enumerate(its):
            f.box(xs[i], y + 2, bw, 56, wrap(it[key], 7), fill=fill, stroke=stroke, size=12,
                  bold=(key == "name"), red=red, rx=6)
    for i in range(n):
        cx = xs[i] + bw / 2
        f.line([(cx, 40), (cx, 57)], color="dblue", sw=1.4)
        for ya in (114, 194, 274):
            f.line([(cx, ya), (cx, ya + 23)], color="dblue", sw=1.4)
        f.line([(cx, 354), (cx, 375)], color="dblue", sw=1.4)
    for i in range(n - 1):
        f.line([(xs[i] + bw, 166), (xs[i + 1], 166)], color="blue", sw=1.6)
    _banner(f, 376, "研究目标", C["goal"], "lblue", "blue", red, h=32, size=13, x=x0, w=x1 - x0)
    fx = W - 14
    f.line([(xs[-1] + bw, 326), (fx, 326), (fx, 150), (xs[-1] + bw + 1, 150)], color="orange", sw=2.0)
    f.text(fx - 8, 238, C.get("feedback_short", C["feedback"][:6]), size=11.5, bold=True, color="orange", vertical=True)
    f.H = 416
    return f


# R3 横向闭环链（每项一列，产出接到下一项，末项反馈回第一项）
def r3(C):
    its = C["items"]
    n = len(its)
    f = Fig(W, 430)
    red = C.get("red", [])
    _banner(f, 8, "核心问题", C["problem"], "lblue", "blue", red)
    gap = 22
    bw = (W - 40 - gap * (n - 1)) / n
    x0, yb, bh = 20, 84, 150
    xs = [x0 + i * (bw + gap) for i in range(n)]
    f.line([(W / 2, 42), (W / 2, 62)], color="blue", arrow=False)
    f.line([(xs[0] + bw / 2, 62), (xs[-1] + bw / 2, 62)], color="blue", arrow=False)
    for i, it in enumerate(its):
        x = xs[i]
        f.line([(x + bw / 2, 62), (x + bw / 2, yb - 1)], color="blue")
        f.box(x, yb, bw, bh, [], fill="white", stroke="blue", sw=1.8)
        f.box(x, yb, bw, 26, [f"研究内容{i + 1}"], fill="blue", stroke="blue", size=12.5, bold=True, color="white",
              rx=6)
        f.lines(x + bw / 2, yb + 58, wrap(it["name"], 6), size=14.5, bold=True, color="blue", red=red)
        f.line([(x + 10, yb + 88), (x + bw - 10, yb + 88)], color="#BFBFBF", sw=1, arrow=False)
        f.lines(x + bw / 2, yb + 118, wrap(it["short"], 8), size=12, color="#262626")
        f.line([(x + bw / 2, yb + bh), (x + bw / 2, yb + bh + 9)], color="green", sw=1.4)
        f.pill(x + bw / 2, yb + bh + 21, it["output"], size=12)
    for i in range(n - 1):
        f.line([(xs[i] + bw / 2 + len(its[i]["output"]) * 6 + 10, yb + bh + 21), (xs[i] + bw + gap / 2, yb + bh + 21),
                (xs[i] + bw + gap / 2, yb + bh / 2), (xs[i + 1] - 1, yb + bh / 2)], color="blue", sw=1.6)
    yf = yb + bh + 58
    f.line([(xs[-1] + bw / 2, yb + bh + 32), (xs[-1] + bw / 2, yf), (xs[0] + bw / 2, yf), (xs[0] + bw / 2, yb + bh + 33)],
           color="orange", sw=2.2)
    f.text(W / 2, yf + 14, C["feedback"], size=12.5, bold=True, color="orange")
    _banner(f, yf + 32, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = yf + 74
    return f


# R4 阶梯递进（自左下向右上逐级上升，台阶之间写产出）
def r4(C):
    its = C["items"]
    n = len(its)
    red = C.get("red", [])
    f = Fig(W, 400)
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    bw, bh, dy = 236, 52, 78
    dx = (W - 20 - bw) / max(n - 1, 1)
    ytop = 54
    pos = [(10 + i * dx, ytop + (n - 1 - i) * dy) for i in range(n)]
    for i, (it, (x, y)) in enumerate(zip(its, pos)):
        f.box(x, y, bw, bh, [], fill="lblue" if i % 2 == 0 else "white", stroke="blue", sw=1.8)
        f.num(x + 16, y + bh / 2, i + 1, r=10)
        f.text(x + 32, y + 17, it["name"], size=14, bold=True, color="blue", anchor="start", red=red)
        f.text(x + 32, y + 37, it["short"], size=11.5, color="#262626", anchor="start")
        if i < n - 1:
            ax = x + bw - 34
            ny = pos[i + 1][1]
            f.line([(ax, y), (ax, ny + bh + 1)], color="green", sw=1.8)
            f.text(ax + 8, (y + ny + bh) / 2, it["output"], size=11.5, bold=True, color="green", anchor="start")
    gy = ytop + (n - 1) * dy + bh + 14
    _banner(f, gy, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = gy + 42
    return f


# R5 环形（四项围绕核心对象顺时针循环）
def r5(C):
    its = C["items"][:4]
    f = Fig(W, 410)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    cx, cy = W / 2, 206
    f.circle(cx, cy, 52, fill="lblue", stroke="blue", sw=1.8)
    f.lines(cx, cy, wrap(C["core"], 6), size=14, bold=True, color="dblue")
    pos = [(cx, cy - 122), (cx + 190, cy), (cx, cy + 122), (cx - 190, cy)]
    bw, bh = 168, 54
    for i, (it, (x, y)) in enumerate(zip(its, pos)):
        f.box(x - bw / 2, y - bh / 2, bw, bh, [it["name"], it["short"]], fill="white", stroke="blue", sw=1.8,
              size=12.5, red=red)
        f.num(x - bw / 2 + 2, y - bh / 2 + 2, i + 1, r=10)
    arcs = [[(cx + 86, cy - 122), (cx + 190, cy - 122), (cx + 190, cy - 28)],
            [(cx + 190, cy + 28), (cx + 190, cy + 122), (cx + 86, cy + 122)],
            [(cx - 86, cy + 122), (cx - 190, cy + 122), (cx - 190, cy + 28)],
            [(cx - 190, cy - 28), (cx - 190, cy - 122), (cx - 86, cy - 122)]]
    for k, a in enumerate(arcs):
        col = "orange" if k == 3 else "blue"
        f.line(a, color=col, sw=2.0)
    for k, (x, y) in enumerate([(cx + 150, cy - 100), (cx + 150, cy + 100), (cx - 150, cy + 100)]):
        f.pill(x, y, its[k]["output"], size=11.5)
    f.pill(cx - 150, cy - 100, C["feedback"][:6], color="orange", fill="lorange", size=11.5)
    _banner(f, 364, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = 404
    return f


# R6 概念闭环（参考 Leidner 2017 博士论文：每步只写一个概念词，围绕决策对象闭环）
def r6(C):
    its = C["items"][:4]
    f = Fig(W, 380)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    pts = [(150, 100), (455, 100), (455, 262), (150, 262)]
    bw, bh = 150, 62
    for i, (it, (x, y)) in enumerate(zip(its, pts)):
        f.box(x - bw / 2, y - bh / 2, bw, bh, [it["concept"]], fill="white", stroke="blue", sw=2, rx=10, size=17,
              bold=True, color="blue")
        f.num(x - bw / 2 + 2, y - bh / 2 + 2, i + 1, r=11)
        if it.get("kp"):
            ty = y - bh / 2 - 23 if i in (0, 1) else y + bh / 2 + 4
            f.box(x + bw / 2 - 78, ty, 76, 19, [f"关键问题{it['kp']}"], fill="lgray", stroke="gray", sw=1, rx=4,
                  size=11, color="gray")
    f.line([(150 + bw / 2, 100), (455 - bw / 2 - 2, 100)], color="blue", sw=2.4)
    f.pill(302, 100, its[0]["output"])
    f.line([(455, 100 + bh / 2), (455, 262 - bh / 2 - 2)], color="blue", sw=2.4)
    f.pill(530, 181, its[1]["output"])
    f.line([(455 - bw / 2, 262), (150 + bw / 2 + 2, 262)], color="blue", sw=2.4)
    f.pill(302, 262, its[2]["output"])
    f.line([(150, 262 - bh / 2), (150, 100 + bh / 2 + 2)], color="orange", sw=2.8)
    f.pill(78, 181, C["feedback"][:6], color="orange", fill="lorange")
    f.box(242, 146, 120, 70, wrap(C["core"], 6), fill="lblue", stroke="blue", sw=1.6, rx=35, size=14, bold=True,
          color="dblue")
    _banner(f, 326, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = 368
    return f


# R7 场景标注（参考 Holladay 2024 博士论文：用场景图交代对象，编号指向各项研究内容）
def r7(C):
    its = C["items"]
    f = Fig(W, 400)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    iw, ih = _img_size(C["scene"], 330)
    ix, iy = 10, 52
    f.image(C["scene"], ix, iy, iw, ih)
    f.box(ix, iy, iw, ih, [], fill="none", stroke="blue", sw=1.2, rx=4, dash="6,4")
    f.text(ix + iw / 2, iy + ih + 12, C.get("scene_caption", ""), size=11, color="gray")
    bx, bw = ix + iw + 16, W - (ix + iw + 16) - 10
    bh = min(64, (ih - 8 * (len(its) - 1)) / len(its))
    marks = {m[0]: m for m in C.get("scene_marks", [])}
    for i, it in enumerate(its):
        y = iy + i * (bh + 8)
        f.box(bx, y, bw, bh, [], fill="white", stroke="blue", sw=1.6)
        f.num(bx + 14, y + bh / 2, i + 1, r=10)
        f.text(bx + 30, y + bh / 2 - 10, it["name"], size=13.5, bold=True, color="blue", anchor="start", red=red)
        f.text(bx + 30, y + bh / 2 + 11, it["short"], size=11.5, color="#262626", anchor="start")
        if i + 1 in marks:
            _, mx, my = marks[i + 1]
            px, py = ix + mx * iw, iy + my * ih
            f.line([(px, py), (bx - 4, y + bh / 2)], color="gray", sw=1.0, arrow=False, dash="3,3")
            f.num(px, py, i + 1, r=10)
    gy = max(iy + ih + 26, iy + len(its) * (bh + 8) + 6)
    _banner(f, gy, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = gy + 42
    return f


# R8 场景图＋四步闭环（作者开题报告图2-1 的画法）
def r8(C):
    its = C["items"]
    n = len(its)
    f = Fig(W, 400)
    red = C.get("red", [])
    _banner(f, 6, "核心问题", C["problem"], "lorange", "orange", red)
    iw, ih = _img_size(C["scene"], 300)
    ix, iy = 10, 52
    f.image(C["scene"], ix, iy, iw, ih)
    f.box(ix, iy, iw, ih, [], fill="none", stroke="blue", sw=1.2, rx=4, dash="6,4")
    for m in C.get("scene_marks", []):
        f.num(ix + m[1] * iw, iy + m[2] * ih, m[0], r=10)
    f.text(ix + iw / 2, iy + ih + 12, C.get("scene_caption", ""), size=11, color="gray")
    bx, bw, bh = 340, 196, 50
    step = max(76, (ih + 10) / n) if n < 4 else 76
    ys = [iy + k * step for k in range(n)]
    for k, it in enumerate(its):
        y = ys[k]
        f.box(bx, y, bw, bh, [], fill="white", stroke="blue", sw=1.8)
        f.num(bx + 17, y + bh / 2, k + 1, r=10)
        f.text(bx + 32 + (bw - 32) / 2, y + 16, it["name"], size=14, bold=True, color="blue", red=red)
        f.text(bx + 32 + (bw - 32) / 2, y + 35, it["short"], size=11.5, color="#262626")
        if k < n - 1:
            f.line([(bx + bw / 2, y + bh), (bx + bw / 2, ys[k + 1] - 1)], color="blue", sw=2.0)
            w = len(it["output"]) * 12 + 18
            f.box(bx + bw / 2 + 8, y + bh + 4, w, 19, [it["output"]], fill="lgreen", stroke="green", sw=1.1, rx=9.5,
                  size=11.5, bold=True, color="green")
    fx = bx + bw + 20
    f.line([(bx + bw, ys[-1] + bh / 2), (fx, ys[-1] + bh / 2), (fx, ys[0] + bh / 2), (bx + bw + 1, ys[0] + bh / 2)],
           color="orange", sw=2.2)
    f.text(fx + 12, (ys[0] + ys[-1]) / 2 + bh / 2, C["feedback"][:8], size=11.5, bold=True, color="orange",
           vertical=True)
    gy = max(iy + ih + 26, ys[-1] + bh + 14)
    _banner(f, gy, "研究目标", C["goal"], "lblue", "blue", red)
    f.H = gy + 42
    return f


# R9 研究问题—章节对应（参考 Trevisan 2025 博士论文：研究问题映射到论文章节）
def r9(C):
    its = C["items"]
    n = len(its)
    f = Fig(W, 420)
    red = C.get("red", [])
    f.box(10, 6, W - 20, 32, ["第1章 绪论：" + C["problem"]], fill="lgray", stroke="gray", size=13, bold=True, red=red)
    f.text(150, 54, "研究问题", size=13, bold=True, color="dblue")
    f.text(455, 54, "研究内容与论文章节", size=13, bold=True, color="dblue")
    y0, bh, g = 68, 58, 10
    for i, it in enumerate(its):
        y = y0 + i * (bh + g)
        f.box(14, y, 272, bh, wrap(f"问题{i + 1}：{it['question']}", 17), fill="lorange", stroke="orange", size=12,
              align="left", red=red)
        f.box(330, y, 260, bh, [f"第{i + 2}章 {it['chapter']}", f"研究内容{i + 1}：{it['name']}"], fill="lblue",
              stroke="blue", size=12, align="left", red=red)
        f.line([(286, y + bh / 2), (329, y + bh / 2)], color="blue", sw=1.8)
        if i < n - 1:
            f.line([(460, y + bh), (460, y + bh + g)], color="green", sw=1.4)
    yb = y0 + n * (bh + g) + 2
    f.box(10, yb, W - 20, 32, [f"第{n + 2}章 总结与展望：{C['goal']}"], fill="lgray", stroke="gray", size=13, bold=True,
          red=red)
    f.H = yb + 40
    return f


STYLES = {
    "R1": ("分层框图", r1), "R2": ("五层四列", r2), "R3": ("横向闭环链", r3), "R4": ("阶梯递进", r4),
    "R5": ("环形循环", r5), "R6": ("概念闭环", r6), "R7": ("场景标注", r7), "R8": ("场景图加四步闭环", r8),
    "R9": ("研究问题与章节对应", r9),
}
