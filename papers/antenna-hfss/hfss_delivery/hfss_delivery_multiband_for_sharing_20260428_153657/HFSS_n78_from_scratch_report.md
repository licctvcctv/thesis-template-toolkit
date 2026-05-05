# HFSS n78 From-scratch Redesign Report

Date: 2026-04-28

## Topology

A new microstrip-fed printed monopole was built from scratch. It uses a stepped top radiator and a bottom partial ground with a center notch at the feed transition.

## Final Dimensions

- Substrate: Rogers RT/duroid 5880 (tm), 60 mm x 55 mm x 1.6 mm
- Feed line: Wf = 5.2 mm, Lf = 17 mm
- Radiator: Wp = 30 mm, Lp = 26 mm, Wneck = 14 mm, Lstep = 4 mm
- Partial ground: Lg = 18 mm, center notch Wgn = 12 mm, Ngd = 4 mm

## Final S11 Result

- Worst S11 over 3.3-3.8 GHz: -12.6516140832041 dB at 3.3 GHz
- Minimum S11 over 3.3-3.8 GHz: -16.5239559716396 dB at 3.8 GHz
- Below -10 dB contiguous span: 3.3-3.8 GHz

## Key Files

- hfss_scratch_project/antenna_n78_scratch_redesign_20260428_003706.aedt
- hfss_scratch_monopole/final_scratch_monopole_converged_S11.csv
- hfss_scratch_monopole/scratch_formal_refine_log.csv
- hfss_scratch_plots/scratch_result_01_final_vs_old.png
- hfss_scratch_plots/scratch_result_02_formal_refine_ranking.png
- hfss_scratch_plots/scratch_result_03_top_formal_curves.png

## Sources Used

- ETSI TS 138 104 for n78 band definition.
- IET paper on microstrip-fed UWB printed monopole using partial ground.
- ISAP paper showing lower patch notches and truncated ground as matching controls.
- Ansys scripting help for lumped port setup.