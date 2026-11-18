# master-proposal-ppt | Proposal defense slides

[简体中文](README.md) | **English** · [Project](../README.md) · [Repository](../../README.md)

Builds an editable Chinese master's thesis proposal defense deck (开题答辩 PPT) from a finished proposal (docx), on top of the school's native PowerPoint template. The bundled demo template is Southwest University of Science and Technology; any school's template can be extracted from a past defense deck with `scripts/make_template.py`.

## Features

- Learn page structure and length from past decks (statistics only, no copying);
- Extract a clean five-skeleton template (cover, contents, part divider, content header, closing);
- Extract text, tables, figures and equations from the proposal docx;
- Plan and generate the six standard parts slide by slide;
- Native, editable Office Math equations (compiler vendored from ppt-master) with image fallback;
- Speaker notes on every slide with talk-time estimate (default 8 to 10 minutes), licensed real photos for the background slide, and a blank slide for personal achievements;
- Style gallery first: six deck-wide styles (including V3实例, a complete 17-slide layout recipe users liked) rendered with the user's own content, the user picks one; then one consistent rule set across the deck while each slide's layout follows its content (no "AI look": no colored text bars, number circles, dashed boxes or red bold);
- Equation slides carry a reference section in the notes (symbol definitions, design rationale, likely questions), excluded from talk time;
- Render every slide to PNG plus contact sheets, with text overflow warnings.

## Install

Plain SKILL.md format: works in Codex, Claude Code and claude.ai.

```bash
pip install python-pptx python-docx lxml pillow matplotlib
```

**Codex** (inside a session):

```text
$skill-installer install https://github.com/hlf885/skills-Master-student/tree/main/proposal-ppt/master-proposal-ppt
```

or copy `proposal-ppt/master-proposal-ppt` into `~/.agents/skills/`, restart Codex, then invoke with `$master-proposal-ppt`.

**Claude Code**: copy the folder into `~/.claude/skills/`. **claude.ai**: `python scripts/package_skill.py proposal-ppt/master-proposal-ppt` and upload the zip.

LaTeX (`pdflatex`) and `pdftoppm` are needed for equation fallbacks; LibreOffice for render checks.

## Usage (Codex)

```text
$master-proposal-ppt
Build my proposal defense deck from <proposal.docx>. Past decks: <folder or none>. Talk length: <8 to 10 minutes>.
Confirm the brief and the slide-by-slide plan first, show me the style gallery rendered with my own content (or use V3实例),
then generate, write speaker notes with a reference section for every equation, and render-check every slide.
```

## Credits

Workflow ideas and the LaTeX to Office Math compiler come from [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) (MIT, Copyright (c) 2025-2026 Hugo He). See `scripts/omml/LICENSE_ppt-master`.
