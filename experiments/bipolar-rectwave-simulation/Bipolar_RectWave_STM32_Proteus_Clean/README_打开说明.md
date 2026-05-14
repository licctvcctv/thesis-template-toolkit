# STM32 双极性矩形波发射控制系统仿真包

## 目录说明

- `01_Proteus仿真/RectWave_Simulation.pdsprj`
  - Proteus 仿真工程。
  - U1 程序文件已指向 `..\Firmware\Rect\MDK-ARM\Rect\RectWave.hex`。

- `Firmware/Rect`
  - STM32 源码和 Keil 工程。
  - Keil 工程：`MDK-ARM/RectWave.uvprojx`。
  - 最终 HEX：`MDK-ARM/Rect/RectWave.hex`。
  - 主要代码：`Core/Src/main.c`、`Core/Src/MCP4921.h`、`Core/Src/vSPI.h`、`Core/Src/gpio.c`。

- `03_测试结果`
  - `双极性矩形波_测试统计表.xlsx`：频率、幅值、矩形波性能和结论统计。
  - `波形采样数据表.xlsx`：波形采样明细。
  - `波形采样原始数据.csv`：CSV 原始采样数据。
  - `仿真与测试结果说明.md`：仿真结论说明。
  - `HEX备份_RectWave.hex`：HEX 备份。
  - `Keil编译日志.log`：Keil 编译日志。

- `04_图片`
  - `Proteus_电路模型局部图.png`。
  - `Proteus_示波器波形显示图.png`。
  - `数字示波器_矩形波测量图.png`。

## 打开方式

1. 打开 Proteus。
2. 打开 `01_Proteus仿真/RectWave_Simulation.pdsprj`。
3. 点击运行仿真。
4. 如果提示找不到 HEX，手动把 U1 的 Program File 指向：

```text
Firmware\Rect\MDK-ARM\Rect\RectWave.hex
```

## 当前默认参数

- 输出波形：双极性矩形波等效输出。
- 默认频率：`12.5 Hz`。
- 倍频范围：`12.5 Hz x N`，N=1..8。
- 默认幅值：等效 `±20 V`。
- 幅值档位：`±5 V`、`±10 V`、`±15 V`、`±20 V`。
- 触发方式：手动运行和外部 PB0 上升沿触发。
- 响应时间：毫秒级，满足 `≤30s` 指标。

## 说明

本包只保留最终交付文件。调试过程截图、探针查找截图、菜单截图、临时解包文件、Keil 编译中间文件均未放入。
