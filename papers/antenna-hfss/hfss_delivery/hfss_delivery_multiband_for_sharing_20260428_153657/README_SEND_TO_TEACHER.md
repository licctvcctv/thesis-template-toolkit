# HFSS 多频段手机天线仿真交付包

## 工程文件

打开：

`hfss_project/antenna_n78_scratch_redesign_20260428_003706.aedt`

主要设计：

- `HFSSDesign_n78_phone_pifa_enhanced`：原 5G n78 专项优化设计。
- `HFSSDesign_phone_multiband_enhanced`：新增多频段扩展设计。

同名结果文件夹：

`hfss_project/antenna_n78_scratch_redesign_20260428_003706.aedtresults/`

不要漏发这个文件夹，否则对方可能需要重新仿真。

## 多频段补充结果

新增多频段设计验证了三个频段：

| 频段 | 范围 | 最差 S11 |
|---|---:|---:|
| WLAN 2.4 GHz | 2.4-2.5 GHz | -30.56 dB |
| 5G n78 | 3.3-3.8 GHz | -10.37 dB |
| WLAN 5.8 GHz | 5.725-5.85 GHz | -16.41 dB |

对应数据和过程：

- `multiband_data/final_phone_multiband_S11.csv`
- `multiband_data/multiband_candidate_log.csv`
- `HFSS_multiband_extension_report.md`

论文图片和软件截图：

- `paper_assets/figures/fig_05_final_multiband_s11.png`
- `paper_assets/figures/fig_06_multiband_candidate_comparison.png`
- `paper_assets/screenshots/hfss_ui_14_multiband_geometry.png`
- `paper_assets/screenshots/hfss_ui_15_multiband_s11_report.png`

## 注意

- `.aedt.lock` 是软件打开工程时产生的临时锁文件，不需要发送。
- 如果老师问是否有多频段调试，可以说明：先完成 n78 主频段优化，随后根据题目要求新增多频段扩展设计，并在 HFSS 中完成 2.4 GHz、n78、5.8 GHz 三频段宽频扫描验证。
