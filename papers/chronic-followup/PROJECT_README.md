# Chronic Follow-up Thesis Project

## Layout

- `content/`: JSON source for metadata, paragraph edits, figures, and tables.
- `images/imagegen/`: ImageGen-created thesis diagrams in the requested `study-buddy/images` black-and-white style.
- `images/reference_style/`: copied reference diagrams from `thesis_project/papers/study-buddy/images`.
- `build.py`: rebuilds the final DOCX from the Word template, JSON content, and diagram assets.
- `render_check/`: current render QA output.

## Build

Run from this folder:

```bash
/Users/a136/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 build.py
```

The final DOCX is:

```text
社区卫生服务中心慢性病随访系统设计与实现_论文修改稿.docx
```

## Figure Rules

- Runtime screenshots remain from the source Word/system material.
- Conceptual thesis diagrams are generated with ImageGen, not Python, canvas, frontend code, or matplotlib.
- The E-R diagram uses table-style PK/FK notation and underlines the primary-key `id` fields.
