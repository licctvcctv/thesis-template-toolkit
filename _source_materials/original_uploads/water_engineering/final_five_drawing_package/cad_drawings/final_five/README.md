# 五张图纸重绘说明

本目录为按指导老师最新要求重绘的五张图纸源码。上一版 10 张增强图已清理，不作为交付成果。

## 文件拆分

- `data.py`：任务书参数、结构方案参数、水位、地质层、规范说明。
- `common.py`：A1 图框、标题栏、尺寸、表格、文字、水位线等公共制图工具。
- `g01_general_layout.py`：总平面布置图。
- `s01_high_pile_plan_elevation.py`：高桩梁板式方案平面、立面图。
- `s02_high_pile_section_detail.py`：高桩方案断面图、细部构造及代表构件配筋图。
- `s03_caisson_plan_elevation.py`：重力式沉箱方案平面、立面图。
- `s04_caisson_section_detail.py`：重力式方案断面图、细部构造及代表构件配筋图。
- `run_all.py`：AutoCAD COM 批量生成入口。

## 图纸清单

1. `G-01_general_layout.dwg`：总平面布置图。
2. `S-01_high_pile_plan_elevation.dwg`：高桩方案结构平面、立面图。
3. `S-02_high_pile_section_detail_rebar.dwg`：高桩方案断面、细部构造及代表构件配筋图。
4. `S-03_caisson_plan_elevation.dwg`：重力式方案结构平面、立面图。
5. `S-04_caisson_section_detail_rebar.dwg`：重力式方案断面、细部构造及代表构件配筋图。

## 设计逻辑

- 总平面和泊位尺度按《海港总体设计规范》JTS 165-2025 和任务书参数表达。
- 结构布置、稳定与构造按《码头结构设计规范》JTS 167-2018 表达。
- 高桩方案作为推荐方案，强调软土地基适应性、桩基入持力层、排架梁板体系。
- 重力式沉箱方案作为比选方案，明确天然软土不能直接承载，需换填/加固后再进行抗滑、抗倾、基床承载等计算。

## 运行

```bash
prlctl exec 'Windows 11' --current-user cmd /c "C:\Python313\python.exe C:\Mac\Home\Documents\hjvjhj\cad_drawings\final_five\run_all.py"
```

单独重跑某一张：

```bash
prlctl exec 'Windows 11' --current-user cmd /c "C:\Python313\python.exe C:\Mac\Home\Documents\hjvjhj\cad_drawings\final_five\run_all.py S-02"
```
