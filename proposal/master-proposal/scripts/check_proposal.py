#!/usr/bin/env python3
"""开题报告 Markdown 稿件自检（只读，不修改文件）。

用法:
    python check_proposal.py 稿件.md [--json] [--targets targets.json]

稿件需使用 assets/proposal-skeleton.md 的标题层级：
    # 一、…  # 二、…  # 三、…  # 四、…  # 五、…  # 学位论文工作计划
    ## 1.1 …  ### 1.2.1 …   参考文献在“## 1.4 参考文献”下，每行以 [n] 开头。
正文引用写作 ^[n]^、^[3-6]^、^[2,5]^（也识别不带 ^ 的 [n]）。

检查项：各部分字数、参考文献数量/编号/格式/重复/未引用、引用首次出现顺序、
图表公式编号、研究内容条目长度与“方案细节”、称谓统一、“拟/已”时态、
常见套话与错别字、第五部分是否留给用户、工作计划时间顺序。
只能做格式与形式检查；文献真实性、内容正确性必须人工或联网核实。
"""
from __future__ import annotations

import argparse
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
DONE_WORDS = ["实现了", "验证了", "证明了", "取得了", "达到了", "完成了"]
REF_TYPE = re.compile(r"\[(J|C|M|D|R|S|P|N|A|G|Z|EB/OL|J/OL|M/OL|C/OL|D/OL|DB/OL|CP/OL)\]")


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
        warn(f"称谓混用：{ {w: voices[w] for w in used} }，建议统一为“本课题”或“本研究”。")
    for key in ("二", "三", "四"):
        if key in by_key:
            seg = strip_md(by_key[key][2])
            hits = {w: seg.count(w) for w in DONE_WORDS if seg.count(w)}
            if hits:
                warn(f"第{key}部分出现完成时表述 {hits}：开题阶段未完成的工作应写“拟……”。")
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
        err("缺少“五、研究基础与工作条件”（由用户本人撰写，但需保留标题与提醒）。")

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
