# 更新日志（仓库级）

记录跨 Skill 的变化；单个 Skill 的细节见其目录下的 `CHANGELOG.md`。

## 2026-11-16（二）

### 修改
- `proposal/master-proposal` 升级到 v1.8.0：补齐技术路线图（5 种）、架构与框架图（6 种）、算法流程图（6 种）的画法图库与推荐规则，画法来源含美国和欧洲高校博士论文与国际通行标准。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-16

### 修改
- `proposal/master-proposal` 升级到 v1.7.0：新增自绘图流程（先问需求、展示图库、给出推荐、由用户选择画法和交付格式），研究内容图九种画法的图库，绘图引擎 `figkit.py` 与 `draw_figure.py`（PNG、SVG、Visio 宏），答辩问答模板，口语化检查。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-15（三）

### 修改
- `proposal/master-proposal` 升级到 v1.6.1：新增题目动作词（如优化）的落实办法、《可能会被问的问题》的写法（懂行与不懂行两类专家）、图片段落单倍行距与口语化说法排查。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-15（二）

### 修改
- `proposal/master-proposal` 升级到 v1.6.0：新增论证主线规范（`references/11-argument-chain.md`）与主线自检脚本 `check_logic_chain.py`，把作者立题依据“围绕题目、层层递进”的写法拆成可复用的步骤；把聊天中直接提出的修改意见整理为规范（硬性规则 17，常见问题 74–86），新增引号、破折号、箭头检查。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-15

### 修改
- `proposal/master-proposal` 升级到 v1.5.0：依据第七轮审阅意见，只引用已正式发表的文献，2020 年以前的概念类文献改引近年高水平论文或博士论文并改写引用句（算法与工具原文保留），记录已核实的著录格式与核实流程；指称课题统一用“本课题”，表述书面化；新增留白排查规则；工作计划参照师兄师姐的时间安排；第五部分依据用户已完成的工作撰写；图2-1 默认改为场景图＋四步闭环；`check_proposal.py` 新增预印本、2020 年以前文献、“本文/文中/本研究”和单位空格检查。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-13

### 修改
- `proposal/master-proposal` 升级到 v1.4.0：依据第六轮审阅意见，研究边界只用文字不配图，规范“依托××项目”的写法，少用分号，删去“由此提出”“据此，本课题拟”类衔接套话，公式运算符也用 Times New Roman；`check_proposal.py` 新增分号和衔接套话检查，并识别 `[PP/OL]`。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-10

### 修改
- `proposal/master-proposal` 升级到 v1.3.0：依据第五轮审阅意见，新增《参考文献导读》和格式用语两条硬性规则；要求近三年文献过半并按 GB/T 7714—2025 著录；研究边界在 1.1 写清，2.1 开头写研究背景，1.2 按类别凝练优缺点，1.3 与研究内容一一对应；文献图片不出现外文；新增五层四列研究内容框图规格；`check_proposal.py` 新增人称代词、近三年占比和预印本标识检查。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-06

### 修改
- `proposal/master-proposal` 升级到 v1.2.0：依据第三轮审阅意见，新增“像样本那样自然叙述”硬性规则，规范 2.1 导语、3.1 路线说明、3.2 开头和实验验证的写法，技术路线图成果栏不写论文；插图基准改为 13–25 幅并要求 1.2 配文献原图，补充网络受限时取原图的办法；`check_proposal.py` 新增元叙述、自我设限句、“本课题”“项目”频次、插图数量和技术路线图检查。详见该 Skill 的 `CHANGELOG.md`。

## 2026-11-02

### 修复
- `proposal/master-proposal` 升级到 v1.1.1：图题表题全角空格显示为方框、公式加粗与字体不符、左上标显示虚线方框、编号公式未按独立公式排版等问题；2.1 研究内容写作顺序规范。详见该 Skill 的 `CHANGELOG.md`。

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
