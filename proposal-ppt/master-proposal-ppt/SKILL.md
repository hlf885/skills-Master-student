---
name: master-proposal-ppt
description: >-
  依据已定稿的中文工科硕士开题报告（docx），在学校原生开题答辩模板上制作开题答辩 PPT（pptx）。
  先学习本校往届开题 PPT 的结构与篇幅，再按 立题依据/研究内容与目标/研究方案/创新点/研究基础与工作条件/研究计划
  六部分逐页规划，用模板母版、页眉和配色生成可编辑的幻灯片，每页配讲稿备注并按汇报时长控制总字数，
  研究背景可配有授权的真实网络图片，公式为可编辑 Office Math，最后渲染逐页检查。
  默认演示模板为西南科技大学，可从任意学校的往届 PPT 抽取模板替换。
  Use for Chinese master's thesis proposal defense slides (开题答辩PPT, 开题PPT, proposal defense deck).
metadata:
  version: "1.1.0"
  repository: "https://github.com/hlf885/skills-Master-student"
  project: "proposal-ppt"
---

# 硕士开题答辩 PPT（master-proposal-ppt）

## 定位

把**已经写好的开题报告**变成答辩用的 PPT。PPT 只做浓缩、排版和可视化，不新增开题报告里没有的事实、数据、文献或结论。开题报告的写作与修改交给 `master-proposal`。

方法来源：学习了 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) 的工作流（见 `references/05-ppt-master-notes.md`）。本 Skill 采用其中的原生模板路线：保留学校模板的母版、版式、页眉页脚和配色，只往页面里填内容；公式沿用 ppt-master 的 LaTeX 转 Office Math 编译器（MIT 许可，已随 `scripts/omml/` 附带）。

## 不可违反的硬性规则

1. **内容只来自开题报告。** 每一句话、每个数字、每张图都能在用户提供的开题报告（或用户在对话中明确给出的材料）里找到出处。可以删减、合并、改成短句，不可以补充、推测或夸大。开题报告里写“拟”“初步”“示意”的，PPT 里照样保留。唯一的例外是研究背景页的配图：可以补充开题报告里没有、但与课题直接相关的**真实照片**，必须从网上找真实清晰、授权允许使用的图片（优先 Wikimedia Commons 等注明许可的来源），在页面上注明来源与许可；不得自己画、不得用 AI 生成，规则见 `references/07-notes-and-images.md`。
2. **个人信息留空。** 封面的答辩人、专业、学号、指导老师默认留空，由用户自己填写；不要从记忆或其他文件里填。
3. **学校名称是占位。** 演示模板为西南科技大学。用户换成本校模板时，用 `scripts/make_template.py` 从本校往届 PPT 抽取，或让用户自己替换封面、结束页的学校名和标志。
4. **书面规范与开题报告一致。** 不用引号和破折号，研究方案小标题写成 研究一：××，不写 研究方案1——××；不用 本文、我们；术语、符号、公式编号与开题报告一致。
5. **往届 PPT 只学结构。** 往届同学的 PPT 只用于学习页面结构、篇幅和版式，不复制其文字和图片；不得把往届 PPT 或未公开的开题报告上传到公开仓库，仓库里只保留统计结果。
6. **每页必须有备注讲稿，总时长按用户要求控制。** 用户答辩时照着备注念、同时翻页，所以页面文字只留关键词、短句和图，完整的话写进备注。汇报时长默认按 8 到 10 分钟准备，讲稿按每分钟约 250 字（不计标点）控制总量，`swust_kit.notes_report()` 会逐页估算。
7. **研究基础留一页空白。** 研究基础与工作条件部分固定留一页只有页眉的空白页，供用户自己粘贴涉及个人隐私的比赛获奖、论文、专利等成果，不替用户填写，也不从记忆或其他文件里找。
8. **生成后必须渲染检查。** 用 `scripts/render_check.py` 渲染全部页面，逐页看是否溢出、遮挡、错位、图片变形、字太小；`swust_kit` 打印的溢出警告必须逐条处理或确认无误后再交付。

## 工作流程

### 阶段 1　收集材料（先问清再动手）

向用户确认并拿到：
- 最新版开题报告 docx（以文件名版本号最大、修改时间最新者为准，拿不准就问）；
- 本校往届开题答辩 PPT 一到多份（用于抽模板和学篇幅），没有就用自带的西南科技大学模板；
- 汇报时长（决定页数和讲稿字数，见 `references/02-deck-structure.md` 第二节；没说就按 8 到 10 分钟）、答辩日期；
- 是否已有专门为 PPT 画的图；没有就直接用开题报告里的图。

### 阶段 2　学习模板与往届篇幅

