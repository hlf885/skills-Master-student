#!/usr/bin/env python3
"""swust_kit: 在学校原生模板上生成开题答辩 PPT 的工具库。

思路取自 ppt-master 的 Edit Native PPTX 路线: 保留模板原生的母版、版式和页眉元素,
只往页面里填新内容; 公式用 ppt-master 的 LaTeX 转 Office Math 编译器生成可编辑公式。

最小用法:
    from swust_kit import Deck, CM
    d = Deck("assets/swust_proposal_template.pptx")
    d.cover(year=2026, school="西南科技大学硕士", title="论文题目")
    d.toc()
    d.part(1, "立 题 依 据")
    s = d.content(1, "立题依据", "研究背景")
    d.text(s, 2, 3.5, 15, 6, ["第一段", "第二段 **红色强调** 和 __蓝色强调__"])
    d.end(year=2026, school="西南科技大学硕士", date="2026年11月")
    d.save("out.pptx")

坐标单位一律为厘米, 画布 33.867 x 19.05。内容安全区 x 1.2~32.6, y 3.2~17.2。
"""
from __future__ import annotations

import copy
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Cm, Emu, Pt

HERE = Path(__file__).resolve().parent
CM = 360000

# 模板配色 (取自西南科技大学开题模板)
DARK = RGBColor(0x27, 0x4F, 0x7F)     # 主色 深蓝
BLUE = RGBColor(0x25, 0x6D, 0xB7)     # 辅色 亮蓝
RED = RGBColor(0xC0, 0x00, 0x00)      # 强调 红
BLACK = RGBColor(0x1A, 0x1A, 0x1A)
GRAY = RGBColor(0x59, 0x59, 0x59)
LIGHT = RGBColor(0xE8, 0xEF, 0xF8)    # 浅蓝底
LIGHT2 = RGBColor(0xF4, 0xF7, 0xFB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xF8, 0xCB, 0xAD)
FONT = "微软雅黑"

_ROLE_ORDER = ["cover", "toc", "part", "content", "end"]
_RT_IMAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"


def _rgb(c):
    return c if isinstance(c, RGBColor) else RGBColor.from_string(c.lstrip("#"))


# 风格样页可选的整套风格。每套只规定颜色与字号规则, 页面版式按内容选择(见 references/08)。
THEMES = {
    "学术极简": dict(NAVY="274F7F", INK="1F2933", MUTE="6B7280", RULE="C8D0DB", ACC="A33B2B", TINT="F1F4F8", head=22, body=18, panels="none", hl="274F7F", gap="A33B2B",
                 desc="模板深蓝做标题, 正文深灰, 浅灰细线分区, 暗红只标研究空白"),
    "V3实例": dict(NAVY="274F7F", INK="1F2933", MUTE="6B7280", RULE="C8D0DB", ACC="A33B2B", TINT="F1F4F8", head=22, body=18, panels="none", hl="274F7F", gap="A33B2B",
                 preset="assets/presets/v3_deck.py",
                 desc="用户反馈很好的一套完整做法: 学术极简规则, 外加 17 页逐页版式配方 (图墙、演进图示、三线表、左图右步骤、图加公式、大数字等), 照着填内容即可"),
    "期刊黑白": dict(NAVY="1F2933", INK="1F2933", MUTE="6B7280", RULE="BFC5CC", ACC="256DB7", TINT="F3F4F6", head=22, body=18, panels="none", hl="256DB7", gap="1F2933",
                 desc="近黑标题, 全篇黑白灰, 只用模板亮蓝标本课题, 像期刊插图一样克制"),
    "浅色分区": dict(NAVY="274F7F", INK="1F2933", MUTE="5B6675", RULE="D5DCE5", ACC="B5651D", TINT="EAF0F6", head=22, body=18, panels="tint", hl="274F7F", gap="B5651D",
                 desc="用无边框浅蓝灰底块分组, 不用线框, 赭色点缀研究空白"),
    "深色重点": dict(NAVY="274F7F", INK="1F2933", MUTE="6B7280", RULE="C8D0DB", ACC="C9A227", TINT="F1F4F8", head=22, body=18, panels="dark", hl="1E3F66", gap="A33B2B",
                 desc="其余部分保持极简, 只把本课题的做法和关键数据放进深蓝反白块, 重点一眼可见"),
    "大字结论": dict(NAVY="274F7F", INK="1F2933", MUTE="6B7280", RULE="C8D0DB", ACC="A33B2B", TINT="F1F4F8", head=28, body=20, panels="none", hl="274F7F", gap="A33B2B",
                 desc="结论句放大到 28 磅, 每页要点更少, 证据靠图和大数字, 适合讲述节奏快的汇报"),
}


