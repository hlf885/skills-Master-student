# 更新日志｜master-proposal

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循语义化版本。

## [1.1.0] - 2026-10-28

依据一次真实开题初稿的审阅意见迭代。

### 新增
- `SKILL.md`：硬性规则 9（学术研究而非项目，背景内容弱化并写明边界，可行性分析不引用文献、不写项目管理内容）、规则 10（图片原图逐张插入，禁止截屏拼接）、规则 11（每轮修改另存新版本并累积更新《修改记录表》）；新增阶段 10“按意见修改与修改记录表”。
- `assets/figure-spec-research-content.json`：分层研究内容框图示例（发现问题→研究目标→研究内容→关键问题，黄蓝虚线分层，重点词标红）。
- `scripts/visio_macro.py`：节点边框色 `stroke`、重点词标红 `red`、纯文字标签 `no_border`、单节点字号 `font_pt`、分组框颜色、连线颜色；`--png` 直接渲染预览图；SVG 预览支持多行文字、颜色与标红。
- `scripts/check_proposal.py`：检查 3.3 可行性分析中的文献引用与项目管理式用语；提示立题依据中被过度展开的背景概念。

### 修改
- `references/02-section-guide.md`：2.1 研究内容框图改为分层结构；3.3 可行性分析改为学生视角的“理论基础—技术储备—研究条件”写法，并列出禁止事项。
- `references/05-research-plan-figures-formulas.md`：统一配色方案；插图方式改为原图逐张插入；补充图规格新字段说明。
- `references/07-style-deai-defensive.md`：新增“学术研究的口吻，而不是项目口吻”与背景边界要求。
- `references/10-common-mistakes.md`：新增第 30–33 条。

### 修复
- `scripts/check_proposal.py`：公式中的区间（如 `[0,1]`）不再被误判为文献引用；模板栏目名“本研究课题可能的创新之处”不再计入称谓混用。

## [1.0.0] - 2026-10-26

### 新增
- `SKILL.md`：九阶段工作流与八条硬性规则（资料确认门槛、量化指标必问、第五部分用户自写、56–66 条可核实文献、先评估后方案、研究内容与方案分离、字数对标、研究诚信）。
- `references/` 10 份规范：分轮提问、各部分写法与字数、文献检索与层层递进综述、GB/T 7714 著录、方案评估与 Visio/MathType/图片流程、答辩通俗稿与比喻库、文风与去 AI 味与预判式写作、苏格拉底式追问与自审清单、9 份样本量化基准、常见问题。
- `assets/`：资料清单、全文 Markdown 骨架、答辩通俗稿模板、Visio 图规格示例。
- `scripts/`：`check_proposal.py`（自检）、`build_docx.py`（Markdown→docx）、`visio_macro.py`（图规格→Visio VBA 宏 + SVG 预览）。
- `tests/sample.md`：脚本冒烟测试样例。
