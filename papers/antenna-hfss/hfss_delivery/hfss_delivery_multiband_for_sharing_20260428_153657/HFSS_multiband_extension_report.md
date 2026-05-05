# HFSS 多频段手机天线补充报告

## 目的

原最终方案主要围绕 5G n78 频段优化。为匹配“多频段手机天线”的论文题目，本次补充了多频段情形，并在同一 HFSS 宽频扫描中验证 WLAN 2.4 GHz、5G n78 和 WLAN 5.8 GHz 三个频段。

## 最终多频段设计

- HFSS 设计名：`HFSSDesign_phone_multiband_enhanced`
- 选中候选：`pg_para_Lg17_Lp28_Wf48`
- 变量：`{'Lg': '17mm', 'Wp': '30mm', 'Lp': '28mm', 'Wf': '4.8mm'}`
- 结构特征：`{'phone_ground': True, 'parasitic': ('right', '1.2mm', '22mm', '0.9mm', '21mm')}`

## 多频段结果

| 频段 | 验证范围 | 最差 S11 |
|---|---:|---:|
| WLAN 2.4 GHz | 2.4-2.5 GHz | -30.56 dB |
| 5G n78 | 3.3-3.8 GHz | -10.37 dB |
| WLAN 5.8 GHz | 5.725-5.85 GHz | -16.41 dB |

三段频率的最差 S11 均低于 -10 dB，因此可以作为论文中的“多频段情形”补充章节。原 n78 专项优化设计仍可作为主设计过程，多频段版本作为扩展设计与对比验证。

## 建议放入论文的图表

- `hfss_paper_assets/figures/fig_05_final_multiband_s11.png`
- `hfss_paper_assets/figures/fig_06_multiband_candidate_comparison.png`
- `hfss_multiband/final_phone_multiband_S11.csv`
- `hfss_multiband/multiband_candidate_log.csv`