class Deck:
    def __init__(self, template: str | os.PathLike):
        self.prs = Presentation(str(template))
        slides = list(self.prs.slides)
        if len(slides) != 5:
            raise ValueError("模板应只含 5 张骨架页: 封面/目录/PART/内容/结束")
        self.proto = dict(zip(_ROLE_ORDER, slides))
        self._proto_ids = list(self.prs.slides._sldIdLst)
        self.warnings: list[str] = []
        self._tmp = Path(tempfile.mkdtemp(prefix="swust_kit_"))
        self._toc_items = None
        self._notes: list[tuple[int, int]] = []

    # ------------------------------------------------------------ 页面复制
    def _clone(self, role):
        src = self.proto[role]
        new = self.prs.slides.add_slide(src.slide_layout)
        for ph in list(new.placeholders):
            ph._element.getparent().remove(ph._element)
        # 背景
        src_bg = src._element.cSld.find(qn("p:bg"))
        if src_bg is not None:
            new._element.cSld.insert(0, copy.deepcopy(src_bg))
        rid_map = {}
        for rel in src.part.rels.values():
            if rel.reltype == _RT_IMAGE:
                rid_map[rel.rId] = new.part.relate_to(rel._target, _RT_IMAGE)
        tree = new.shapes._spTree
        for el in src.shapes._spTree.iterchildren():
            if el.tag in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
                continue
            e2 = copy.deepcopy(el)
            for node in e2.iter():
                for att in (qn("r:embed"), qn("r:link"), qn("r:id")):
                    v = node.get(att)
                    if v and v in rid_map:
                        node.set(att, rid_map[v])
            tree.append(e2)
        return new

    def _shape(self, slide, name):
        for sh in slide.shapes:
            if sh.name == name:
                return sh
        return None

    @staticmethod
    def _set_runs(par, texts):
        runs = par.runs
        for i, r in enumerate(runs):
            r.text = texts[i] if i < len(texts) else ""

    # ------------------------------------------------------------ 骨架页
    def cover(self, year, school, title, fields=None, title_size=None):
        s = self._clone("cover")
        for sh in s.shapes:
            if sh.has_text_frame and len(sh.text_frame.paragraphs) >= 3:
                p0 = sh.text_frame.paragraphs[0]
                self._set_runs(p0, [str(year), "年", school, "学位论文开题答辩"])
                p2 = sh.text_frame.paragraphs[2]
                self._set_runs(p2, [title])
                if title_size:
                    for r in p2.runs:
                        r.font.size = Pt(title_size)
            if sh.has_table and fields:
                for row in sh.table.rows:
                    key = row.cells[0].text.strip().rstrip("：:")
                    if key in fields:
                        cell = row.cells[1]
                        tf = cell.text_frame
                        tf.paragraphs[0].text = fields[key]
        return s

    def toc(self, items=None):
        s = self._clone("toc")
        if items:
            boxes = [sh for sh in s.shapes if sh.has_text_frame and sh.name == "文本框 33"]
            for sh, t in zip(boxes, items):
                self._set_runs(sh.text_frame.paragraphs[0], [t])
        self._toc_items = items
        return s

    def part(self, n, title):
        s = self._clone("part")
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            t = sh.text_frame.text
            if t.startswith("PART"):
                runs = [r for p in sh.text_frame.paragraphs for r in p.runs]
                if len(runs) >= 2:
                    runs[0].text = "PART"
                    runs[1].text = str(n)
                    for r in runs[2:]:
                        r.text = ""
            elif sh.name == "文本框 33":
                self._set_runs(sh.text_frame.paragraphs[0], [title])
        return s

    def content(self, n, label, subtitle=""):
        """内容页: n=部分编号, label=部分名称(小字), subtitle=本页小标题(大字)。"""
        s = self._clone("content")
        num = self._shape(s, "文本框 2")
        self._set_runs(num.text_frame.paragraphs[0], [str(n)])
        lab = self._shape(s, "矩形 11")
        self._set_runs(lab.text_frame.paragraphs[0], [label])
        lab.width = Cm(0.62 * len(label) + 0.4)
        sub = self._shape(s, "文本框 10")
        self._set_runs(sub.text_frame.paragraphs[0], [subtitle])
        sub.width = Cm(max(8, 0.9 * len(subtitle) + 1))
        pg = self._shape(s, "灯片编号占位符 1")
        idx = len(self.prs.slides) - 5  # 去掉 5 张骨架
        self._set_runs(pg.text_frame.paragraphs[0], [str(idx)])
        return s

    def end(self, year, school, date="", text=None):
        s = self._clone("end")
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            ps = sh.text_frame.paragraphs
            if len(ps) >= 3:
                self._set_runs(ps[0], [str(year), "年", school, "学位论文开题答辩"])
                if text:
                    self._set_runs(ps[2], [text])
            elif re.search(r"\d+年", sh.text_frame.text):
                self._set_runs(ps[0], [date])
        return s

    # ------------------------------------------------------------ 文字
    _MARK = re.compile(r"(\*\*.+?\*\*|__.+?__)")

    def _fill_par(self, p, text, size, color, bold, font=FONT):
        parts = self._MARK.split(text)
        for part in parts:
            if not part:
                continue
            r = p.add_run()
            c, b = color, bold
            if part.startswith("**") and part.endswith("**"):
                part, c, b = part[2:-2], RED, True
            elif part.startswith("__") and part.endswith("__"):
                part, c, b = part[2:-2], DARK, True
            r.text = part
            f = r.font
            f.size = Pt(size)
            f.bold = b
            f.color.rgb = _rgb(c)
            f.name = font
            rPr = r._r.get_or_add_rPr()
            for tag in ("a:ea", "a:cs"):
                el = rPr.find(qn(tag))
                if el is None:
                    el = etree.SubElement(rPr, qn(tag))
                el.set("typeface", font)

    def text(self, slide, x, y, w, h, paras, size=16, color=BLACK, bold=False,
             align="l", anchor="t", spacing=1.2, space_after=4, bullet=None,
             indent=0.0, margin=0.1, fit_check=True):
        """paras: 字符串列表; **x** 红色加粗, __x__ 深蓝加粗。bullet 可为 '•' '▶' 等。"""
        if isinstance(paras, str):
            paras = [paras]
        tb = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
        tf = tb.text_frame
        tf.word_wrap = True
        for side in ("left", "right", "top", "bottom"):
            setattr(tf, f"margin_{side}", Cm(margin))
        tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
        for i, t in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT, "j": PP_ALIGN.JUSTIFY}[align]
            p.line_spacing = spacing
            p.space_after = Pt(space_after)
            if bullet:
                pPr = p._p.get_or_add_pPr()
                pPr.set("marL", str(int(Cm(0.6))))
                pPr.set("indent", str(int(-Cm(0.6))))
                bu = etree.SubElement(pPr, qn("a:buChar"))
                bu.set("char", bullet)
            elif indent:
                pPr = p._p.get_or_add_pPr()
                pPr.set("indent", str(int(Cm(indent))))
            self._fill_par(p, t, size, color, bold)
        if fit_check:
            self._check_fit(slide, paras, w - 2 * margin - (0.6 if bullet else 0), h - 2 * margin, size, spacing, space_after)
        return tb

    @staticmethod
    def text_height(paras, w, size, spacing=1.2, space_after=4):
        """粗估文字高度(cm)。中文字宽≈字号, 西文≈0.55 字号。"""
        pt_cm = 2.54 / 72
        total = 0.0
        for t in paras:
            t = re.sub(r"\*\*|__", "", t)
            width = sum(size * pt_cm * (1.0 if ord(ch) > 0x2E80 else 0.55) for ch in t)
            lines = max(1, math.ceil(width / max(w, 0.1) - 1e-6))
            total += lines * size * pt_cm * spacing * 1.17 + space_after * pt_cm
        return total

    def _check_fit(self, slide, paras, w, h, size, spacing, space_after):
        need = self.text_height(paras, w, size, spacing, space_after)
        if need > h + 0.15:
            idx = len(self.prs.slides) - 5
            first = re.sub(r"\*\*|__", "", paras[0])[:16]
            self.warnings.append(f"第{idx}页 文字可能溢出: 需{need:.1f}cm 给{h:.1f}cm [{first}...]")

    # ------------------------------------------------------------ 形状
    def box(self, slide, x, y, w, h, fill=None, line=DARK, dash=False, radius=True,
            line_w=1.25, shadow=False):
        shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                     Cm(x), Cm(y), Cm(w), Cm(h))
        if radius:
            shp.adjustments[0] = min(0.12, 0.25 * 1.0 / max(h, 1))
        if fill is None:
            shp.fill.background()
        else:
            shp.fill.solid()
            shp.fill.fore_color.rgb = _rgb(fill)
        if line is None:
            shp.line.fill.background()
        else:
            shp.line.color.rgb = _rgb(line)
            shp.line.width = Pt(line_w)
            if dash:
                ln = shp.line._get_or_add_ln()
                pd = etree.SubElement(ln, qn("a:prstDash"))
                pd.set("val", "dash")
        if not shadow:
            spPr = shp._element.spPr
            etree.SubElement(spPr, qn("a:effectLst"))
        shp.text_frame.text = ""
        return shp

    def bar(self, slide, x, y, w, h, text, size=16, fill=DARK, color=WHITE, align="c", bold=True, radius=False):
        """[v1.1 旧版式, 有 AI 味, 新做的 PPT 不再使用, 见 references/08]"""
        shp = self.box(slide, x, y, w, h, fill=fill, line=None, radius=radius)
        tf = shp.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        for side in ("left", "right"):
            setattr(tf, f"margin_{side}", Cm(0.2))
        tf.margin_top = tf.margin_bottom = Cm(0.05)
        lines = text if isinstance(text, list) else text.split("\n")
        for i, t in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER}[align]
            self._fill_par(p, t, size, color, bold)
        return shp

    def card(self, slide, x, y, w, h, title, paras, size=14, title_size=16, title_h=1.0,
             fill=LIGHT2, line=DARK, dash=True, bullet=None, title_fill=DARK, spacing=1.2):
        """[v1.1 旧版式, 有 AI 味, 新做的 PPT 不再使用, 见 references/08] 带深蓝标题条的卡片。"""
        self.box(slide, x, y, w, h, fill=fill, line=line, dash=dash)
        self.bar(slide, x, y, w, title_h, title, size=title_size, fill=title_fill)
        return self.text(slide, x + 0.15, y + title_h + 0.15, w - 0.3, h - title_h - 0.25, paras,
                         size=size, bullet=bullet, spacing=spacing)

    def arrow(self, slide, x, y, w, h, direction="right", fill=BLUE):
        kind = {"right": MSO_SHAPE.RIGHT_ARROW, "down": MSO_SHAPE.DOWN_ARROW,
                "left": MSO_SHAPE.LEFT_ARROW, "up": MSO_SHAPE.UP_ARROW}[direction]
        shp = slide.shapes.add_shape(kind, Cm(x), Cm(y), Cm(w), Cm(h))
        shp.fill.solid()
        shp.fill.fore_color.rgb = _rgb(fill)
        shp.line.fill.background()
        etree.SubElement(shp._element.spPr, qn("a:effectLst"))
        return shp

    def circle_num(self, slide, x, y, d, n, fill=DARK, size=14):
        """[v1.1 旧版式, 有 AI 味, 新做的 PPT 不再使用, 见 references/08]"""
        shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Cm(x), Cm(y), Cm(d), Cm(d))
        shp.fill.solid()
        shp.fill.fore_color.rgb = _rgb(fill)
        shp.line.fill.background()
        etree.SubElement(shp._element.spPr, qn("a:effectLst"))
        tf = shp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        self._fill_par(p, str(n), size, WHITE, True, font="Times New Roman")
        return shp

    # ------------------------------------------------------------ 图片
    def picture(self, slide, path, x, y, w, h, caption=None, cap_h=0.75, cap_size=12, border=False):
        """把图片等比放进 (x,y,w,h) 框内居中; caption 为图下深蓝标签。"""
        from PIL import Image
        ph = h - (cap_h + 0.1 if caption else 0)
        with Image.open(path) as im:
            iw, ih = im.size
        r = min(w / iw, ph / ih)
        pw, pph = iw * r, ih * r
        px, py = x + (w - pw) / 2, y + (ph - pph) / 2
        pic = slide.shapes.add_picture(str(path), Cm(px), Cm(py), Cm(pw), Cm(pph))
        if border:
            pic.line.color.rgb = DARK
            pic.line.width = Pt(0.75)
        if caption:
            cw = min(max(pw, 0.62 * len(caption) * cap_size / 14 + 0.8), w)
            self.bar(slide, x + (w - cw) / 2, py + pph + 0.1, cw, cap_h, caption, size=cap_size)
        return pic

    # ------------------------------------------------------------ 表格
    def table(self, slide, x, y, w, rows, col_w=None, row_h=0.9, size=13, head_size=14,
              head_fill=DARK, zebra=(LIGHT, LIGHT2), align_cols=None, bold_first_col=False):
        nr, nc = len(rows), len(rows[0])
        gf = slide.shapes.add_table(nr, nc, Cm(x), Cm(y), Cm(w), Cm(row_h * nr))
        tbl = gf.table
        # 去掉默认样式
        tblPr = tbl._tbl.tblPr
        tblPr.set("firstRow", "0")
        tblPr.set("bandRow", "0")
        if col_w:
            tot = sum(col_w)
            for i, cw in enumerate(col_w):
                tbl.columns[i].width = Cm(w * cw / tot)
        for ri, row in enumerate(rows):
            tbl.rows[ri].height = Cm(row_h)
            for ci, val in enumerate(row):
                cell = tbl.cell(ri, ci)
                cell.margin_left = cell.margin_right = Cm(0.12)
                cell.margin_top = cell.margin_bottom = Cm(0.05)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf = cell.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                al = "c"
                if align_cols and ri > 0:
                    al = align_cols[ci]
                p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER}[al]
                if ri == 0:
                    self._fill_par(p, str(val), head_size, WHITE, True)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = _rgb(head_fill)
                else:
                    self._fill_par(p, str(val), size, BLACK, bold_first_col and ci == 0)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = _rgb(zebra[(ri - 1) % 2])
        return gf

    # ------------------------------------------------------------ 公式
    def _latex_png(self, latex):
        key = abs(hash(latex))
        out = self._tmp / f"f{key}.png"
        if out.exists():
            return out
        tex = (r"\documentclass[border=1pt,10pt]{standalone}\usepackage{amsmath,amssymb,bm}"
               r"\begin{document}$\displaystyle " + latex + r"$\end{document}")
        d = self._tmp / f"t{key}"
        d.mkdir(exist_ok=True)
        (d / "f.tex").write_text(tex, encoding="utf-8")
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "f.tex"], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if not (d / "f.pdf").exists():
            raise RuntimeError(f"LaTeX 渲染失败: {latex}")
        subprocess.run(["pdftoppm", "-r", "600", "-png", "-singlefile", "f.pdf", "f"], cwd=d, check=True)
        from PIL import Image
        im = Image.open(d / "f.png").convert("RGBA")
        px = im.load()
        for j in range(im.height):
            for i in range(im.width):
                r, g, b, a = px[i, j]
                lum = (r + g + b) / 3
                px[i, j] = (0x1A, 0x1A, 0x1A, int(255 - lum))
        im.save(out)
        return out

    def formula(self, slide, x, y, latex, size=18, color="1A1A1A", max_w=None, label=None):
        """插入可编辑公式(Office Math), 并附 LaTeX 渲染图作为兼容回退。返回 (w,h) cm。"""
        import sys
        sys.path.insert(0, str(HERE))
        from omml.formula_compiler import compile_latex_to_omml
        from omml.formula_run_properties import (merge_formula_control_properties,
                                                 merge_formula_run_properties,
                                                 serialize_styled_formula_omml)
        from xml.etree import ElementTree as ET
        from PIL import Image

        png = self._latex_png(latex)
        with Image.open(png) as im:
            iw, ih = im.size
        scale = size / 10.0
        w = iw / 600 * 2.54 * scale
        h = ih / 600 * 2.54 * scale
        if max_w and w > max_w:
            h, w = h * max_w / w, max_w
        pic = slide.shapes.add_picture(str(png), Cm(x), Cm(y), Cm(w), Cm(h))
        pic_el = pic._element

        DML = "http://schemas.openxmlformats.org/drawingml/2006/main"
        MATH = "http://schemas.openxmlformats.org/officeDocument/2006/math"
        root = ET.fromstring(compile_latex_to_omml(latex))
        ppr = root.find(f"{{{MATH}}}oMathParaPr")
        if ppr is None:
            ppr = ET.Element(f"{{{MATH}}}oMathParaPr")
            root.insert(0, ppr)
        jc = ET.SubElement(ppr, f"{{{MATH}}}jc")
        jc.set(f"{{{MATH}}}val", "left")
        rpr = ET.Element(f"{{{DML}}}rPr", {"lang": "en-US", "sz": str(int(size * 100)), "dirty": "0"})
        sf = ET.SubElement(rpr, f"{{{DML}}}solidFill")
        ET.SubElement(sf, f"{{{DML}}}srgbClr", {"val": color})
        for tag in ("latin", "ea", "cs"):
            ET.SubElement(rpr, f"{{{DML}}}{tag}", {"typeface": "Cambria Math"})
        for run in root.iter(f"{{{MATH}}}r"):
            merge_formula_run_properties(run, rpr)
        merge_formula_control_properties(root, rpr)
        omml = serialize_styled_formula_omml(root)

        sid = pic_el.nvPicPr.cNvPr.get("id")
        xml = f'''<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="{DML}" xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<mc:Choice Requires="a14"><p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="公式 {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{int(Cm(x))}" y="{int(Cm(y))}"/><a:ext cx="{int(Cm(w))}" cy="{int(Cm(h))}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"><a:spAutoFit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="l"/><a14:m>{omml}</a14:m></a:p></p:txBody></p:sp></mc:Choice>
<mc:Fallback/></mc:AlternateContent>'''
        ac = etree.fromstring(xml)
        parent = pic_el.getparent()
        parent.replace(pic_el, ac)
        ac.find("{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback").append(pic_el)
        if label:
            self.text(slide, x + w + 0.3, y + h / 2 - 0.45, 2.2, 0.9, [label], size=13, color=GRAY, fit_check=False, anchor="m")
        return w, h




    # ------------------------------------------------------------ 细线
    def line(self, slide, x1, y1, x2, y2, color="D0D7E2", width=0.75, dash=False):
        """细线(分隔、列边界)。只作结构线, 不作标题下的装饰线。"""
        from pptx.enum.shapes import MSO_CONNECTOR
        c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x1), Cm(y1), Cm(x2), Cm(y2))
        c.line.color.rgb = _rgb(color)
        c.line.width = Pt(width)
        if dash:
            ln = c.line._get_or_add_ln()
            pd = etree.SubElement(ln, qn("a:prstDash"))
            pd.set("val", "dash")
        return c


    # ------------------------------------------------------------ 学术极简规则(v1.2.0)
    # 全篇一套规则: 模板深蓝只用于标题和少数重点, 正文深灰黑, 一个暗红点缀, 浅灰细线分区,
    # 不用色条、编号圆、虚线框、通栏色块; 图注灰色小字; 每页顶部一句结论句。
    INK, MUTE, RULE, ACC, NAVY_HEX, TINT = "1F2933", "6B7280", "C8D0DB", "A33B2B", "274F7F", "F1F4F8"

    HEAD_SIZE = 22
    THEME = "学术极简"

    def set_theme(self, name):
        """切换整套风格(全篇统一的颜色、字号规则)。版式仍按每页内容选择, 不随风格固定。"""
        th = THEMES[name]
        self.THEME = name
        for k in ("INK", "MUTE", "RULE", "ACC", "TINT"):
            setattr(self, k, th[k])
        self.NAVY_HEX = th["NAVY"]
        self.HEAD_SIZE = th["head"]
        return th

    def headline(self, slide, text, size=None):
        """内容区顶部的结论句: 这一页要让评委记住的一句话。"""
        size = size or self.HEAD_SIZE
        h = 1.4 if size <= 24 else 1.8
        return self.text(slide, 1.6, 3.15, 30.7, h, [text], size=size, color=self.NAVY_HEX, bold=True, fit_check=False)

    def fig(self, slide, path, x, y, w, h, cap=None, cap_size=12, align="l"):
        """图片等比放入框内(顶部对齐), 下方灰色小字图注; 返回图片底边 y。"""
        from PIL import Image
        ph = h - (0.8 if cap else 0)
        with Image.open(path) as im:
            iw, ih = im.size
        r = min(w / iw, ph / ih)
        pw, pph = iw * r, ih * r
        px = x + (w - pw) / 2 if align == "c" else x
        slide.shapes.add_picture(str(path), Cm(px), Cm(y), Cm(pw), Cm(pph))
        if cap:
            cx, cw = (x, w) if align == "c" else (px, max(pw, w))
            self.text(slide, cx, y + pph + 0.1, cw, 0.8, [cap], size=cap_size, color=self.MUTE, align=align if align == "c" else "l", fit_check=False)
        return y + pph

    def rule_table(self, slide, x, y, col_w, rows, row_h, size=16, head_size=14, first_bold=True, colors=None, align=None):
        """学术三线表: 顶线、表头下线、底线, 行间浅灰细线, 无竖线无底色。rows[0] 为表头。返回底边 y。"""
        W = sum(col_w)
        self.line(slide, x, y, x + W, y, color=self.INK, width=1.5)
        yy = y + 0.05
        for ri, row in enumerate(rows):
            h = row_h[ri] if isinstance(row_h, (list, tuple)) else row_h
            xx = x
            for ci, cell in enumerate(row):
                c = self.MUTE if ri == 0 else (colors[ci] if colors else self.INK)
                b = ri == 0 or (first_bold and ci == 0)
                al = (align[ci] if align else "l")
                self.text(slide, xx + 0.15, yy, col_w[ci] - 0.3, h, cell.split("\n") if isinstance(cell, str) else cell,
                          size=head_size if ri == 0 else size, color=c, bold=b, anchor="m", align=al,
                          spacing=1.12, space_after=0, fit_check=False)
                xx += col_w[ci]
            yy += h
            if ri == 0:
                self.line(slide, x, yy, x + W, yy, color=self.INK, width=0.75)
            elif ri < len(rows) - 1:
                self.line(slide, x, yy, x + W, yy, color=self.RULE, width=0.5)
        self.line(slide, x, yy + 0.03, x + W, yy + 0.03, color=self.INK, width=1.5)
        return yy

    def big_number(self, slide, x, y, w, number, label, color=None, size=40, label_color=None):
        """大号数字 + 小字说明, 不加底色框。"""
        self.text(slide, x, y, w, size / 72 * 2.54 * 1.3, [number], size=size, color=color or self.NAVY_HEX, bold=True, fit_check=False)
        self.text(slide, x, y + size / 72 * 2.54 * 1.3, w, 1.0, [label], size=14, color=label_color or self.MUTE, fit_check=False)

    # ------------------------------------------------------------ 组合版式
    def chain(self, slide, x, y, w, items, h=1.5, gap=0.55, size=15, fills=None):
        """[v1.1 旧版式, 有 AI 味, 新做的 PPT 不再使用, 见 references/08] 竖向关键词链: 圆角条 + 向下箭头, 适合背景因果、技术路线步骤。"""
        for i, t in enumerate(items):
            yy = y + i * (h + gap)
            self.bar(slide, x, yy, w, h, t, size=size, fill=(fills[i] if fills else DARK), radius=True)
            if i < len(items) - 1:
                self.arrow(slide, x + w / 2 - 0.35, yy + h + 0.05, 0.7, gap - 0.1, "down")

    def class_row(self, slide, y, label, items, gap_text, x=1.4, label_w=3.4, item_w=19.0, h=1.0, size=13.5):
        """[v1.1 旧版式, 有 AI 味, 新做的 PPT 不再使用, 见 references/08] 研究现状分类条(仿往届做法): 左侧方向标签, 右侧若干亮蓝做法条, 最后一条灰色写不足。返回占用高度。"""
        n = len(items) + 1
        total = n * (h + 0.15) - 0.15
        self.bar(slide, x, y, label_w, total, label, size=15, fill=DARK, radius=True)
        xi = x + label_w + 0.3
        for i, t in enumerate(items):
            self.bar(slide, xi, y + i * (h + 0.15), item_w, h, t, size=size, fill=BLUE, align="l")
        self.bar(slide, xi, y + len(items) * (h + 0.15), item_w, h, gap_text, size=size, fill=GRAY, align="l")
        return total

    # ------------------------------------------------------------ 备注(讲稿)
    def notes(self, slide, text, ref=None):
        """写入本页备注。text 是要念的讲稿; ref 是备查内容(公式详解、可能的追问), 不念, 不计入时长。"""
        tf = slide.notes_slide.notes_text_frame
        body = text.strip()
        if ref:
            body += "\n\n【备查，不念】\n" + ref.strip()
        tf.text = body
        self._notes.append((len(self.prs.slides) - 5, len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", text))))
        return tf

    def notes_report(self, chars_per_min=250):
        """只数汉字与字母数字(标点不念), 按每分钟约 250 字估算讲稿时长, 返回 (总字数, 分钟)。"""
        total = sum(n for _, n in self._notes)
        for idx, n in self._notes:
            print(f"  第{idx:>2}页 备注 {n:>4} 字 ≈ {n / chars_per_min * 60:>4.0f} 秒")
        print(f"  合计 {total} 字 ≈ {total / chars_per_min:.1f} 分钟(按每分钟{chars_per_min}字)")
        return total, total / chars_per_min

    def blank_page(self, n, label, subtitle):
        """留白页: 只有页眉, 内容区空着, 供用户自行粘贴涉及个人隐私的成果。"""
        return self.content(n, label, subtitle)

    def picture_or_placeholder(self, slide, path, x, y, w, h, caption=None, **kw):
        """图片存在就放图; 不存在时放灰色虚线占位框并在框内写明缺哪张图。"""
        if path and Path(path).exists():
            return self.picture(slide, path, x, y, w, h, caption=caption, **kw)
        self.box(slide, x, y, w, h, fill=LIGHT2, line=GRAY, dash=True)
        self.text(slide, x, y, w, h, [f"待放入图片：{Path(str(path)).name if path else ''}", caption or ""],
                  size=12, color=GRAY, align="c", anchor="m", fit_check=False)
        self.warnings.append(f"第{len(self.prs.slides) - 5}页 缺少图片 {path}")
        return None

    # ------------------------------------------------------------ 保存
    def save(self, path):
        lst = self.prs.slides._sldIdLst
        for sid in self._proto_ids:
            self.prs.part.drop_rel(sid.rId)
            lst.remove(sid)
        self.prs.save(str(path))
        shutil.rmtree(self._tmp, ignore_errors=True)
        for w in self.warnings:
            print("[警告]", w)
        return path
