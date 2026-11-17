# 更新日志｜master-proposal-ppt

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循语义化版本。

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
