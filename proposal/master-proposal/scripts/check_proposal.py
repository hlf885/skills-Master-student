#!/usr/bin/env python3
"""开题报告 Markdown 稿件自检（只读，不修改文件）。

用法:
    python check_proposal.py 稿件.md [--json] [--targets targets.json] [--specs 图规格目录]

稿件需使用 assets/proposal-skeleton.md 的标题层级：
    # 一、…  # 二、…  # 三、…  # 四、…  # 五、…  # 学位论文工作计划
    ## 1.1 …  ### 1.2.1 …   参考文献在“## 1.4 参考文献”下，每行以 [n] 开头。
正文引用写作 ^[n]^、^[3-6]^、^[2,5]^（也识别不带 ^ 的 [n]）。

检查项：各部分字数、参考文献数量/编号/格式/重复/未引用、引用首次出现顺序、
图表公式编号、研究内容条目长度与“方案细节”、称谓统一、“拟/已”时态、
常见套话与错别字、第五部分是否留给用户、工作计划时间顺序；
元叙述与“聊天/思考”式句子、项目口吻（“本课题”“项目”频次）、自我设限式条件句、
插图数量与文献原图、技术路线图成果栏是否写了论文（需 --specs）。
只能做格式与形式检查；文献真实性、内容正确性必须人工或联网核实。
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

DEFAULT_TARGETS = OrderedDict(
    [
        ("1.1", (1300, 1900)),
        ("1.2", (4000, 6000)),
        ("1.3", (600, 1100)),
        ("一", (7000, 8500)),
        ("二", (2800, 3600)),
        ("三", (5000, 6500)),
        ("四", (600, 900)),
    ]
)
HARD_MIN = {"一": 800, "二": 2500, "三": 800, "四": 500, "五": 500}
REF_RANGE = (56, 66)

AI_PHRASES = [
    "赋能", "助力", "深度融合", "全方位", "多维度", "无缝", "至关重要", "不可或缺", "彰显",
    "奠定了坚实的基础", "奠定坚实基础", "重大而深远", "具有重要的意义", "广阔的应用前景",
    "飞速发展", "日新月异", "不仅是", "更是", "值得注意的是", "众所周知", "毋庸置疑",
    "填补了", "首次", "国际领先", "国内领先", "开创性", "前所未有", "堪称", "极具挑战性",
    "让我们", "本节将", "下面将", "接下来将",
]
TYPOS = {
    "选代": "迭代", "必可或缺": "必不可少/不可或缺", "部份": "部分", "做为": "作为",
    "既使": "即使", "在次": "再次", "按装": "安装", "园满": "圆满", "竟管": "尽管",
    "截止目前": "截至目前", "考虑到了": "考虑到", "机械臂臂": "机械臂",
}
METHOD_HINTS = [
    "采用", "利用", "借助", "通过", "算法", "公式", "Unity", "ROS", "MATLAB", "Matlab", "Python",
    "SolidWorks", "Gazebo", "神经网络", "损失函数", "奖励函数", "卡尔曼", "RRT", "PPO", "SAC",
]
PM_WORDS = ["项目方", "降级", "退路", "人·月", "人月", "难度最大", "难度较低", "项目进度", "设备进度"]
BACKGROUND_WATCH = ["遥操作"]
# 元叙述、讲稿式过渡、把思考过程写进正文的句子（V3 审阅意见 1、3、5、8、10）
META_PHRASES = [
    "本节对应", "对应关键问题", "下面分别说明", "下面分别介绍", "下面从", "下面对", "第一部分说明", "第二部分说明",
    "后两部分对应", "前两部分", "以上为拟创新点", "最终表述将", "口径", "前期验证后", "中期检查时一并说明",
    "需要说明的是", "需要指出的是", "本节建模指", "本节目标是", "本节的目标", "目标是建立可供", "具体条件按",
    "不是本课题的研究内容", "不属于本课题",
    # 1.4.0（存在的问题-V6）
    "由此提出", "呈现以下", "据此，本课题拟", "据此本课题拟", "依托实验室承担", "实验室承担的",
]
# 自我设限、先给自己留退路的条件句（专家会追问“条件不具备怎么办”）
HEDGE_PHRASES = ["条件具备时", "条件具备后", "具备条件后", "现场条件具备", "设备与场地条件具备", "经项目方许可", "若条件允许", "如条件允许", "视情况"]
DONE_WORDS = ["实现了", "验证了", "证明了", "取得了", "达到了", "完成了"]
REF_TYPE = re.compile(r"\[(J|C|M|D|R|S|P|N|A|G|Z|EB/OL|J/OL|M/OL|C/OL|D/OL|DB/OL|CP/OL|PP/OL|PP)\]")


def strip_md(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"^\s*\|?\s*:?-{3,}.*$", "", text, flags=re.M)
    text = re.sub(r"[#*`>|]", "", text)
    return text


def count_chars(text: str) -> int:
    return len(re.sub(r"\s", "", strip_md(text)))


def parse_sections(md: str):
    """Return ordered list of (level, key, title, body) where key is 一/二/…/1.1/1.2.1/计划."""
    lines = md.splitlines()
    heads = []
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.*\S)\s*$", ln)
        if not m:
            continue
        level, title = len(m.group(1)), m.group(2)
        key = None
        m1 = re.match(r"^([一二三四五])、", title)
        m2 = re.match(r"^(\d+(?:\.\d+)+)\s*", title)
        if m1:
            key = m1.group(1)
        elif "工作计划" in title:
            key = "计划"
        elif m2:
            key = m2.group(1)
        heads.append((i, level, key, title))
    out = []
    for n, (i, level, key, title) in enumerate(heads):
        end = len(lines)
        for j, lv2, _, _ in heads[n + 1:]:
            if lv2 <= level:
                end = j
                break
        out.append((level, key, title, "\n".join(lines[i + 1:end])))
    return out


def expand_cites(spec: str) -> list[int]:
    nums: list[int] = []
    for part in re.split(r"[,，]", spec):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*[-–—~]\s*(\d+)", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b and b - a < 50:
                nums.extend(range(a, b + 1))
        elif part.isdigit():
            nums.append(int(part))
    return nums


def norm_title(ref: str) -> str:
    body = re.sub(r"^\[\d+\]\s*", "", ref)
    m = re.search(r"\.\s*(.+?)\[[A-Z/]+\]", body)
    t = m.group(1) if m else body
    return re.sub(r"[\W_]+", "", t.lower())


def has_cjk(s: str) -> bool:
    return re.search(r"[\u4e00-\u9fff]", s) is not None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path)
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--targets", type=Path, help="自定义字数目标 JSON，如 {\"二\": [2800, 3600]}")
    ap.add_argument("--specs", type=Path, help="图规格 JSON 所在目录，用于检查技术路线图成果栏")
    args = ap.parse_args()

    md = args.file.read_text(encoding="utf-8")
    targets = OrderedDict(DEFAULT_TARGETS)
    if args.targets:
        for k, v in json.loads(args.targets.read_text(encoding="utf-8")).items():
            targets[k] = tuple(v)

    secs = parse_sections(md)
    by_key = {k: (lvl, title, body) for lvl, k, title, body in secs if k}
    issues: list[tuple[str, str]] = []  # (level, message)
    report: dict = {"file": str(args.file), "word_counts": {}, "references": {}, "issues": []}

    def warn(msg: str) -> None:
        issues.append(("警告", msg))

    def err(msg: str) -> None:
        issues.append(("错误", msg))

    # ---------- 参考文献 ----------
    ref_key = next((k for k, (l, t, b) in by_key.items() if "." in k and "参考文献" in t), None)
    refs: list[str] = []
    if ref_key:
        for ln in by_key[ref_key][2].splitlines():
            m = re.match(r"^\s*\[(\d+)\]\s*(.*)$", ln)
            if m and m.group(2).strip():
                refs.append(ln.strip())
    else:
        err("未找到“参考文献”小节（应为“## 1.4 参考文献”）。")

    # ---------- 字数 ----------
    def body_without_refs(key: str) -> str:
        lvl, title, body = by_key[key]
        if ref_key and key == "一":
            ref_body = by_key[ref_key][2]
            body = body.replace(ref_body, "")
        return body

    for key, (lo, hi) in targets.items():
        if key not in by_key:
            if key in {"1.1", "1.2", "1.3", "一", "二", "三", "四"}:
                err(f"缺少部分：{key}")
            continue
        n = count_chars(body_without_refs(key))
        status = "OK" if lo <= n <= hi else ("偏少" if n < lo else "偏多")
        report["word_counts"][key] = {"chars": n, "target": [lo, hi], "status": status}
        if status != "OK":
            warn(f"{key} 字数 {n}，目标 {lo}–{hi}（{status}）。")
    for key, mn in HARD_MIN.items():
        if key in by_key and key != "五":
            n = count_chars(body_without_refs(key))
            if n < mn:
                err(f"{key} 仅 {n} 字，低于表格要求的“不少于 {mn} 字”。")

    # ---------- 参考文献格式 ----------
    nums = [int(re.match(r"\[(\d+)\]", r).group(1)) for r in refs]
    report["references"]["count"] = len(refs)
    if refs:
        if not (REF_RANGE[0] <= len(refs) <= REF_RANGE[1]):
            err(f"参考文献 {len(refs)} 条，要求 {REF_RANGE[0]}–{REF_RANGE[1]} 条。")
        if nums != list(range(1, len(nums) + 1)):
            err("参考文献编号不连续或不从 [1] 开始。")
        titles = Counter(norm_title(r) for r in refs)
        dups = [t for t, c in titles.items() if c > 1 and len(t) > 8]
        if dups:
            err(f"疑似重复文献 {len(dups)} 组：" + "；".join(r for r in refs if norm_title(r) in dups)[:300])
        for r in refs:
            no = r.split("]")[0] + "]"
            body = r[len(no):]
            if not REF_TYPE.search(body):
                warn(f"{no} 缺少文献类型标识（[J]/[C]/[M]/[D]/[EB/OL] 等）。")
            if re.search(r"[，。：；（）]", body) and has_cjk(body) is False:
                warn(f"{no} 外文文献中含全角标点。")
            if has_cjk(body) and re.search(r"et al", body):
                warn(f"{no} 中文文献应使用“等”，不用 et al。")
            if not has_cjk(body) and "等" in body:
                warn(f"{no} 外文文献应使用 et al。")
            if re.search(r"\d\s*[~～]\s*\d", body):
                warn(f"{no} 页码范围应使用半角连字符“-”。")
            if re.search(r"\]\.\S", body) and not re.search(r"\]\.\s", body):
                warn(f"{no} 类型标识后的句点后应空一格。")

    # 1.3.0：近三年占比与预印本标识
    if refs:
        this_year = datetime.date.today().year
        years = []
        for r in refs:
            ys = [int(y) for y in re.findall(r"(?<![\d./-])((?:19|20)\d\d)(?![\d-])", r)]
            ys = [y for y in ys if 1950 <= y <= this_year + 1]
            if ys:
                years.append(ys[0])
        recent = sum(1 for y in years if y >= this_year - 2)
        report["references"]["recent3"] = recent
        if years and recent * 2 < len(refs):
            warn(f"近三年（{this_year - 2}–{this_year}）文献约 {recent} 条，不足一半（共 {len(refs)} 条）：补充近两年的高水平文献。")
        for r in refs:
            if re.search(r"\[PP(?:/OL)?\]|arXiv|preprint|预印本", r, re.I):
                warn(r.split("]")[0] + "] 疑似未正式发表的预印本：开题报告只引用已正式发表的文献，改引正式版本或换文献（1.5.0）。")
        # 1.5.0：2020 年以前的文献
        old = [y for y in years if y < 2020]
        report["references"]["before2020"] = len(old)
        if old:
            warn(f"2020 年以前的文献 {len(old)} 条：只保留方案中直接使用的算法、工具、定理的原始出处，概念类改引近年文献。")

    # ---------- 正文引用顺序 ----------
    text_wo_refs = md
    if ref_key:
        text_wo_refs = md.replace(by_key[ref_key][2], "")
    text_wo_refs = re.sub(r"<!--.*?-->", "", text_wo_refs, flags=re.S)
    # 公式中的区间（如 s∈[0,1]）不是引用：先去掉行间与行内公式
    text_wo_refs = re.sub(r"\$\$.*?\$\$", "", text_wo_refs, flags=re.S)
    text_wo_refs = re.sub(r"\$[^$\n]+\$", "", text_wo_refs)
    cites = []
    for m in re.finditer(r"\^?\[(\d+(?:\s*[-–—~,，]\s*\d+)*)\]\^?", text_wo_refs):
        cites.extend(expand_cites(m.group(1)))
    first_seen: list[int] = []
    for c in cites:
        if c not in first_seen:
            first_seen.append(c)
    report["references"]["cited_unique"] = len(first_seen)
    disorder = [c for i, c in enumerate(first_seen) if i > 0 and c < max(first_seen[:i]) and c != i + 1]
    if first_seen and first_seen != sorted(first_seen):
        bad = [f"[{c}]" for c in first_seen if first_seen.index(c) + 1 != c][:10]
        err("正文首次引用顺序不是递增：" + "、".join(bad) + " 等（顺序编码制要求按首次出现编号）。")
    if refs:
        uncited = sorted(set(nums) - set(first_seen))
        missing = sorted(set(first_seen) - set(nums))
        if uncited:
            err(f"列表中未被正文引用的文献：{uncited[:20]}")
        if missing:
            err(f"正文引用了列表中不存在的编号：{missing[:20]}")
    del disorder

    # ---------- 图、表、公式编号 ----------
    def check_seq(kind: str, items: list[str]) -> None:
        seen = Counter(items)
        d = [k for k, v in seen.items() if v > 1]
        if d:
            err(f"{kind}编号重复：{d}")
        per_ch: dict[str, list[int]] = {}
        for it in items:
            ch, no = re.split(r"[-.]", it)
            per_ch.setdefault(ch, []).append(int(no))
        for ch, lst in per_ch.items():
            if sorted(set(lst)) != list(range(1, max(lst) + 1)):
                warn(f"{kind}第 {ch} 章编号不连续：{sorted(set(lst))}")
        styles = {("-" if "-" in it else ".") for it in items}
        if len(styles) > 1:
            warn(f"{kind}编号体例混用（如 1-1 与 1.1）。")

    fig_caps = re.findall(r"!\[\s*图\s*(\d+[-.]\d+)", md) + re.findall(r"^\s*图\s*(\d+[-.]\d+)[\s　]", md, flags=re.M)
    tab_caps = re.findall(r"^\s*表\s*(\d+[-.]\d+)[\s　]", md, flags=re.M)
    eq_tags = re.findall(r"\\tag\{(\d+[-.]\d+)\}", md) + re.findall(r"^\s*[（(](\d+[-.]\d+)[）)]\s*$", md, flags=re.M)
    for kind, items in (("图", fig_caps), ("表", tab_caps), ("公式", eq_tags)):
        if items:
            check_seq(kind, items)
    for f in sorted(set(fig_caps)):
        if not re.search(rf"如图\s*{re.escape(f)}|图\s*{re.escape(f)}\s*所示|见图\s*{re.escape(f)}", md):
            warn(f"图{f} 在正文中未被提及（如“如图{f}所示”）。")
    report["figures"] = len(set(fig_caps))
    nfig = len(set(fig_caps))
    if nfig and nfig < 12:
        warn(f"全文插图 {nfig} 幅，同领域样本多为 13–25 幅：可在 1.2 各小节补充代表性工作的文献原图，在 3.2 补充模型截图、原理图。")
    lit_figs = re.findall(r"!\[\s*图\s*\d+[-.]\d+[^\]\n]*\^\[\d", md) + re.findall(r"^\s*图\s*\d+[-.]\d+ [^\n]*\^\[\d", md, flags=re.M)
    report["literature_figures"] = len(lit_figs)
    if nfig and not lit_figs:
        warn("没有带文献引用的图题：1.2 研究现状中宜插入代表性工作的原图（清晰、无水印、图题后标注引用）。")
    report["tables"] = len(set(tab_caps))
    report["equations"] = len(set(eq_tags))

    # ---------- 研究内容条目 ----------
    if "2.1" in by_key:
        body = by_key["2.1"][2]
        item_head = r"(?:[（(]\d[）)]|[①②③④⑤⑥]|\d[）)])"
        items = re.split(rf"\n\s*(?={item_head})", "\n" + body)
        content_items = [it.strip() for it in items if re.match(item_head, it.strip())]
        report["research_content_items"] = len(content_items)
        if not 3 <= len(content_items) <= 5:
            warn(f"2.1 识别到 {len(content_items)} 项研究内容，模板通常为 3–4 项（含系统集成/实验验证）。")
        for it in content_items:
            head = it.splitlines()[0][:20]
            n = count_chars(it)
            if n > 260:
                warn(f"研究内容“{head}…”约 {n} 字，超过 4–5 行（约 120–220 字），请浓缩为一句核心话。")
            hits = [w for w in METHOD_HINTS if w in it]
            if len(hits) >= 2:
                warn(f"研究内容“{head}…”含方案性词语 {hits[:5]}，研究内容只说做什么，不说怎么做。")

    # ---------- 称谓、时态、套话、错别字 ----------
    plain = strip_md(text_wo_refs)
    # 学校模板的栏目名“四、本研究课题可能的创新之处”不计入称谓统计
    plain_voice = re.sub(r"本研究课题可能的创新之处", "", plain)
    voices = {w: plain_voice.count(w) for w in ("本文", "本课题", "本研究", "我们")}
    used = [w for w, c in voices.items() if c]
    if len(used) > 1:
        warn(f"称谓混用：{ {w: voices[w] for w in used} }，统一为“本课题”。")
    # 1.5.0：“本文”“文中”“本研究”一律改为“本课题”
    bad_voice = {"本文": plain_voice.count("本文"), "本研究": plain_voice.count("本研究"),
                 "文中": len(re.findall(r"(?<![论正英原全译])文中", plain_voice))}
    bad_voice = {k: v for k, v in bad_voice.items() if v}
    if bad_voice:
        warn(f"出现 {bad_voice}：指称课题统一用“本课题”。")
    # 1.6.0：引号、破折号、箭头（用户认为成段出现有 AI 味）
    punct = {"双引号": len(re.findall(r"[“”\"]", plain)) // 2, "破折号": plain.count("——"), "箭头": len(re.findall(r"[→⟶⇒]", plain))}
    punct = {k: v for k, v in punct.items() if v}
    if punct:
        warn(f"正文中有 {punct}：少用引号、破折号和箭头（07 第十一节）。")
    # 1.7.0：口语化说法（用户指出一处后要全文排查）
    COLLOQ = ["停在哪里", "停在什么位置", "以什么构型停住", "停住", "够不到", "够得着", "会不会", "看似",
              "搞清", "搞定", "弄清", "卡壳", "大显身手", "合拍", "一下子", "说白了", "啥"]
    colloq = {w: plain.count(w) for w in COLLOQ if plain.count(w)}
    if colloq:
        warn(f"口语化说法 {colloq}：改为书面表述，并全文排查同类说法（07 第十节）。")
    # 1.5.0：数字与单位之间的空格是否统一
    spaced = len(re.findall(r"\d\s+(?:mm|cm|km|m|kg|Hz|ms|s|°)(?![A-Za-z])", plain))
    tight = len(re.findall(r"\d(?:mm|cm|km|m|kg|Hz|ms|s)(?![A-Za-z])", plain))
    if spaced and tight:
        warn(f"数字与单位之间有空格 {spaced} 处、无空格 {tight} 处：按用户习惯全文统一。")
    for key in ("二", "三", "四"):
        if key in by_key:
            seg = strip_md(by_key[key][2])
            hits = {w: seg.count(w) for w in DONE_WORDS if seg.count(w)}
            if hits:
                warn(f"第{key}部分出现完成时表述 {hits}：开题阶段未完成的工作应写“拟……”。")
    # 1.3.0：人称代词
    pron_src = re.sub(r"来论述其|及其可行性", "", plain)  # 学校模板栏目原文
    pron = {w: len(re.findall(w, pron_src)) for w in ("我们", "我国", "我(?![们国])", "你", "他(?!们)", "她", "它", "其(?![中余他次实])")}
    pron = {k.split("(")[0]: v for k, v in pron.items() if v}
    if pron:
        warn(f"出现人称代词 {pron}：省略主语或重复名词（“其他”等已排除，“其”请逐处判断是否作代词）。")
    # 1.4.0：分号（“式中，……；……”符号说明除外）
    semi_lines = [ln for ln in plain.split("\n") if "；" in ln and not ln.lstrip().startswith("式中")]
    n_semi = sum(ln.count("；") for ln in semi_lines)
    if n_semi:
        warn(f"正文出现分号 {n_semi} 处（“式中”符号说明除外）：能用句号或逗号的都改掉，一句话写一件事。")
    ai = {p: plain.count(p) for p in AI_PHRASES if plain.count(p)}
    if ai:
        warn(f"模板化/拔高表达（逐条判断是否需要改）：{ai}")
    if plain.count("综上所述") > 4:
        warn(f"“综上所述”出现 {plain.count('综上所述')} 次，收尾句式重复。")
    typo = {k: v for k, v in TYPOS.items() if k in plain}
    if typo:
        err(f"疑似错别字：{typo}")
    if re.search(r"[\u4e00-\u9fff][,;:?!][\u4e00-\u9fff]", plain):
        warn("中文正文中出现半角标点（, ; : ? !）。")

    # ---------- 图表题与公式写法 ----------
    if re.search(r"(?:!\[\s*)?[图表]\s*\d+[-.]\d+\u3000", md):
        warn("图题或表题的图号与标题之间是全角空格（Word 中常显示为方框），请改为一个半角空格。")
    bad_tex = [w for w, pat in (("\\boldsymbol/\\mathbf 加粗", r"\\(?:boldsymbol|mathbf)\{"), ("左上标 {}^", r"\{\}\^"), ("花体 \\mathcal", r"\\mathcal\{")) if re.search(pat, md)]
    if bad_tex:
        warn(f"公式中出现 {bad_tex}：模板公式不加粗、不用左上标和花体，请按 05 号规范改写。")

    # ---------- 元叙述、自我设限、项目口吻 ----------
    meta = {p: plain.count(p) for p in META_PHRASES if plain.count(p)}
    if meta:
        warn(f"元叙述或思考过程式句子 {meta}：开题报告直接写内容，不写“本节对应……”“下面分别说明……”“需要说明的是……”之类的讲稿和说明句。")
    hedge = {p: plain.count(p) for p in HEDGE_PHRASES if plain.count(p)}
    if hedge:
        warn(f"自我设限式条件句 {hedge}：实验与验证按计划直接写（如“开展虚实联合验证”），不要从开题起就给自己留条件。")
    n_topic = plain_voice.count("本课题")
    if n_topic > 12:
        warn(f"“本课题”出现 {n_topic} 次（样本多为 4–12 次）：多数句子可以直接以研究对象或方法作主语。")
    proj_outside = plain.count("项目") - (strip_md(by_key["1.1"][2]).count("项目") if "1.1" in by_key else 0)
    if proj_outside > 3:
        warn(f"1.1 以外“项目”出现约 {proj_outside} 次：依托项目在 1.1 说明一次即可，后文用研究对象、设计资料、装置等表述，保持学术研究而非项目报告的口吻。")

    # ---------- 技术路线图 ----------
    if args.specs and args.specs.is_dir():
        for f in sorted(args.specs.glob("*.json")):
            try:
                sp = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if "技术路线" not in str(sp.get("title", "")):
                continue
            bad = [n.get("text", "").replace("\n", " ") for n in sp.get("nodes", []) if re.search(r"论文|专利|软著", n.get("text", ""))]
            if bad:
                warn(f"{f.name} 技术路线图出现 {bad}：技术路线写研究步骤与阶段成果，论文、专利等写在工作计划里。")

    # ---------- 可行性分析（学生视角、学术研究） ----------
    feas_key = next((k for k, (l, t, b) in by_key.items() if k.startswith("3.") and "可行性" in t), None)
    if feas_key:
        fb = by_key[feas_key][2]
        if re.search(r"\^\[\d", fb):
            warn("3.3 可行性分析中出现文献引用：可行性分析写本人的理论基础、技术储备和研究条件，不需要引用文献。")
        pm = [w for w in PM_WORDS if w in fb]
        if pm:
            warn(f"3.3 可行性分析含项目管理式表述 {pm}：开题是学术研究，难度分级、降级退路、谁提供数据等放在内部评估表，不写进正文。")
        if not re.search(r"理论基础", fb) or not re.search(r"技术储备|技术基础", fb) or not re.search(r"研究条件|工作条件", fb):
            warn("3.3 可行性分析建议按“理论基础—技术储备—研究条件”三方面展开，并以学生本人的视角写。")
    tech = by_key.get("1.1", (0, "", ""))[2] + by_key.get("1.2", (0, "", ""))[2]
    for w in BACKGROUND_WATCH:
        n = tech.count(w)
        if n >= 8:
            warn(f"立题依据中“{w}”出现 {n} 次：若课题本身不研究它，应弱化为背景并说明研究边界，避免专家误判研究方向。")

    # ---------- 第五部分 ----------
    if "五" in by_key:
        b5 = by_key["五"][2]
        if "请本人撰写" not in b5 and count_chars(b5) < 500:
            warn("第五部分不足 500 字；该部分须由用户本人撰写，请提醒用户补写。")
        elif "请本人撰写" in b5:
            warn("第五部分仍是占位提纲，交付时须醒目提醒用户本人撰写（≥500 字）。")
    else:
        err("缺少“五、研究基础与工作条件”（依据用户已完成的工作撰写；没有材料时保留标题与提纲）。")

    # ---------- 工作计划 ----------
    if "计划" in by_key:
        spans = re.findall(r"(\d{4})\.(\d{1,2})\s*[-–—~至]+\s*(\d{4})\.(\d{1,2})", by_key["计划"][2])
        prev_end = None
        for y1, m1, y2, m2 in spans:
            s, e = int(y1) * 12 + int(m1), int(y2) * 12 + int(m2)
            if e < s:
                err(f"工作计划时间倒置：{y1}.{m1}-{y2}.{m2}")
            if prev_end is not None and s < prev_end:
                warn(f"工作计划时间段重叠或倒序：{y1}.{m1} 开始早于上一段结束")
            prev_end = e
        if spans and not re.search(r"中期", by_key["计划"][2]):
            warn("工作计划中没有标出中期检查节点。")

    report["issues"] = [{"level": lv, "message": m} for lv, m in issues]
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"== 开题报告自检：{args.file.name} ==")
        print("[字数]")
        for k, v in report["word_counts"].items():
            print(f"  {k:<4} {v['chars']:>6} 字   目标 {v['target'][0]}–{v['target'][1]}   {v['status']}")
        r = report["references"]
        print(f"[文献] 列表 {r.get('count', 0)} 条，正文引用 {r.get('cited_unique', 0)} 条")
        print(f"[图表] 图 {report.get('figures', 0)}  表 {report.get('tables', 0)}  公式 {report.get('equations', 0)}")
        if "research_content_items" in report:
            print(f"[研究内容] {report['research_content_items']} 项")
        print(f"[问题] {len(issues)} 条")
        for lv, m in issues:
            print(f"  - {lv}：{m}")
        print("说明：本脚本只做形式检查；文献真实性、论述正确性须人工核实。")
    return 1 if any(lv == "错误" for lv, _ in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
