# 更新日志｜master-proposal-ppt

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循语义化版本。

## [1.2.0] - 2026-11-18

依据第二轮用户修改意见（存在的问题-V2）修订：第二版配色差、创新点页 AI 味重、字太小；公式要在备注里详细解释以防被问；改之前先确认需求、学习别人好的做法。另据用户要求：使用本 Skill 时要提供多种高质量、无 AI 味的风格案例供用户选择；选定风格后全篇统一，但不能页页一个样。修订前对照学习了 ppt-master、anthropics/skills 的 pptx 技能、academic-pptx-skill、MiniMax pptx-generator 和讨论 AI 幻灯片通病的文章。

### 新增
- 硬性规则 8：先确认需求，风格样页先行，由用户选风格。
- 硬性规则 9：去 AI 味；全篇统一规则但版式按内容变化，相邻两页不用同一种版式，全篇至少 5 种；每个内容页顶部一句结论句；正文不低于 16 磅。
- `references/08-aesthetics-and-style.md`：宗旨与需求确认、AI 味清单与改法、全篇统一规则、版式多样要求、风格样页流程、公式页备注写法。
- `scripts/style_gallery.py`：同一组内容按五套风格（学术极简、期刊黑白、浅色分区、深色重点、大字结论）各出 4 张不同版式的样页，可 `--content` 换成用户自己的内容，`--render` 输出拼图。
- `assets/style_gallery/`：五套风格样页拼图（虚构示例内容）。
- `swust_kit.py`：`THEMES` 与 `set_theme()`、`headline()`、`fig()`（灰色小字图注）、`rule_table()`（学术三线表）、`line()`、`big_number()`；`notes(text, ref=)` 备查部分不计入时长。
- 阶段 0（确认宗旨与需求）和阶段 4.5（风格样页）。

### 修改
- `references/03-layout-patterns.md` 重写为按内容选版式的 L1 到 L9；v1.1 的 P1 到 P24 退役。
- `references/04-text-rules.md`：停用红色加粗，强调改为结论句和主色加粗；字号表上调（正文 17 到 20 磅）。
- `references/06-qa-checklist.md`：增加审美与去 AI 味、版式多样、公式备查检查项。
- `references/07-notes-and-images.md`：增加备查部分写法。
- `references/01`、`02`、`05`：去掉沿用往届色条、虚线框、红色强调的建议。
- `assets/example_build.py` 重写为学术极简示例，演示 L1 到 L9，`--theme` 切换风格。
- `swust_kit.py`：`bar()`、`card()`、`circle_num()`、`chain()`、`class_row()` 标为旧版式，不再推荐。

## [1.1.0] - 2026-11-17

依据第一轮用户修改意见（存在的问题-V1）修订：汇报限时 8 到 10 分钟，初稿 34 页过长过密；要求图文并茂、研究背景补充真实网络图片、每页写备注讲稿、研究基础留一页空白放个人成果，并以用户推荐的往届 PPT 为详略基准。

### 新增
- 硬性规则 6：每页必须有备注讲稿，按每分钟约 250 字（不计标点）控制总时长，默认 8 到 10 分钟。
- 硬性规则 7：研究基础固定留一页空白页，供用户自行粘贴比赛、论文、专利等个人成果。
- 硬性规则 1 增加例外：研究背景页可补充与课题直接相关、授权允许使用的真实网络照片，须注明作者与许可，不得自绘或生成。
- `references/07-notes-and-images.md`：备注讲稿写法与逐页时长分配；Wikimedia Commons 检索、下载、落盘与标注流程；留白页做法。
- `swust_kit.py`：`notes()`、`notes_report()`、`blank_page()`、`picture_or_placeholder()`、`chain()`、`class_row()`；`bar()` 支持换行符。
- `references/03-layout-patterns.md`：P20 背景图墙、P21 现状分类条、P22 目标与关键问题双栏、P23 两项研究一页、P24 关键数字色块。

### 修改
- `references/02-deck-structure.md`：按汇报时长重定页数，8 到 10 分钟版 15 到 18 页、不用 PART 过渡页，给出 17 页推荐页序；补充推荐样例的统计特点。
- `references/04-text-rules.md`：有备注后页面文字降到每页 40 到 120 字，一条要点不超过 25 字。
- `references/06-qa-checklist.md`：增加讲稿与时长、图片来源、留白页、另存新版本和修改记录表等检查项。
- `assets/example_build.py`：改为 8 到 10 分钟版结构，演示备注、留白页和新版式。
- `SKILL.md`：流程中加入汇报时长、重点学习用户推荐的往届 PPT、交付时说明讲稿时长与图片来源。

## [1.0.0] - 2026-11-17

首个版本。学习 hugohe3/ppt-master 的工作流和 9 份往届开题答辩 PPT 后整理而成，并用一份真实开题报告走通了完整流程（34 页）。

### 新增
- `SKILL.md`：七阶段流程（收集材料、学习模板与篇幅、提取开题报告、逐页规划、生成、检查、交付）与六条硬性规则。
- `scripts/swust_kit.py`：在原生模板上生成封面、目录、PART 页、内容页（自动页码）、结束页，提供文字、卡片、标题条、箭头、编号圆、图片、表格、可编辑公式等函数，并给出文字溢出警告。
- `scripts/make_template.py`：从往届 PPT 抽取只含五张骨架页的干净模板，支持替换学校名。
- `scripts/extract_docx.py`、`scripts/outline_dump.py`、`scripts/render_check.py`。
- `scripts/omml/`：ppt-master 的 LaTeX 转 Office Math 编译器（MIT）。
- `assets/swust_proposal_template.pptx`：西南科技大学开题答辩模板；`assets/example_build.py`：占位内容示例。
- `references/01` 至 `06`：模板解剖、结构与篇幅统计、版式、文字规则、ppt-master 笔记、检查清单。
