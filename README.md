# skills-Master-student｜硕士研究生学位论文全流程 Skill 集合

**简体中文** | [English](README_EN.md)

面向工科硕士研究生的学位论文写作 Skill 集合，按培养环节分为三个项目：**开题（proposal）→ 中期（mid-term）→ 学位论文（thesis）**。每个 Skill 以“本领域博士生导师 + 高级工程师”的身份工作：先问清楚、再动笔；不编造文献、数据和成果。

> 适用于 Claude Code、Claude Cowork、claude.ai 自定义 Skill，以及兼容 `SKILL.md` 规范的其他智能体（如 Codex）。

## 项目一览

| 项目 | Skill | 状态 | 说明 |
| --- | --- | --- | --- |
| [proposal](proposal/README.md) | [`master-proposal`](proposal/master-proposal/README.md) | ✅ v1.0.0 | 开题报告：资料收集与追问、立项必要性、层层递进的研究现状、研究内容/目标/关键问题、评估后的研究方案（Visio + MathType）、56–66 条 GB/T 7714 文献、去 AI 味、答辩通俗讲解稿 |
| [mid-term](mid-term/README.md) | `master-midterm` | 🗓 规划中 | 中期检查报告：进展对照开题计划、阶段成果、存在问题与调整、后续计划 |
| [thesis](thesis/README.md) | `master-thesis` | 🗓 规划中 | 学位论文：章节架构、各章写作、图表公式、参考文献、查重与送审前自查、答辩 |

## 快速安装（以 master-proposal 为例）

只复制需要的 Skill 文件夹，**不要把整个仓库当成一个 Skill 安装**。

```bash
git clone https://github.com/hlf885/skills-Master-student.git
mkdir -p ~/.claude/skills
cp -r skills-Master-student/proposal/master-proposal ~/.claude/skills/
```

- Claude Cowork / claude.ai：将 `proposal/master-proposal` 文件夹压缩为 zip，在 设置 → 功能 → Skills 中上传；
- Codex：复制到 `%USERPROFILE%\.agents\skills\master-proposal\`，用 `$master-proposal` 调用。

详见各 Skill 的 README。

## 仓库结构

```text
skills-Master-student/
├── README.md / README_EN.md       # 集合索引（本文件）
├── CHANGELOG.md                   # 仓库级更新日志
├── docs/                          # 仓库管理规范（命名、版本、发布、隐私）
├── scripts/validate_skills.py     # 结构与 SKILL.md 头信息校验（CI 使用）
├── .github/workflows/validate.yml # 提交时自动校验
├── proposal/                      # 项目一：开题报告
│   ├── README.md
│   └── master-proposal/           # Skill 本体（SKILL.md、references、assets、scripts、tests）
├── mid-term/                      # 项目二：中期检查（规划中）
│   └── README.md
└── thesis/                        # 项目三：学位论文（规划中）
    └── README.md
```

## 约定

- 每个 Skill 放在 `<项目>/<skill-name>/`，文件夹名与 `SKILL.md` 中的 `name:` 完全一致（kebab-case）；
- 每个 Skill 自带 `README.md`（中文）、`README_EN.md`（英文）、`CHANGELOG.md`；
- 三个项目共用的写作规范（GB/T 7714、去 AI 味、苏格拉底式追问等）**在各 Skill 内各保留一份**，保证单个文件夹复制即可使用；修改时同步更新（见 [仓库管理规范](docs/REPOSITORY_GUIDE_ZH.md)）；
- 提交前运行 `python scripts/validate_skills.py`。

## 研究诚信与隐私

- Skill 不代写“研究基础与工作条件”等必须由学生本人完成的内容，不编造文献、实验数据、成果与项目信息；
- 仓库中不得上传未公开的开题报告、论文原文、项目合同、个人信息和任何密钥；学习样本只保留统计结果；
- 尚未选定统一开源许可证。在添加许可证前，请勿假定内容可自由复制或再分发。

## 致谢

方法参考：[hlf885/thesis-writing](https://github.com/hlf885/thesis-writing)、[Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills)、[Imbad0202/academic-research-skills-codex](https://github.com/Imbad0202/academic-research-skills-codex)、[op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh)、[obra/superpowers](https://github.com/obra/superpowers)。
