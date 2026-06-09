# 基于数据库过滤的谱图聚类 — 实验代码与参考源码

## 目录结构

```
spectrum_clustering_code/
├── README.md                          # 本文件
├── experiment/
│   └── run_experiment.py              # 主实验脚本（759行）
├── toplib_src/                        # TopLib 参考实现源码
│   ├── README.md                      # 原版使用说明
│   ├── msalign_file.py                # msalign 格式读写
│   ├── distance_calculation.py        # 碎片峰距离计算（Numba加速）
│   ├── spectra_masses_gen.py          # 谱图/质量数据入库
│   ├── ms_library_building.py         # 谱图库构建（核心）
│   ├── ms_library_query.py            # 谱图库搜索
│   ├── tsv_file_processing.py         # TSV 后处理编排
│   ├── remove_comment_lines.py        # 去掉 TopPIC 注释行
│   ├── remove_duplicated.py           # 去重复鉴定
│   ├── remove_inconsistent_prsm.py    # 去不一致 PrSM
│   ├── filter_prsm_based_on_proteoform.py
│   ├── db_gen.py                      # 创建 SQLite 库
│   ├── db_add_project.py              # 添加项目
│   ├── db_add_sample.py               # 添加样本
│   ├── db_add_method.py               # 添加方法
│   ├── db_add_experiment.py           # 添加实验
│   ├── db_add_file.py                 # 添加文件并入库
│   ├── db_query.py                    # 提取代表谱
│   ├── db_to_msalign_tsv.py           # SQLite → msalign+TSV
│   ├── db_to_msp.py                   # SQLite → NIST MSP
│   ├── db_remove_decoy_data.py        # 去除诱饵数据
│   ├── db_update_reviewed_status.py   # 更新审核状态
│   └── mzml_convert_library_mgf.py    # mzML → MGF 转换
├── input_data/                        # 实验输入数据（样例）
│   ├── Atrium-F1.msalign              # TopFD 去卷积谱图
│   ├── Atrium-F1.OUTPUT_TABLE         # TopPIC 鉴定结果
│   └── Human2018July2.fasta           # 蛋白序列库
└── data/                              # 实验输出数据
    ├── metrics.json                   # 完整指标
    ├── algorithm_comparison.csv       # 算法对比
    ├── filter_sensitivity.csv         # 阈值敏感性
    └── filter_sensitivity.json
```

---

## 数据来源

实验使用 **PRIDE PXD019368** 公共自上而下质谱数据集。

完整输入数据共 **31 个 msalign + 31 个 OUTPUT_TABLE 文件**，位于 `_source_materials/pride/PXD019368/`。
此处仅包含一个样例文件（Atrium-F1），完整数据请从 PRIDE 下载或从项目原始目录获取。

- `.msalign` 文件：TopFD 去卷积后的二级谱图（含前体质量/电荷、碎片峰）
- `.OUTPUT_TABLE` 文件：TopPIC 搜索结果（蛋白匹配、Proteoform ID、E-value 等）

---

## 实验脚本 (`experiment/run_experiment.py`)

### 整体流程

```
msalign + OUTPUT_TABLE
        ↓
read_identifications()     ← 解析 TopPIC 鉴定标签
read_spectra()             ← 解析 msalign 谱图数据
        ↓
build_database()           ← 写入 SQLite（spectrum + peak 表）
        ↓
precursor_candidates()     ← 前体质量-电荷过滤产生候选对
        ↓
fragment_cosine()          ← 计算每对候选的碎片峰余弦相似度
        ↓
run_methods()              ← 跑 5 种聚类方法（Union-Find）
create_outputs()           ← 输出指标 + 画图
```

### 核心参数

| 参数 | 值 |
|---|---|
| 碎片峰 top-N | 50 |
| 前体质量窗口 | 2.2 Da |
| 碎片峰容差 | 10 ppm |
| 相似度阈值 | 0.30, 0.50, 0.70 |

### 候选过滤

按前体电荷分组，同电荷内质量差 ≤ 2.2 Da 的谱图构成候选对：

- 全部理论谱图对: **10,032,960**
- 候选对: **14,614**
- 过滤率: **99.85%**

### 碎片峰相似度

遍历两个谱图的所有碎片峰，质量容差 10 ppm 内且电荷相同的峰做点积。

### 5 种聚类设置（Union-Find 连通聚类）

| 算法 | 使用的边 | ARI |
|---|---|---|
| 全部单谱图基线 | 无 | 0 |
| 前体质量-荷电过滤 | 所有候选对 | 0.866 |
| 过滤+相似度≥0.30 | 候选对中 score ≥ 0.30 | 0.843 |
| 过滤+相似度≥0.50 | 候选对中 score ≥ 0.50 | 0.688 |
| 过滤+相似度≥0.70 | 候选对中 score ≥ 0.70 | 0.270 |

### 评估指标

- **ARI** (Adjusted Rand Index)
- **NMI** (Normalized Mutual Information)
- **错误率**: 每个簇中非多数标签占比
- **聚类比例**

### 输出

- `data/metrics.json` — 完整指标
- `data/algorithm_comparison.csv` — 算法对比
- `data/filter_sensitivity.csv` — 阈值 0.1～0.7 敏感性
- 8 张 PNG（运行时在 `outputs/` 下生成）

---

## TopLib 参考源码 (`toplib_src/`)

TopLib 是论文公开的谱图库构建工具。`run_experiment.py` 借鉴了其核心思路，但做了简化：

| 对比项 | TopLib | 本实验脚本 |
|---|---|---|
| 聚类方法 | 层次聚类 + 代表谱 | Union-Find 连通聚类 |
| 距离函数 | `1 - cosine`，处理同位素峰 | 原始点积，仅 ppm 容差 |
| 强度处理 | log2 + L2 归一化 | log2 + L2 归一化 |
| 定位 | 通用建库搜索工具 | 验证"数据库过滤+聚类"方法的实验脚本 |

### TopLib 各模块功能

**基础层**
- `msalign_file.py` — msalign 格式解析与写入
- `distance_calculation.py` — 碎片峰余弦/欧氏距离（Numba JIT 加速）

**鉴定后处理管道**（tsv_file_processing.py 统一编排）
1. `remove_comment_lines.py` — 删前 29 行注释
2. `remove_duplicated.py` — 同蛋白且质量差 < 2.2 Da 去重
3. `remove_inconsistent_prsm.py` — 同 Proteoform ID 但不同蛋白的去不一致
4. `filter_prsm_based_on_proteoform.py` — 按 Proteoform ID 过滤 + Q-value ≤ 0.01

**建库与搜索**
- `ms_library_building.py` — 核心：前体过滤 → 层次聚类 → 代表谱 → 诱饵库
- `ms_library_query.py` — 查询谱搜索匹配
- `spectra_masses_gen.py` — 谱图/质量数据入库

**数据库管理**
- `db_gen.py` / `db_add_*.py` — 创建库结构、添加项目/样本/方法/实验/文件
- `db_query.py` — 提取代表谱
- `db_to_msalign_tsv.py` / `db_to_msp.py` — 导出 msalign/TSV/MSP
- `db_remove_decoy_data.py` / `db_update_reviewed_status.py` — 维护工具

---

## 运行方式

```bash
pip install pillow python-docx

# 需在完整数据目录下，或将 input_data/ 补全为 31 组文件
python experiment/run_experiment.py
```
