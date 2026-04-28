# HFSS n78 Paper Assets Index

Date: 2026-04-28

## Final Design

- Final selected HFSS design: `HFSSDesign_n78_phone_pifa_enhanced`
- Structure type: phone/PIFA-style enhanced n78 antenna
- Added phone features: extended handset ground and coupled parasitic branch
- n78 target: 3.3-3.8 GHz
- Worst S11: -10.7677807288241 dB
- Worst S11 frequency: 3.8 GHz
- Max VSWR: 1.8148197659118377
- Max mismatch loss: 0.3800769202143621 dB

## Recommended Figures for Paper

1. `figures/fig_01_final_phone_pifa_s11.png`: final S11 curve.
2. `figures/fig_02_final_phone_pifa_zin.png`: input impedance.
3. `figures/fig_03_final_phone_pifa_vswr.png`: VSWR.
4. `figures/scratch_result_07_phone_pifa_vs_base_old.png`: old model vs clean redesign vs phone/PIFA enhanced.
5. `figures/scratch_result_08_phone_pifa_candidate_ranking.png`: tested phone/PIFA enhancement candidates.
6. `screenshots/05_hfss_phone_pifa_enhanced_geometry.png`: HFSS final geometry screenshot.
7. `screenshots/hfss_ui_02_s11_rectangular_plot.png`: HFSS software S11 report screenshot.
8. `screenshots/hfss_ui_03_vswr_rectangular_plot.png`: HFSS software VSWR report screenshot.
9. `screenshots/hfss_ui_05_smith_chart.png`: HFSS software Smith chart screenshot.
10. `screenshots/hfss_ui_09_3d_gain_total.png`: HFSS software 3D gain pattern screenshot.
11. `screenshots/hfss_ui_13_theta_phi_gain_contour.png`: HFSS software Theta/Phi gain contour screenshot.

## HFSS Software Screenshots

The `screenshots/` folder now contains 13 AEDT/HFSS screenshots exported from the active project window:

- final geometry and project tree
- S11 rectangular plot
- VSWR rectangular plot
- input impedance plot
- Smith chart
- modal data table
- gain cuts at Phi=0 deg and Phi=90 deg
- 3D total gain pattern
- polar radiation pattern
- radiation data table
- Theta/Phi gain surface
- Theta/Phi gain contour

Use `screenshots/hfss_ui_screenshot_index.csv` to match each screenshot to the corresponding test/view.

## HFSS Report CSV Data

The `data/` folder includes HFSS-exported CSV data for the new report screenshots:

- `hfss_report_01_s11_from_aedt.csv`
- `hfss_report_02_vswr_from_aedt.csv`
- `hfss_report_03_input_impedance_from_aedt.csv`
- `hfss_report_04_smith_chart_from_aedt.csv`
- `hfss_report_05_modal_data_table_from_aedt.csv`
- `hfss_report_06_radiation_gain_phi0_from_aedt.csv`
- `hfss_report_07_radiation_gain_phi90_from_aedt.csv`
- `hfss_report_08_3d_gain_total_from_aedt.csv`
- `hfss_report_09_radiation_polar_phi0_from_aedt.csv`
- `hfss_report_10_radiation_data_table_from_aedt.csv`
- `hfss_report_11_theta_phi_gain_surface_from_aedt.csv`
- `hfss_report_12_theta_phi_gain_contour_from_aedt.csv`

Use `data/hfss_report_data_index.csv` to match each CSV to the corresponding HFSS report.

## Data Folders

- `data/`: CSV result data exported from HFSS and calculated RF metrics.
- `process/`: full design process timeline and combined candidate logs.
- `figures/`: publication-style PNG plots.
- `screenshots/`: HFSS UI screenshots.

## Process Notes

The teacher reference model was preserved and used as a comparison baseline. The clean redesigned antenna met the n78 S11 target with stronger margin, but looked too simple for a handset antenna. The final selected version therefore adds handset ground and a coupled parasitic branch. Direct shorting-wall PIFA and side-frame variants were tested but rejected because they degraded matching.
