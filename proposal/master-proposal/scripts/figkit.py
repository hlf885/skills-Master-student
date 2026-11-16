#!/usr/bin/env python3
"""figkit：开题自绘图的统一绘图引擎（1.7.0 新增）。

同一套图元可输出三种格式，供用户自行选择：
  - SVG：可在 Visio、PowerPoint 中插入后转为形状编辑；
  - PNG：直接插入 Word（Playwright + Chromium 渲染，约 300 dpi）；
  - Visio 宏（.bas）：在 Visio 中 Alt+F11 → 文件 → 导入文件 → 运行 DrawFigure，生成可编辑图形。

坐标单位为像素，96 px = 1 in，原点在左上角。默认画布宽 605 px（约 16 cm，A4 版心）。
图元：box（带文字的矩形）、text（文字）、line（折线，可带箭头）、circle（圆，可带编号）、image（插图）。
画法（style）见 figstyles/ 目录；命令行入口见 draw_figure.py。
"""
from __future__ import annotations

import base64
import html
import mimetypes
import re
from pathlib import Path

FONT_SVG = "SimSun, Noto Serif CJK SC, Times New Roman, serif"
PALETTE = {
    "blue": "#2F5597", "lblue": "#DEEBF7", "orange": "#ED7D31", "lorange": "#FBE5D6",
    "green": "#548235", "lgreen": "#E2F0D9", "red": "#C00000", "gray": "#595959",
    "lgray": "#F2F2F2", "yellow": "#FFC000", "dblue": "#1F3864", "black": "#000000", "white": "#FFFFFF",
}


def c(col: str | None) -> str:
    if col is None or col == "none":
        return "none"
    return PALETTE.get(col, col)


