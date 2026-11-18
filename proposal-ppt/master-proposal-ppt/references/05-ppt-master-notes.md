# 05 从 ppt-master 学到的做法

[返回 SKILL.md](../SKILL.md)

来源：[hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)（v6.9.0，MIT 许可，作者 Hugo He）。ppt-master 是一个通用的演示文稿生成工作流：先把资料整理成设计规格，再逐页写 SVG，最后转成可编辑的原生 pptx。

## 一、采用的做法

| ppt-master 的做法 | 在本 Skill 中的落实 |
| --- | --- |
| 路由先行：生成新稿、建模板、在原生 pptx 上改内容是三条不同路线，一次只走一条 | 开题答辩有学校固定模板，走 在原生模板上填内容 这条路线：保留母版、版式和页眉，只往内容区放新元素 |
| 模板是可复用的工作区，从参考文件抽取，不在原文件上改 | `make_template.py` 从往届 PPT 抽取只含骨架页的新模板，不改往届文件 |
| 先计划后执行：资料齐全、逐页规划确认后再生成 | 阶段 1 到阶段 4，逐页清单先给用户看 |
| 每页先想清楚这页要让读者明白什么，再选承载形式（卡片、条带、编号、图） | `references/03-layout-patterns.md` 按页面任务列出版式 |
| 一套贯穿全篇的视觉母题，按页面角色变化 | v1.2.0 起改为：全篇统一颜色与字号规则（结论句、细线、三线表、灰色图注），版式按内容变化，见 08 |
| 公式用 LaTeX 编译成可编辑的 Office Math，并保留回退显示 | `scripts/omml/` 直接使用 ppt-master 的编译器；`swust_kit.formula()` 生成 Office Math，并把 LaTeX 渲染图作为不支持公式的软件的回退 |
| 生成后按检查关口逐项验收，在出问题的那一层修 | `render_check.py` 渲染检查；文字溢出警告；`06-qa-checklist.md`；问题出在内容就改规划，出在版式就改坐标 |
| 不在用户确认前替用户做决定 | 页数、学校模板、讲稿与否在阶段 1 问清 |

## 二、没有采用的部分

| 部分 | 原因 |
| --- | --- |
| SVG 逐页手写再转换 | 开题答辩以学校模板为准，直接在原生 pptx 上用 python-pptx 放元素更稳定，用户也更容易手工微调 |
| AI 生图、网络配图 | 开题答辩的图必须来自开题报告或用户自己的工作，不使用生成或网络图片 |
| 动画、旁白、视频导出 | 开题答辩为现场讲解，往届 PPT 都不用动画；需要时可参考 ppt-master 的 animations 规范另行添加 |
| 设计规格锁定文件（spec_lock）与浏览器确认界面 | 学校模板已经固定了配色和字体，规格由 `01-school-template.md` 记录即可 |

## 三、公式编译器的使用

```python
from omml.formula_compiler import compile_latex_to_omml
xml = compile_latex_to_omml(r"\frac{a}{b}")   # 返回 m:oMathPara
```

支持常用 LaTeX：分式、上下标、求和、`\underset`、`\left( \right)`、`\boldsymbol`、`\mathrm`、希腊字母、集合符号。不支持的写法会抛出 `FormulaCompileError`，改写为等价的简单写法即可。公式中不要写中文。
