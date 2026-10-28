# master-proposal｜硕士学位论文开题报告 Skill

**简体中文** | [English](README_EN.md) · [返回 proposal 项目](../README.md) · [仓库首页](../../README.md)

以“本领域博士生导师 + 高级工程师”的身份，陪你把一份**依托科研项目的工科硕士开题报告**从资料收集写到答辩通俗稿。适用于 Claude（Claude Code、Claude Cowork、claude.ai 自定义 Skill）以及兼容 `SKILL.md` 的智能体（如 Codex）。

## 它会怎么做

| 阶段 | 做什么 | 硬性规则 |
| --- | --- | --- |
| 1 资料收集 | 分四轮提问；给出资料清单；提醒脱敏 | 用户确认“资料已全部提供”后才开始分析 |
| 2 苏格拉底式澄清 | 六层追问，产出《课题定位卡》 | **必须明确询问是否使用量化指标** |
| 3 文献 | 按研究内容检索、逐条核实 | **56–66 条**，GB/T 7714 顺序编码，真实可查 |
| 4 提纲 | 题目—内容—目标—关键问题—方案—创新点对齐 | 用户确认后再写 |
| 5 正文 | 立项必要性 → 层层递进的现状 → 趋势 → 研究内容/目标/关键问题 → 方案 → 创新点 → 计划 | 研究内容每项一句核心话、4–5 行、只说做什么 |
| 6 图与公式 | Visio 作图、MathType 公式、无水印图片 | 作图写公式前请用户先打开 Visio 与 MathType |
| 7 自审 | 脚本检查 + 清单自审 + 去 AI 味 + 预判式写作 | 字数对标模板 |
| 8 答辩通俗稿 | 3–5 分钟讲清楚，贴切比喻 + 预判 10 问 | 不含难懂术语 |
| 9 交付 | docx 正文、文献核实表、图源文件、答辩稿、自审报告 | **第五部分由用户本人撰写** |
| 10 按意见修改 | 逐条处理审阅意见，全文排查同类问题，另存新版本 | **每轮更新同一张《修改记录表》** |

## 目录

```text
master-proposal/
├── SKILL.md                     # 主流程与硬性规则（智能体入口）
├── references/                  # 分阶段读取的详细规范
│   ├── 01-intake-questionnaire.md      分轮提问与资料清单
│   ├── 02-section-guide.md             各部分写法、字数、句式
│   ├── 03-literature-review.md         检索、核实、层层递进的综述
│   ├── 04-citation-gbt7714.md          GB/T 7714 著录与常见错误
│   ├── 05-research-plan-figures-formulas.md  评估表、Visio、MathType、无水印图片
│   ├── 06-defense-plain-language.md    答辩通俗稿与比喻库
│   ├── 07-style-deai-defensive.md      文风、去 AI 味、预判式写作
│   ├── 08-socratic-review.md           苏格拉底式追问与自审清单
│   ├── 09-template-benchmarks.md       9 份样本的量化基准
│   └── 10-common-mistakes.md           样本中出现过的常见问题
├── assets/                      # 资料清单、全文骨架、答辩稿模板、图规格示例
├── scripts/                     # check_proposal.py / build_docx.py / visio_macro.py
├── tests/sample.md              # 脚本冒烟测试样例
└── CHANGELOG.md
```

## 安装

只复制 `master-proposal` 这个文件夹，不要把整个仓库当成一个 Skill。

**Claude Code（个人级）**
```bash
git clone https://github.com/hlf885/skills-Master-student.git
mkdir -p ~/.claude/skills
cp -r skills-Master-student/proposal/master-proposal ~/.claude/skills/
```
Windows PowerShell：
```powershell
git clone https://github.com/hlf885/skills-Master-student.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\skills-Master-student\proposal\master-proposal" "$HOME\.claude\skills\master-proposal"
```

**Claude Cowork / claude.ai**：把 `master-proposal` 文件夹压缩为 zip（zip 根目录下即为 `master-proposal/SKILL.md`），在 设置 → 功能（Capabilities）→ Skills 中上传。

**Codex**：复制到 `%USERPROFILE%\.agents\skills\master-proposal\`，重启后用 `$master-proposal` 调用。

## 使用示例

```text
请用 master-proposal 帮我写开题报告。我的课题依托一个企业横向项目，研究对象是管廊巡检机器人。
```
```text
这是我写好的开题报告初稿（附件），请按 master-proposal 的自审清单检查，并给出修改建议，不要整体重写。
```
```text
开题报告已经定稿，请按 master-proposal 第 8 阶段生成答辩通俗讲解稿。
```

## 脚本

```bash
python scripts/check_proposal.py 我的开题报告.md          # 自检（字数、文献、编号、套话……）
python scripts/build_docx.py 我的开题报告.md -o 开题报告.docx   # 生成 Word（需 pandoc、python-docx）
python scripts/visio_macro.py 图规格.json -o fig.bas --svg 预览.svg  # 生成 Visio 宏
```

## 致谢与参考

写作规范参考并改写自：[hlf885/thesis-writing](https://github.com/hlf885/thesis-writing)（作者声音、反防御性写作、无水印图像）、[Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) 与 [academic-research-skills-codex](https://github.com/Imbad0202/academic-research-skills-codex)（苏格拉底式导师、写作质量检查、论断强度阶梯）、[op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh)（中文模板化表达检查）、[obra/superpowers](https://github.com/obra/superpowers) 的 brainstorming（先问清再动手）。各项目的许可证以其仓库为准；本 Skill 只吸收方法，未复制其文本。

结构与篇幅基准来自 9 份同领域硕士开题报告，仓库中只保留统计结果，不包含任何原文。

## 诚信声明

本 Skill 不代写研究基础，不编造文献、数据和成果，不保证通过任何 AI 检测。开题报告的学术责任由作者本人承担。
