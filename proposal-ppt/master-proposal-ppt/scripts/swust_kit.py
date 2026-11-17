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
        shp = self.box(slide, x, y, w, h, fill=fill, line=None, radius=radius)
        tf = shp.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        for side in ("left", "right"):
            setattr(tf, f"margin_{side}", Cm(0.2))
        tf.margin_top = tf.margin_bottom = Cm(0.05)
        lines = text if isinstance(text, list) else [text]
        for i, t in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER}[align]
            self._fill_par(p, t, size, color, bold)
        return shp

    def card(self, slide, x, y, w, h, title, paras, size=14, title_size=16, title_h=1.0,
             fill=LIGHT2, line=DARK, dash=True, bullet=None, title_fill=DARK, spacing=1.2):
        """带深蓝标题条的卡片。"""
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
