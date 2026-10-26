# Repository Guide

[简体中文](REPOSITORY_GUIDE_ZH.md) · [Home](../README_EN.md)

This is a **collection repository** with three projects matching the master's degree milestones: `proposal/`, `mid-term/`, `thesis/`. Each project holds one or more skills.

## Layout and naming

- A skill lives at `<project>/<skill-name>/` (kebab-case, prefix `master-`), and the folder name must equal `name:` in its `SKILL.md`.
- Required files: `SKILL.md` (YAML front matter with `name`, `description`, `metadata.version`), `README.md`, `README_EN.md`, `CHANGELOG.md`. Optional: `references/`, `assets/`, `scripts/`, `tests/`.
- Keep `SKILL.md` short (workflow, hard rules, index); put details in `references/`. Never reference files in another skill folder.

## Shared rules

Rules shared by the three skills (GB/T 7714, de-templating, Socratic questioning, Visio/MathType workflow, defense brief) are duplicated per skill. `proposal/master-proposal/references/` is the baseline; copies state their source file and version; changes are logged in the root `CHANGELOG.md`.

## Versioning and releases

Each skill has its own semantic version (`metadata.version` = its CHANGELOG). Tag releases as `<skill-name>-v<version>`. Patch = wording/examples; minor = new checks/references/steps; major = changed hard rules or deliverables.

## Branches and commits

`main` is always installable. Use `feat/<skill>-<topic>` and `fix/<skill>-<topic>` branches; commit messages as `<skill or scope>: <summary>`.

## Quality gate

Run `python scripts/validate_skills.py` before committing (CI runs it on every push/PR). It checks front matter, required files, relative Markdown links, script compilation and smoke tests.

## Privacy and integrity

Do not commit unpublished proposals/theses, contracts, personal data, raw experimental data or secrets. Learning samples are kept only as statistics. Skills must not ghost-write sections the student is required to write, and must never fabricate references, data or results.