1. `python3 scripts/outline_dump.py 往届PPT目录 --stats` 得到各份 PPT 的总页数、各部分页数、每页平均字数、含图页比例；不加 `--stats` 可看逐页提纲。
2. `python3 scripts/render_check.py 往届.pptx 输出目录` 渲染总览图，看封面、目录、PART 页、内容页的版式。用户点名推荐的往届 PPT 要重点学：逐页看它的页数、每页一张主图加少量文字的做法、备注字数，作为本次详略的基准。
3. 需要换学校时：`python3 scripts/make_template.py 往届.pptx assets/学校_proposal_template.pptx --school 学校名`，得到只含五张骨架页（封面、目录、PART、内容页页眉、结束页）的干净模板；版式结构与西南科技大学模板不同时，按 `references/01-school-template.md` 第四节调整。

### 阶段 3　提取开题报告

`python3 scripts/extract_docx.py 开题报告.docx 工作目录`，得到按文档顺序排列的文字、表格和图片。逐章读完，记下每张图对应的图号和图题、每个公式的编号。

### 阶段 4　逐页规划

按 `references/02-deck-structure.md` 的六部分结构和页数预算列出逐页清单：每页的小标题、要点、用哪张图、用哪种版式（`references/03-layout-patterns.md`）、备注讲多少字。研究背景页先确定要补哪几张网络实拍图。规划时同步把开题报告的长句压成短句（规则见 `references/04-text-rules.md`）。规划清单先给用户过目；用户说直接做时，可以跳过确认。

### 阶段 5　生成

复制 `assets/example_build.py` 为工作目录下的 `build_deck.py`，把内容换成规划好的页面后运行：

```bash
python3 build_deck.py <本Skill目录> 输出.pptx
```

`scripts/swust_kit.py` 提供 封面、目录、PART 页、内容页（自动页码）、留白页、结束页，以及 文字、卡片、标题条、关键词链、分类条、箭头、编号圆、图片（等比放入并加图注条，缺图时放占位框）、表格、可编辑公式、备注讲稿与时长估算 等函数，坐标单位为厘米。

### 阶段 6　检查与修改

1. `python3 scripts/render_check.py 输出.pptx 检查目录`，逐张看总览图，必要时提高 `--dpi` 看单页；
2. 对照 `references/06-qa-checklist.md` 逐项检查（内容出处、数字一致、版式、字号、篇幅、备注时长、图片来源）；
3. 修改后重新生成、重新渲染，直到没有问题。

### 阶段 7　交付

交付 pptx 和生成脚本（脚本、开题报告图片和网络图片放在用户本地开题目录下，方便以后改一句话就重新生成）。说明：页数和各部分分布、讲稿总字数和预计时长、封面与留白页待填项、网络图片来源、学校名称的替换方法。新版本另存为新文件（V2、V3……），不覆盖旧版。给出本轮修改记录表。用户提出的修改意见，属于通用规律的，写回本 Skill 的 references 并升版本，推送到仓库。

## 文件索引

| 文件 | 用途 |
| --- | --- |
| `references/01-school-template.md` | 西南科技大学模板解剖：五类骨架页、页眉元素、配色、字体、坐标；换学校的方法 |
| `references/02-deck-structure.md` | 六部分结构、往届篇幅统计、按答辩时长的页数预算、开题报告各节到幻灯片的映射 |
| `references/03-layout-patterns.md` | 常用版式及其 `swust_kit` 写法：图文并排、四卡片、层次阶梯、表格加不足、公式加流程图等 |
| `references/04-text-rules.md` | 浓缩规则、强调用法、字号下限、每页字数、引用写法 |
| `references/05-ppt-master-notes.md` | 从 ppt-master 学到并采用的做法，以及没有采用的部分和原因 |
| `references/06-qa-checklist.md` | 交付前检查清单 |
| `references/07-notes-and-images.md` | 备注讲稿写法与时长控制；研究背景网络实拍图的选取、授权、下载与标注；个人成果留白页 |
| `scripts/swust_kit.py` | 生成库 |
| `scripts/make_template.py` | 从往届 PPT 抽取干净模板 |
| `scripts/extract_docx.py` | 提取开题报告文字、表格、图片 |
| `scripts/outline_dump.py` | 往届 PPT 提纲与统计 |
| `scripts/render_check.py` | 渲染逐页 PNG 与总览图 |
| `scripts/omml/` | LaTeX 转 Office Math 编译器（来自 ppt-master，MIT） |
| `assets/swust_proposal_template.pptx` | 西南科技大学开题答辩模板（五张骨架页） |
| `assets/example_build.py` | 示例生成脚本（占位内容，演示全部版式） |

## 运行环境

Python 3.9+，`python-pptx`、`python-docx`、`lxml`、`Pillow`；公式回退图需要 `pdflatex` 与 `pdftoppm`；渲染检查需要 LibreOffice。LibreOffice 不显示 Office Math，渲染图里看到的公式是 LaTeX 回退图，PowerPoint 中打开是可编辑公式。