class Fig:
    def __init__(self, W: float = 605, H: float = 400):
        self.W, self.H = W, H
        self.items: list[dict] = []

    # ---------- 图元 ----------
    def box(self, x, y, w, h, lines=(), fill="white", stroke="blue", sw=1.6, rx=8, dash=None,
            size=13, bold=False, color="black", red=(), align="center", valign="middle", gap=1.4, pad=6):
        if isinstance(lines, str):
            lines = [lines]
        self.items.append(dict(k="box", x=x, y=y, w=w, h=h, lines=list(lines), fill=fill, stroke=stroke, sw=sw,
                               rx=rx, dash=dash, size=size, bold=bold, color=color, red=list(red), align=align,
                               valign=valign, gap=gap, pad=pad))

    def text(self, x, y, t, size=13, bold=False, color="black", anchor="middle", red=(), vertical=False):
        self.items.append(dict(k="text", x=x, y=y, t=t, size=size, bold=bold, color=color, anchor=anchor,
                               red=list(red), vertical=vertical))

    def lines(self, x, y, ls, size=13, gap=1.4, **kw):
        y0 = y - (len(ls) - 1) * size * gap / 2
        for i, l in enumerate(ls):
            self.text(x, y0 + i * size * gap, l, size=size, **kw)

    def line(self, pts, color="blue", sw=1.8, arrow=True, dash=None, both=False):
        self.items.append(dict(k="line", pts=[tuple(p) for p in pts], color=color, sw=sw, arrow=arrow, dash=dash,
                               both=both))

    def circle(self, cx, cy, r, fill="blue", stroke="white", sw=1.5, t=None, size=None, color="white", bold=True):
        self.items.append(dict(k="circle", cx=cx, cy=cy, r=r, fill=fill, stroke=stroke, sw=sw, t=t,
                               size=size or r * 1.25, color=color, bold=bold))

    def image(self, path, x, y, w, h):
        self.items.append(dict(k="image", path=str(path), x=x, y=y, w=w, h=h))

    # 常用组合
    def num(self, cx, cy, n, color="blue", r=10):
        self.circle(cx, cy, r, fill=color, t=str(n))

    def pill(self, cx, cy, t, color="green", fill="lgreen", size=12):
        w = len(t) * size * 0.98 + 18
        self.box(cx - w / 2, cy - 10.5, w, 21, [t], fill=fill, stroke=color, sw=1.2, rx=10.5, size=size, bold=True,
                 color=color)

    # ---------- SVG ----------
    def to_svg(self) -> str:
        cols = sorted({c(i["color"]) for i in self.items if i["k"] == "line"})
        defs = "".join(
            f'<marker id="m{col[1:]}" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" '
            f'markerUnits="userSpaceOnUse"><path d="M0,0 L10,4 L0,8 z" fill="{col}"/></marker>'
            f'<marker id="s{col[1:]}" markerWidth="10" markerHeight="8" refX="1" refY="4" orient="auto" '
            f'markerUnits="userSpaceOnUse"><path d="M10,0 L0,4 L10,8 z" fill="{col}"/></marker>' for col in cols)
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" '
               f'viewBox="0 0 {self.W} {self.H}" font-family="{FONT_SVG}"><defs>{defs}</defs>'
               f'<rect width="100%" height="100%" fill="white"/>']
        for it in self.items:
            out.append(getattr(self, "_svg_" + it["k"])(it))
        out.append("</svg>")
        return "".join(out)

    @staticmethod
    def _spans(t, red, base):
        s = html.escape(t)
        for r in red:
            s = s.replace(html.escape(r), f'<tspan fill="{c("red")}">{html.escape(r)}</tspan>')
        return s

    def _svg_text_line(self, x, y, t, size, bold, color, anchor, red, vertical=False):
        extra = ' style="writing-mode:vertical-rl;glyph-orientation-vertical:0"' if vertical else ""
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{"bold" if bold else "normal"}" '
                f'fill="{c(color)}" text-anchor="{anchor}" dominant-baseline="central"{extra}>'
                f'{self._spans(t, red, color)}</text>')

    def _svg_box(self, b):
        d = f' stroke-dasharray="{b["dash"]}"' if b["dash"] else ""
        s = (f'<rect x="{b["x"]:.1f}" y="{b["y"]:.1f}" width="{b["w"]:.1f}" height="{b["h"]:.1f}" rx="{b["rx"]}" '
             f'fill="{c(b["fill"])}" stroke="{c(b["stroke"])}" stroke-width="{b["sw"]}"{d}/>')
        n = len(b["lines"])
        if n:
            lh = b["size"] * b["gap"]
            if b["valign"] == "top":
                y0 = b["y"] + b["pad"] + b["size"] / 2 + 2
            else:
                y0 = b["y"] + b["h"] / 2 - (n - 1) * lh / 2
            if b["align"] == "left":
                x, anc = b["x"] + b["pad"] + 2, "start"
            else:
                x, anc = b["x"] + b["w"] / 2, "middle"
            for i, l in enumerate(b["lines"]):
                s += self._svg_text_line(x, y0 + i * lh, l, b["size"], b["bold"], b["color"], anc, b["red"])
        return s

    def _svg_text(self, t):
        return self._svg_text_line(t["x"], t["y"], t["t"], t["size"], t["bold"], t["color"], t["anchor"], t["red"],
                                   t["vertical"])

    def _svg_line(self, l):
        col = c(l["color"])
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in l["pts"])
        m = f' marker-end="url(#m{col[1:]})"' if l["arrow"] else ""
        if l["both"]:
            m += f' marker-start="url(#s{col[1:]})"'
        d = f' stroke-dasharray="{l["dash"]}"' if l["dash"] else ""
        return (f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{l["sw"]}" '
                f'stroke-linejoin="round"{m}{d}/>')

    def _svg_circle(self, o):
        s = (f'<circle cx="{o["cx"]:.1f}" cy="{o["cy"]:.1f}" r="{o["r"]}" fill="{c(o["fill"])}" '
             f'stroke="{c(o["stroke"])}" stroke-width="{o["sw"]}"/>')
        if o["t"] is not None:
            s += self._svg_text_line(o["cx"], o["cy"] + 0.5, o["t"], round(o["size"], 1), o["bold"], o["color"],
                                     "middle", [])
        return s

    def _svg_image(self, im):
        mime = mimetypes.guess_type(im["path"])[0] or "image/png"
        data = base64.b64encode(Path(im["path"]).read_bytes()).decode()
        return (f'<image href="data:{mime};base64,{data}" x="{im["x"]}" y="{im["y"]}" width="{im["w"]}" '
                f'height="{im["h"]}" preserveAspectRatio="xMidYMid meet"/>')

    # ---------- PNG ----------
    def to_png(self, path, scale=3.2):
        from playwright.sync_api import sync_playwright
        svg = self.to_svg()
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": int(self.W) + 1, "height": int(self.H) + 1}, device_scale_factor=scale)
            pg.set_content(f'<html><body style="margin:0">{svg}</body></html>')
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(path), clip={"x": 0, "y": 0, "width": self.W, "height": self.H})
            b.close()

    # ---------- Visio 宏 ----------
    def to_vba(self, title="figure", font_cn="宋体", font_en="Times New Roman") -> str:
        from visio_macro import vb_str, vb_assign  # 复用中文转 ChrW 的工具

        W, H = self.W / 96, self.H / 96
        X = lambda px: round(px / 96, 4)
        Y = lambda py: round((self.H - py) / 96, 4)

        def rgb(col):
            col = c(col)
            if col == "none":
                return "none"
            col = col.lstrip("#")
            return f"RGB({int(col[0:2], 16)},{int(col[2:4], 16)},{int(col[4:6], 16)})"

        L: list[str] = []
        a = L.append
        a('Attribute VB_Name = "FigureMacro"')
        a("Option Explicit")
        a("' Auto-generated by figkit.py. Visio: Alt+F11 -> File -> Import File -> run DrawFigure")
        a("' Figure: " + re.sub(r"[^\x20-\x7e]", "?", title))
        a("Private gFontEn As String")
        a("Private gFontCn As String")
        a("Private gImgDir As String")
        a("")
        a("Sub DrawFigure()")
        a("    Dim doc As Visio.Document, pg As Visio.Page, shp As Visio.Shape, txt As String, lbl As String")
        a('    Set doc = Application.Documents.Add("")')
        a("    Set pg = doc.Pages(1)")
        a(f'    pg.PageSheet.CellsU("PageWidth").FormulaU = "{W:.3f} in"')
        a(f'    pg.PageSheet.CellsU("PageHeight").FormulaU = "{H:.3f} in"')
        vb_assign(L, "gFontEn", font_en)
        vb_assign(L, "gFontCn", font_cn)
        if any(i["k"] == "image" for i in self.items):
            vb_assign(L, "lbl", "场景图所在文件夹（与本宏文件放在一起）")
            a('    gImgDir = InputBox(lbl, "figkit", "")')
            a('    If Len(gImgDir) = 0 Then gImgDir = CurDir')
            a('    If Right(gImgDir, 1) <> "\\" Then gImgDir = gImgDir & "\\"')
        for it in self.items:
            k = it["k"]
            if k == "box":
                txt = "\n".join(it["lines"])
                vb_assign(L, "txt", txt)
                halign = 0 if it["align"] == "left" else 1
                valign = 0 if it["valign"] == "top" else 1
                a(f"    Set shp = MakeBox(doc, pg, {X(it['x'])}, {Y(it['y'] + it['h'])}, {X(it['x'] + it['w'])}, "
                  f"{Y(it['y'])}, txt, \"{rgb(it['fill'])}\", \"{rgb(it['stroke'])}\", {it['sw'] * 0.75:.2f}, "
                  f"{X(it['rx']) if it['rx'] else 0}, {'True' if it['dash'] else 'False'}, {it['size'] * 0.75:.2f}, "
                  f"{'True' if it['bold'] else 'False'}, \"{rgb(it['color'])}\", {halign}, {valign})")
                for r in it["red"]:
                    vb_assign(L, "lbl", r)
                    a("    Highlight shp, lbl")
            elif k == "text":
                w = max(len(it["t"]) * it["size"] * 1.05 + 8, 20)
                hgt = it["size"] * 1.6
                if it["vertical"]:
                    w, hgt = hgt, w
                if it["anchor"] == "start":
                    x1 = it["x"]
                elif it["anchor"] == "end":
                    x1 = it["x"] - w
                else:
                    x1 = it["x"] - w / 2
                vb_assign(L, "txt", it["t"])
                a(f"    Set shp = MakeText(doc, pg, {X(x1)}, {Y(it['y'] + hgt / 2)}, {X(x1 + w)}, {Y(it['y'] - hgt / 2)}, "
                  f"txt, {it['size'] * 0.75:.2f}, {'True' if it['bold'] else 'False'}, \"{rgb(it['color'])}\", "
                  f"{'True' if it['vertical'] else 'False'})")
                for r in it["red"]:
                    vb_assign(L, "lbl", r)
                    a("    Highlight shp, lbl")
            elif k == "line":
                pts = it["pts"]
                arr = ", ".join(f"{X(x)}, {Y(y)}" for x, y in pts)
                a(f"    Set shp = MakeLine(pg, Array({arr}), \"{rgb(it['color'])}\", {it['sw'] * 0.75:.2f}, "
                  f"{'True' if it['arrow'] else 'False'}, {'True' if it['dash'] else 'False'}, "
                  f"{'True' if it['both'] else 'False'})")
            elif k == "circle":
                vb_assign(L, "txt", it["t"] or "")
                a(f"    Set shp = MakeCircle(doc, pg, {X(it['cx'] - it['r'])}, {Y(it['cy'] + it['r'])}, "
                  f"{X(it['cx'] + it['r'])}, {Y(it['cy'] - it['r'])}, txt, \"{rgb(it['fill'])}\", "
                  f"\"{rgb(it['stroke'])}\", {it['size'] * 0.75:.2f}, \"{rgb(it['color'])}\")")
            elif k == "image":
                vb_assign(L, "txt", Path(it["path"]).name)
                a(f"    Set shp = PlaceImage(pg, gImgDir & txt, {X(it['x'])}, {Y(it['y'] + it['h'])}, "
                  f"{X(it['x'] + it['w'])}, {Y(it['y'])})")
        a("    ActiveWindow.ViewFit = visFitPage")
        a("End Sub")
        a("")
        a(VBA_HELPERS)
        text = "\n".join(L) + "\n"
        return text.replace("\r\n", "\n").replace("\n", "\r\n")


