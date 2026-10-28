# master-proposal | Master's Thesis Proposal Skill (Chinese)

[简体中文](README.md) | **English** · [Back to proposal](../README.md) · [Repository home](../../README.md)

A skill for writing Chinese engineering master's thesis proposals (开题报告) that are grounded in a funded research project. The agent works as a doctoral supervisor and senior engineer in the student's field. Output is in Chinese.

## Workflow

| Stage | What happens | Hard rule |
| --- | --- | --- |
| 1 Intake | Four rounds of questions; material checklist; privacy reminder | No analysis until the user confirms all materials are provided |
| 2 Socratic clarification | Six levels of probing → "topic card" | Must explicitly ask whether objectives use quantitative indicators |
| 3 Literature | Search per research content; verify every entry | **56–66 references**, GB/T 7714 numeric style, all verifiable |
| 4 Outline | Align title, contents, objectives, key problems, plan, innovations | User approves before drafting |
| 5 Drafting | Project necessity → layered state of the art → trends → contents/objectives/key problems → plan → innovations → schedule | Each research content item: one core sentence, 4–5 lines, *what* not *how* |
| 6 Figures & equations | Visio diagrams, MathType equations, watermark-free images | Ask the user to open Visio and MathType first |
| 7 Self-review | Script checks + checklist + de-templating + anticipatory writing | Section lengths benchmarked against templates |
| 8 Defense brief | Plain-language 3–5 minute script with apt metaphors + 10 likely questions | No unexplained jargon |
| 9 Delivery | .docx, reference verification table, figure sources, defense brief, review report | **Section 5 (research foundation) is written by the student** |
| 10 Revision | Handle reviewer comments item by item, check the whole text for the same issue, save a new version | **Keep one cumulative revision log (修改记录表)** |

## Install

Copy only the `master-proposal` folder.

- **Claude Code**: `cp -r proposal/master-proposal ~/.claude/skills/`
- **Claude Cowork / claude.ai**: zip the folder (so the zip contains `master-proposal/SKILL.md`) and upload it under Settings → Capabilities → Skills.
- **Codex**: copy to `%USERPROFILE%\.agents\skills\master-proposal\` and invoke with `$master-proposal`.

## Scripts

- `scripts/check_proposal.py` — read-only checks: section lengths, reference count/format/duplicates/citation order, figure/table/equation numbering, research-content length, voice consistency, tense, stock phrases, typos, schedule order.
- `scripts/build_docx.py` — Markdown → formatted .docx (pandoc + python-docx), superscript citations, OMML equations with right-aligned numbers.
- `scripts/visio_macro.py` — figure spec (JSON) → Visio VBA macro producing an editable drawing, plus an SVG preview.

## Credits

Methods adapted (not copied) from hlf885/thesis-writing, Imbad0202/academic-research-skills(-codex), op7418/Humanizer-zh and obra/superpowers. Length benchmarks come from nine anonymised proposals; no source text is included.
