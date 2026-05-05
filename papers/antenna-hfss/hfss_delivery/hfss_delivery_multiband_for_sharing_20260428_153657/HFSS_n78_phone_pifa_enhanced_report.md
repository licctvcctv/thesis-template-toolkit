# HFSS n78 Phone/PIFA-style Enhanced Report

Date: 2026-04-28

## Why This Version Was Added

The clean from-scratch printed monopole has strong S11 performance, but it looks more like a laboratory antenna than a handset antenna. This version keeps the good n78 matching while adding phone-terminal features: an extended handset ground and a coupled parasitic antenna branch near the radiator.

## Final Selected Structure

- Base antenna: microstrip-fed printed monopole with partial ground
- Added phone feature 1: extended handset main ground behind the antenna
- Added phone feature 2: right-side coupled parasitic branch, 1.2 mm x 24 mm, 0.9 mm coupling gap
- Tested but not kept: direct PIFA shorting wall and side-frame strips, because they degraded the n78 match below target

## Final S11 Result

- Design: HFSSDesign_n78_phone_pifa_enhanced
- Selected case: phone_ground_right_parasitic
- Worst S11 over 3.3-3.8 GHz: -10.7677807288241 dB at 3.8 GHz
- Minimum S11 over 3.3-3.8 GHz: -12.7667292777427 dB at 3.3 GHz
- Below -10 dB span: 3.3-3.8 GHz

## Engineering Interpretation

The direct shorting-wall PIFA feature made the structure look closer to a classical PIFA, but it pulled the impedance match above -10 dB and was therefore rejected. The coupled parasitic branch is a better compromise for this model: it makes the antenna more handset-like while preserving the n78 return-loss requirement.

## Key Files

- hfss_scratch_monopole/final_phone_pifa_balanced_S11.csv
- hfss_scratch_monopole/phone_pifa_balanced_final_summary.csv
- hfss_scratch_monopole/phone_pifa_enhance_log.csv
- hfss_scratch_plots/scratch_result_07_phone_pifa_vs_base_old.png
- hfss_scratch_plots/scratch_result_08_phone_pifa_candidate_ranking.png