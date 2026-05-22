# S-02 沉箱断面及 A-A 平面参考图补充包

这个包是单独补上的早期“按参考图复刻”的沉箱 S-02 图纸和脚本。

## 内容

- `script/draw_caisson_exact.py`
  - 生成 `S-02_caisson_section_AA_plan_reference_exact_v4.dwg` 的主脚本。
- `script/cad.py`
  - AutoCAD COM 公共绘图封装，脚本运行时需要。
- `dwg/S-02_caisson_section_AA_plan_reference_exact_v4.dwg`
  - 最终较稳定版本，包含沉箱码头断面和右侧 A-A 平面图。
- `dwg/S-02_caisson_section_AA_plan_reference_exact_v3.dwg`
  - 上一个版本，留作对照。
- `dwg/caisson_reference_exact_only.zip`
  - 原来单独打包的 S-02 参考图成果包。
- `screenshots/`
  - AutoCAD 打开自检截图。

## 本项目接入

已把 `draw_caisson_exact.py` 接入到项目根目录的 `caisson_only_reference_exact/`，并调整为导入当前项目的 `05_绘图脚本/cad.py`。主绘图脚本会优先使用这个参考模块；只有该模块不存在时才使用兜底沉箱结构。
