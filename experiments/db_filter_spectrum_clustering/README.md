# 基于数据库过滤的谱图聚类 — 实验代码说明

## 目录结构

```
experiments/db_filter_spectrum_clustering/
├── run_experiment.py              # 主实验脚本
├── outputs/                       # 实验结果输出
│   ├── toplib_real_spectra.sqlite # SQLite 谱图数据库
│   ├── spectrum_library.sqlite
│   ├── metrics.json               # 完整实验指标
│   ├── algorithm_comparison.csv   # 算法对比
│   ├── filter_sensitivity.csv     # 阈值敏感性
│   ├── filter_sensitivity.json
│   └── *.png                      # 8 张可视化图
└── README.md                      # 本文件

_source_materials/
├── pride/
│   ├── PXD019368/                 # 实验输入数据（公共数据集）
│   │   ├── *.msalign              # 31 个谱图文件（TopFD 去卷积结果）
│   │   ├── *.OUTPUT_TABLE         # 31 个 TopPIC 鉴定结果
│   │   └── Human2018July2.fasta   # 蛋白序列库
│   └── PXD029703/
│       ├── CRC_SW480_SEC4_RPLC1.raw  # 原始 RAW 文件样例
│       └── Note.docx
└── toplib/                        # TopLib 参考实现源码
    ├── README.md                  # 原版使用说明
    ├── requirements.txt
    ├── LICENSE
    └── src/
        ├── msalign_file.py              # msalign 读写
        ├── distance_calculation.py      # 碎片峰距离计算
        ├── spectra_masses_gen.py        # 谱图/质量入库
        ├── ms_library_building.py       # 谱图库构建
        ├── ms_library_query.py          # 谱图库搜索
        ├── tsv_file_processing.py       # TSV 后处理
        ├── remove_comment_lines.py      # 去掉 TopPIC 输出注释行
        ├── remove_duplicated.py         # 去重复鉴定
        ├── remove_inconsistent_prsm.py  # 去不一致 PrSM
        ├── filter_prsm_based_on_proteoform.py  # 按蛋白型过滤
        ├── db_gen.py                    # 创建 SQLite 库
        ├── db_add_project.py            # 添加项目
        ├── db_add_sample.py             # 添加样本
        ├── db_add_method.py             # 添加方法
        ├── db_add_experiment.py         # 添加实验
        ├── db_add_file.py               # 添加文件/入库
        ├── db_query.py                  # 查询/提取代表谱
        ├── db_to_msalign_tsv.py         # SQLite → msalign + TSV
        ├── db_to_msp.py                 # SQLite → NIST MSP
        ├── db_remove_decoy_data.py      # 去除诱饵数据
        ├── db_update_reviewed_status.py # 更新审核状态
        └── mzml_convert_library_mgf.py  # mzML → MGF 转换
```

---

## 数据来源

实验使用 **PRIDE PXD019368** 公共自上而下质谱数据集。

- **31 个 `.msalign` 文件**: TopFD 去卷积后的二级谱图，含前体质量/电荷、碎片峰列表
- **31 个 `.OUTPUT_TABLE` 文件**: TopPIC 搜索鉴定结果，含蛋白匹配、PrSM ID、E-value 等
- 原始 RAW 文件已通过 msconvert + TopFD + TopPIC 预处理成上述格式，无需重复处理
- 最终使用 **4480 张有鉴定谱图**，对应 **2505 个 ground-truth 组**

---

## 实验主脚本：`run_experiment.py`

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
run_methods()              ← 跑 5 种聚类方法
create_outputs()           ← 输出结果 + 画图
```

### 核心参数

| 参数 | 值 |
|---|---|
| 碎片峰 top-N | 50 |
| 前体质量窗口 | 2.2 Da |
| 碎片峰容差 | 10 ppm |
| 相似度阈值 | 0.30, 0.50, 0.70 |

### 候选过滤逻辑

`precursor_candidates()` 按前体电荷分组，同电荷内质量差 ≤ 2.2 Da 的谱图构成候选对：

- 全部理论谱图对: **10,032,960**
- 候选对: **14,614**
- 过滤率: **99.85%**

### 碎片峰相似度计算

`fragment_cosine()` 遍历两个谱图的所有碎片峰，质量容差 10 ppm 内且电荷相同的峰做点积：

```python
while i < len(a) and j < len(b):
    if abs(mass_a - mass_b) <= tolerance and charge_a == charge_b:
        score += intensity_a * intensity_b
