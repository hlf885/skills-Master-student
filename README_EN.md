# skills-Master-student | Skills for the Master's Degree Thesis Lifecycle

[简体中文](README.md) | **English**

A collection of agent skills for Chinese engineering master's students, organised by the three milestones of the degree: **proposal → mid-term review → thesis**. Each skill acts as a doctoral supervisor and senior engineer in the student's field: it asks before it writes, and it never fabricates references, data or results.

Works with Claude Code, Claude Cowork, claude.ai custom skills and other agents that read `SKILL.md` (e.g. Codex).

| Project | Skill | Status | Scope |
| --- | --- | --- | --- |
| [proposal](proposal/README.md) | [`master-proposal`](proposal/master-proposal/README_EN.md) | ✅ v1.0.0 | Thesis proposal (开题报告) |
| [mid-term](mid-term/README.md) | `master-midterm` | 🗓 planned | Mid-term review report (中期检查) |
| [thesis](thesis/README.md) | `master-thesis` | 🗓 planned | Degree thesis (学位论文) |

## Install

Copy only the skill folder you need, e.g. `cp -r proposal/master-proposal ~/.claude/skills/`. For Cowork/claude.ai, zip the folder and upload it under Settings → Capabilities → Skills.

## Conventions

- One skill per folder at `<project>/<skill-name>/`; folder name equals `name:` in `SKILL.md`.
- Each skill ships `README.md`, `README_EN.md`, `CHANGELOG.md`; shared writing rules are duplicated inside each skill so that a single folder is self-contained.
- Run `python scripts/validate_skills.py` before committing; CI runs it on every push.
- Never commit unpublished proposals/theses, contracts, personal data or secrets. No licence has been chosen yet.

See [docs/REPOSITORY_GUIDE_EN.md](docs/REPOSITORY_GUIDE_EN.md).
