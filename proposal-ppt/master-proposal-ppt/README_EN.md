# master-proposal-ppt | Proposal defense slides

[简体中文](README.md) | **English** · [Project](../README.md) · [Repository](../../README.md)

Builds an editable Chinese master's thesis proposal defense deck (开题答辩 PPT) from a finished proposal (docx), on top of the school's native PowerPoint template. The bundled demo template is Southwest University of Science and Technology; any school's template can be extracted from a past defense deck with `scripts/make_template.py`.

## Features

- Learn page structure and length from past decks (statistics only, no copying);
- Extract a clean five-skeleton template (cover, contents, part divider, content header, closing);
- Extract text, tables, figures and equations from the proposal docx;
- Plan and generate the six standard parts slide by slide;
- Native, editable Office Math equations (compiler vendored from ppt-master) with image fallback;
- Render every slide to PNG plus contact sheets, with text overflow warnings.

## Install

```bash
cp -r skills-Master-student/proposal-ppt/master-proposal-ppt ~/.claude/skills/
pip install python-pptx python-docx lxml pillow
```

LaTeX (`pdflatex`) and `pdftoppm` are needed for equation fallbacks; LibreOffice for render checks.

## Credits

Workflow ideas and the LaTeX to Office Math compiler come from [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) (MIT, Copyright (c) 2025-2026 Hugo He). See `scripts/omml/LICENSE_ppt-master`.
