# 更新日志（仓库级）

记录跨 Skill 的变化；单个 Skill 的细节见其目录下的 `CHANGELOG.md`。

## 2026-10-28

### 修改
- `proposal/master-proposal` 升级到 v1.1.0：依据一次开题初稿的审阅意见，新增“学术研究而非项目”“原图逐张插入”“修改记录表”三条硬性规则与阶段 10；研究内容框图改为分层结构并统一配色；可行性分析改为学生视角；`visio_macro.py`、`check_proposal.py` 相应增强。详见该 Skill 的 `CHANGELOG.md`。

## 2026-10-26（二）

### 新增
- `scripts/package_skill.py`：把 Skill 打包为可上传 claude.ai 的 zip；
- 仓库管理规范新增“迭代与发布流程”，约定提交作者为仓库所有者本人。

## 2026-10-26

### 新增
- 建立集合仓库结构：`proposal/`、`mid-term/`、`thesis/` 三个项目；
- 发布 `proposal/master-proposal` v1.0.0（开题报告 Skill）；
- `mid-term/`、`thesis/` 写入规划说明，Skill 待开发；
- 仓库管理规范（中英文）、`scripts/validate_skills.py` 校验脚本与 GitHub Actions 自动校验；
- `.gitignore` 默认排除 Word/PDF/Visio 文件，防止误传开题报告原文与项目资料。
