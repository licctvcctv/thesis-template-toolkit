# Outpatient Appointment Thesis Project

## Layout

- `content/`: thesis content JSON, including metadata, chapters, and references.
- `images/`: paper-ready figures and real system screenshots referenced by the JSON files.
- `scripts/generate_imagegen_diagrams.py`: regenerates the black-and-white thesis diagrams used for use cases, three sequence diagrams, database logic, and flowcharts.
- `build.py`: assembles the final DOCX from the school template, content JSON, images, and tables.
- `render_check/`: current render QA output generated from the latest DOCX.

## Build

Run from this folder to refresh the paper-ready diagrams and rebuild the DOCX:

```bash
python3 scripts/generate_imagegen_diagrams.py
python3 build.py
```

The final DOCX is:

```text
基于Spring Boot的门诊预约挂号系统设计与实现_修改版.docx
```

## Figure Rules

- Runtime screenshots keep the `run_*.png` names and come from the actual system pages.
- Non-runtime diagrams use black-and-white thesis/Visio style and are generated into `images/`.
- Do not hand-edit figure captions inside the DOCX. Update the JSON and rebuild instead.
- Stale render output and unused legacy diagrams live under `../../artifacts/outpatient-appointment/`.