VBA_HELPERS = r'''
Private Sub ApplyFont(doc As Visio.Document, shp As Visio.Shape, sizePt As Double, isBold As Boolean, fontRGB As String)
    On Error Resume Next
    shp.CellsU("Char.Size").FormulaU = CStr(sizePt) & " pt"
    shp.CellsU("Char.Font").FormulaU = CStr(doc.Fonts.Item(gFontEn).ID)
    shp.CellsU("Char.AsianFont").FormulaU = CStr(doc.Fonts.Item(gFontCn).ID)
    shp.CellsU("Char.Color").FormulaU = fontRGB
    If isBold Then shp.CellsU("Char.Style").FormulaU = "1"
    shp.CellsU("LeftMargin").FormulaU = "1 pt"
    shp.CellsU("RightMargin").FormulaU = "1 pt"
    shp.CellsU("TopMargin").FormulaU = "1 pt"
    shp.CellsU("BottomMargin").FormulaU = "1 pt"
    On Error GoTo 0
End Sub

Private Function MakeBox(doc As Visio.Document, pg As Visio.Page, x1 As Double, y1 As Double, x2 As Double, y2 As Double, _
    txt As String, fillRGB As String, lineRGB As String, lwPt As Double, rnd As Double, dashed As Boolean, _
    sizePt As Double, isBold As Boolean, fontRGB As String, hAlign As Integer, vAlign As Integer) As Visio.Shape
    Dim shp As Visio.Shape
    Set shp = pg.DrawRectangle(x1, y1, x2, y2)
    If fillRGB = "none" Then
        shp.CellsU("FillPattern").FormulaU = "0"
    Else
        shp.CellsU("FillForegnd").FormulaU = fillRGB
        shp.CellsU("FillPattern").FormulaU = "1"
    End If
    If lineRGB = "none" Then
        shp.CellsU("LinePattern").FormulaU = "0"
    Else
        shp.CellsU("LineColor").FormulaU = lineRGB
        shp.CellsU("LineWeight").FormulaU = CStr(lwPt) & " pt"
        If dashed Then shp.CellsU("LinePattern").FormulaU = "2"
    End If
    shp.CellsU("Rounding").FormulaU = CStr(rnd) & " in"
    shp.Text = Replace(txt, vbLf, Chr(10))
    shp.CellsU("Para.HorzAlign").FormulaU = CStr(hAlign)
    shp.CellsU("VerticalAlign").FormulaU = CStr(vAlign)
    ApplyFont doc, shp, sizePt, isBold, fontRGB
    Set MakeBox = shp
End Function

Private Function MakeText(doc As Visio.Document, pg As Visio.Page, x1 As Double, y1 As Double, x2 As Double, y2 As Double, _
    txt As String, sizePt As Double, isBold As Boolean, fontRGB As String, vertical As Boolean) As Visio.Shape
    Dim shp As Visio.Shape
    Set shp = pg.DrawRectangle(x1, y1, x2, y2)
    shp.CellsU("FillPattern").FormulaU = "0"
    shp.CellsU("LinePattern").FormulaU = "0"
    shp.Text = txt
    If vertical Then shp.CellsU("TxtAngle").FormulaU = "-90 deg"
    If vertical Then shp.CellsU("TxtWidth").FormulaU = "Height"
    If vertical Then shp.CellsU("TxtHeight").FormulaU = "Width"
    ApplyFont doc, shp, sizePt, isBold, fontRGB
    Set MakeText = shp
End Function

Private Function MakeLine(pg As Visio.Page, pts As Variant, lineRGB As String, lwPt As Double, _
    hasArrow As Boolean, dashed As Boolean, both As Boolean) As Visio.Shape
    Dim n As Long, i As Long
    n = UBound(pts) - LBound(pts) + 1
    Dim xy() As Double
    ReDim xy(0 To n - 1)
    For i = 0 To n - 1
        xy(i) = CDbl(pts(LBound(pts) + i))
    Next i
    Dim shp As Visio.Shape
    If n = 4 Then
        Set shp = pg.DrawLine(xy(0), xy(1), xy(2), xy(3))
    Else
        Set shp = pg.DrawPolyline(xy, 0)
    End If
    shp.CellsU("LineColor").FormulaU = lineRGB
    shp.CellsU("LineWeight").FormulaU = CStr(lwPt) & " pt"
    If dashed Then shp.CellsU("LinePattern").FormulaU = "2"
    If hasArrow Then shp.CellsU("EndArrow").FormulaU = "13"
    If both Then shp.CellsU("BeginArrow").FormulaU = "13"
    Set MakeLine = shp
End Function

Private Function MakeCircle(doc As Visio.Document, pg As Visio.Page, x1 As Double, y1 As Double, x2 As Double, y2 As Double, _
    txt As String, fillRGB As String, lineRGB As String, sizePt As Double, fontRGB As String) As Visio.Shape
    Dim shp As Visio.Shape
    Set shp = pg.DrawOval(x1, y1, x2, y2)
    shp.CellsU("FillForegnd").FormulaU = fillRGB
    shp.CellsU("FillPattern").FormulaU = "1"
    If lineRGB = "none" Then
        shp.CellsU("LinePattern").FormulaU = "0"
    Else
        shp.CellsU("LineColor").FormulaU = lineRGB
    End If
    shp.Text = txt
    ApplyFont doc, shp, sizePt, True, fontRGB
    Set MakeCircle = shp
End Function

Private Function PlaceImage(pg As Visio.Page, path As String, x1 As Double, y1 As Double, x2 As Double, y2 As Double) As Visio.Shape
    Dim shp As Visio.Shape
    On Error Resume Next
    Set shp = pg.Import(path)
    If shp Is Nothing Then
        Set shp = pg.DrawRectangle(x1, y1, x2, y2)
        shp.Text = "[image] " & path
        Set PlaceImage = shp
        Exit Function
    End If
    On Error GoTo 0
    shp.CellsU("PinX").FormulaU = CStr((x1 + x2) / 2) & " in"
    shp.CellsU("PinY").FormulaU = CStr((y1 + y2) / 2) & " in"
    shp.CellsU("Width").FormulaU = CStr(x2 - x1) & " in"
    shp.CellsU("Height").FormulaU = CStr(y2 - y1) & " in"
    shp.SendToBack
    Set PlaceImage = shp
End Function

Private Sub Highlight(shp As Visio.Shape, s As String)
    Dim pos As Long
    Dim chars As Visio.Characters
    If Len(s) = 0 Then Exit Sub
    pos = InStr(1, shp.Characters.Text, s)
    Do While pos > 0
        Set chars = shp.Characters
        chars.Begin = pos - 1
        chars.End = pos - 1 + Len(s)
        chars.CharProps(visCharacterColor) = 2
        pos = InStr(pos + Len(s), shp.Characters.Text, s)
    Loop
End Sub
'''
