---
name: autocad-com-drawing
description: Create or modify AutoCAD DWG drawings through AutoCAD COM/ActiveX on Windows. Use when Codex needs to draw model-space geometry with AutoCAD COM, especially dimensioned 2D parts such as rectangles, plates, holes, centerlines, layers, text, and linear/diameter dimensions, or when the user asks in Chinese or English to use COM to draw in AutoCAD.
---

# AutoCAD COM Drawing

## Overview

Use AutoCAD COM through Python/pywin32 for deterministic DWG creation. Prefer model space, millimeters, and explicit layers unless the user specifies otherwise.

## Workflow

1. Extract the geometry, dimensions, units, layers, text, and save path from the user request. If a critical dimension is missing, ask one concise question; otherwise use sensible drafting assumptions.
2. Before drawing annotations, create a simple layout plan: reserve the main geometry, dimensions, title block, tables, and detail views as forbidden rectangles.
3. Use `scripts/cad_layout.py` for labels, tables, legends, and callouts whenever a drawing has many annotations. It chooses candidate positions with rectangle collision checks and reserves the accepted location.
4. For rectangular plates with circular holes, run `scripts/draw_plate_with_holes.py` and pass dimensions as CLI arguments.
5. For other 2D drawings, reuse the COM patterns in that script: `VARIANT(VT_ARRAY | VT_R8)` points, retry COM calls when AutoCAD is busy, create layers before assigning them, and validate `ModelSpace.Count`.
6. Save output DWG files in the current workspace unless the user gives another path.
7. Report the DWG path and a short verification summary. Do not claim success until the COM script returns entity counts or the saved DWG exists.

## Annotation Conflict Avoidance

Use this rule for engineering drawings with crowded dimensions or notes:

1. Reserve fixed zones first: structure outline, dimensions, title block, tables, legends, enlarged details, and margins.
2. For each label, generate candidate boxes around its anchor: right, left, above, below, then diagonal positions.
3. Score candidates by collision count, distance from anchor, and preferred side. Pick the lowest-score conflict-free candidate.
4. If no candidate is conflict-free, move the label to an external note lane and draw a leader line.
5. Keep repeated labels sparse: do not label every identical component when numbering every 2nd or 5th item is clearer.
6. After drawing, run a bounding-box conflict report for planned labels/tables before calling the final AutoCAD save.

Implementation helper: `scripts/cad_layout.py`.

## Plate Script

Use this for requests like "draw a 1000 x 600 rectangle with two diameter 80 holes, 250 from left and right, and add dimensions":

```powershell
python "$env:USERPROFILE\.codex\skills\autocad-com-drawing\scripts\draw_plate_with_holes.py" `
  --output "C:\path\to\plate.dwg" `
  --width 1000 --height 600 `
  --hole-diameter 80 `
  --left-offset 250 --right-offset 250 `
  --title-text "1000 x 600 plate, 2-%%c80 holes"
```

Useful options:

- `--hole-centers "250,300;750,300"`: explicit hole centers; overrides left/right offsets.
- `--no-dimensions`: draw geometry without dimensions.
- `--active-document`: draw into the current active DWG instead of a new drawing.
- `--units mm|unitless`: set AutoCAD insertion units; defaults to `mm`.

## COM Notes

- AutoCAD COM is Windows-only and requires AutoCAD installed and accessible as `AutoCAD.Application`.
- If AutoCAD returns `RPC_E_CALL_REJECTED`, retry briefly instead of failing immediately.
- Use radians for `AddDimRotated` rotation.
- Use `%%c` for the AutoCAD diameter symbol in dimension text.
- If MCP AutoCAD tools are unavailable, continue with Python COM.
