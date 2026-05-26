#!/usr/bin/env python3
"""Regenerate precise CAD detail crops from the original user-provided sheets."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
SRC = IMG / "user_provided"
OUT = IMG / "cad_details" / "expanded"


def crop_sheet(source: str, output: str, box: tuple[int, int, int, int]) -> None:
    """Crop by (left, top, right, bottom) pixel coordinates."""
    OUT.mkdir(parents=True, exist_ok=True)
    with Image.open(SRC / source) as im:
        im.crop(box).save(OUT / output)


def main() -> None:
    # General layout sheet: keep functional zones and transport interface only.
    crop_sheet(
        "G-01_general_layout_revised_rail_road.png",
        "fig3-2-yard-functional-zone-cad.png",
        (3650, 1050, 5600, 3500),
    )
    crop_sheet(
        "G-01_general_layout_revised_rail_road.png",
        "fig3-3-quay-apron-road-cad.png",
        (3350, 3420, 5650, 4250),
    )
    crop_sheet(
        "G-01_general_layout_revised_rail_road.png",
        "fig3-4-gate-rail-interface-cad.png",
        (3830, 360, 5260, 1800),
    )

    # Caisson sheet: separate main section, representative reinforcement and tables.
    crop_sheet(
        "S-02_caisson_section_detail_rebar_combined.png",
        "fig4-7-caisson-section-enlarged-cad.png",
        (720, 600, 6800, 4050),
    )
    crop_sheet(
        "S-02_caisson_section_detail_rebar_combined.png",
        "fig5-2-caisson-rebar-enlarged-cad.png",
        (420, 4200, 4050, 5600),
    )
    crop_sheet(
        "S-02_caisson_section_detail_rebar_combined.png",
        "fig6-1-caisson-parameter-table-cad.png",
        (7050, 4060, 8400, 5700),
    )

    # Large-cylinder sheet: keep the actual cylinder section/detail areas.
    crop_sheet(
        "C-02_large_cylinder_section_detail_rebar.png",
        "fig4-8-cylinder-section-enlarged-cad.png",
        (680, 1250, 7000, 5550),
    )
    crop_sheet(
        "C-02_large_cylinder_section_detail_rebar.png",
        "fig5-3-cylinder-detail-rebar-cad.png",
        (5350, 1600, 7250, 4150),
    )


if __name__ == "__main__":
    main()