```

### 5 种聚类设置

| 算法 | Union-Find 使用的边 | 含义 |
|---|---|---|
| 全部单谱图基线 | 无 | 每个谱图独立一簇 |
| 前体质量-荷电过滤 | 所有候选对 | 仅靠前体过滤聚类 |
| 过滤+相似度≥0.30 | 候选对中 score ≥ 0.30 | 论文基准方案 |
| 过滤+相似度≥0.50 | 候选对中 score ≥ 0.50 | 更严格 |
| 过滤+相似度≥0.70 | 候选对中 score ≥ 0.70 | 最严格 |

### 评估指标

- **ARI** (Adjusted Rand Index): 聚类与 ground truth 的一致性
- **NMI** (Normalized Mutual Information): 归一化互信息
- **错误率**: 每个簇中非多数标签的谱图占比
- **聚类比例**: 处于大小 > 1 簇中的谱图比例

### 输出文件

`outputs/` 目录产生:
- `metrics.json` — 完整指标（含数据集元信息、算法对比、阈值敏感性）
- `algorithm_comparison.csv` — 算法对比表
- `filter_sensitivity.csv` — 阈值 0.1～0.7 的敏感性分析
- 8 张 PNG 图:
  - `algorithm_metrics.png` — 聚类质量对比
  - `runtime_comparison.png` — 运行时间与保留边数
  - `candidate_reduction.png` — 候选空间压缩
  - `memory_comparison.png` — 峰值内存对比
  - `filter_sensitivity.png` — 阈值敏感性
  - `similarity_histogram.png` — 相似度分布直方图
  - `cluster_size_distribution.png` — 簇规模分布
  - `cluster_projection.png` — 前体质量-电荷投影

---

## TopLib 参考源码说明

`_source_materials/toplib/` 是 TopLib 论文公开的参考实现，用于自上而下质谱谱图库的构建和搜索。

### 分层说明

**基础层 — 数据格式处理**

| 文件 | 功能 |
|---|---|
| `msalign_file.py` | 读写 `.msalign` 格式（TopFD/TopPIC 的标准谱图格式） |
| `distance_calculation.py` | 碎片峰余弦距离/欧氏距离计算（Numba 加速） |
| `mzml_convert_library_mgf.py` | mzML → MGF 转换 |

**鉴定结果后处理**

| 文件 | 功能 |
|---|---|
| `tsv_file_processing.py` | 编排整个后处理流程 |
| `remove_comment_lines.py` | 删除 TopPIC 输出的前 29 行注释 |
| `remove_duplicated.py` | 去重复：同蛋白且前体质量差 < 2.2 Da |
| `remove_inconsistent_prsm.py` | 去不一致：同 Proteoform ID 但不同蛋白 |
| `filter_prsm_based_on_proteoform.py` | 按 Proteoform ID 过滤 + Q-value ≤ 0.01 |

**谱图库构建**

| 文件 | 功能 |
|---|---|
| `spectra_masses_gen.py` | 将 msalign 谱图和碎片峰插入 SQLite 的 spectra/masses 表 |
| `ms_library_building.py` | 核心建库：前体过滤 → 层次聚类 → 生成代表谱 → 诱饵库 |
| `ms_library_query.py` | 查询谱图对库进行搜索匹配 |

**数据库管理**

| 文件 | 功能 |
|---|---|
| `db_gen.py` | 创建完整 SQLite 库表结构 |
| `db_add_project.py` | 添加项目元数据 |
| `db_add_sample.py` | 添加样本元数据 |
| `db_add_method.py` | 添加仪器/方法元数据 |
| `db_add_experiment.py` | 添加实验元数据 |
| `db_add_file.py` | 添加文件到库（写入谱图+建代表谱） |
| `db_query.py` | 按项目提取代表谱（msalign + TSV） |
| `db_to_msalign_tsv.py` | SQLite 库导出为 msalign + TSV |
| `db_to_msp.py` | SQLite 库导出为 NIST MSP 格式 |
| `db_remove_decoy_data.py` | 去除诱饵数据 |
| `db_update_reviewed_status.py` | 自动审核标记 |

### TopLib 与实验脚本的关系

`run_experiment.py` 借鉴了 TopLib 的核心思路（前体过滤 + 碎片相似度），但做了简化和关键差异：

- TopLib 使用层次聚类+代表谱；`run_experiment.py` 使用 Union-Find 连通聚类
- TopLib 的距离函数 `peak_50_cosine_mass_ppm()` 返回 `1 - cosine` 作为距离，且处理了同位素峰（±1.00235 Da）；`run_experiment.py` 的 `fragment_cosine()` 返回原始点积（不处理同位素，仅 10 ppm 容差内匹配）
- `run_experiment.py` 的碎片峰强度先做 log2 再 L2 归一化；TopLib 的 `ms_spectrum_preprocess()` 类似
- TopLib 是通用建库搜索工具；`run_experiment.py` 是专为验证"数据库过滤+谱图聚类"方法而写的实验脚本

---

## 如何运行

```bash
# 依赖（自动尝试切换到 bundled Python，若 Pillow 缺失）
pip install pillow python-docx

# 运行实验（在项目根目录下）
python experiments/db_filter_spectrum_clustering/run_experiment.py
```

输入数据已预置于 `_source_materials/pride/PXD019368/`，脚本直接读取，无需额外下载。
