# 仓库管理规范

[English](REPOSITORY_GUIDE_EN.md) · [首页](../README.md)

本仓库是**集合仓库**，按硕士培养环节分为三个项目：`proposal/`（开题）、`mid-term/`（中期）、`thesis/`（学位论文）。每个项目下可以有一个或多个 Skill。

## 1. 目录与命名

```text
<项目>/
├── README.md                 # 项目说明：包含哪些 Skill、适用阶段、规划
└── <skill-name>/             # Skill 本体，kebab-case
    ├── SKILL.md              # 必需；YAML 头含 name、description、metadata.version
    ├── README.md / README_EN.md
    ├── CHANGELOG.md
    ├── references/           # 分阶段读取的详细规范（编号前缀 01-、02-……）
    ├── assets/               # 模板、清单、示例数据
    ├── scripts/              # 可选的只读检查或生成工具（Python 3.9+）
    └── tests/                # 脚本冒烟测试样例
```

- 文件夹名必须与 `SKILL.md` 的 `name:` 一致；建议前缀统一为 `master-`（`master-proposal`、`master-midterm`、`master-thesis`）；
- `SKILL.md` 只放流程、硬性规则和索引（建议 300 行以内），细节放 `references/`；
- `description` 同时写中英文触发词，便于智能体匹配；
- 不跨 Skill 引用文件（`../other-skill/...`），保证单个文件夹复制即可使用。

## 2. 共享规范的同步

三个 Skill 会共用一些规范（GB/T 7714 著录、去 AI 味、苏格拉底式追问、Visio/MathType 流程、答辩通俗稿）。规则：

1. 以 `proposal/master-proposal/references/` 中的版本为基准；
2. 其他 Skill 复制后可按环节改写，但在文件开头注明“同步自 master-proposal 的 xx 文件，版本 x.y.z”；
3. 修改共享规范时，在仓库 `CHANGELOG.md` 记一笔，并检查其余 Skill 是否需要同步。

## 3. 版本与发布

- 每个 Skill 独立使用语义化版本（`SKILL.md` 的 `metadata.version` 与该 Skill 的 `CHANGELOG.md` 保持一致）：
  - 修订号：错别字、示例、措辞；
  - 次版本号：新增检查项、新增参考文件、流程中增加步骤；
  - 主版本号：硬性规则或交付物发生变化；
- 发布时打标签：`<skill-name>-v<版本>`，例如 `master-proposal-v1.0.0`；
- 仓库级 `CHANGELOG.md` 记录跨 Skill 的变化。

## 4. 分支与提交

- `main` 为可直接安装的稳定版本；
- 新功能在 `feat/<skill>-<主题>` 分支开发，修复用 `fix/<skill>-<主题>`，合并前通过 CI；
- 提交信息格式：`<skill或scope>: <动词开头的简述>`，例如 `master-proposal: 增加工作计划时间重叠检查`。

## 5. 质量检查

提交前在仓库根目录运行：

```bash
python scripts/validate_skills.py
```

它会检查：每个 Skill 的 `SKILL.md` 头信息（name 与文件夹一致、description 存在且不超长、version 存在）、README/CHANGELOG 是否齐全、Markdown 相对链接是否有效、脚本能否通过语法编译，并对 `tests/` 样例运行冒烟测试。GitHub Actions 会在每次 push 和 PR 时自动运行。

## 6. 隐私与诚信

- 严禁上传：未公开的开题报告/论文原文、项目合同与任务书、个人身份信息（姓名、学号、导师）、实验原始数据、账号密钥；
- 学习样本只保留统计结果和抽象出的写作规律，不保留原文段落；
- Skill 不得被设计为代写必须由学生本人完成的部分，不得编造文献、数据或成果；
- 引用他人仓库的方法时，在 README 致谢中注明来源，遵守其许可证，不复制受限文本。

## 7. 新增 Skill 的检查清单

- [ ] 放在正确的项目目录，文件夹名 = `name:`；
- [ ] `SKILL.md`、`README.md`、`README_EN.md`、`CHANGELOG.md` 齐全；
- [ ] 项目 `README.md` 与仓库根 `README.md`/`README_EN.md` 的索引已更新；
- [ ] `python scripts/validate_skills.py` 通过；
- [ ] 至少用一个真实（已脱敏）案例走通完整流程。
