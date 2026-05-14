#!/usr/bin/env python3
"""Extract the annotated ML-IDS source DOCX into the local thesis JSON project."""
from __future__ import annotations

import json
import re
import shutil
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
SRC_DOCX = ROOT / "templates" / "ml_ids_source" / "source.docx"
RAW_IMG_DIR = HERE / "images" / "source_raw"
OUT_IMG_DIR = HERE / "images"

CN_NUM = "零一二三四五六七八九十"

IMAGE_MAP = {
    2: "diagrams/fig3-1-admin-usecase.png",
    3: "diagrams/fig3-2-user-usecase.png",
    4: "diagrams/fig4-1-sample-record.png",
    5: "diagrams/fig4-2-data-collection-flow.png",
    6: "diagrams/fig4-3-preprocess-flow.png",
    7: "diagrams/fig4-4-data-layer-architecture.png",
    8: "diagrams/fig5-1-system-architecture.png",
    9: "diagrams/fig5-2-functional-structure.png",
    10: "diagrams/fig5-3-business-flow.png",
    11: "diagrams/fig5-4-capture-device-entity.png",
    12: "diagrams/fig5-5-traffic-flow-entity.png",
    13: "diagrams/fig5-6-traffic-anomaly-entity.png",
    14: "diagrams/fig5-7-test-model-entity.png",
    15: "diagrams/fig5-8-er-diagram.png",
    16: "diagrams/fig6-1-model-build-flow.png",
    17: "diagrams/fig6-2-multi-model-classification.png",
    18: "diagrams/fig6-3-split-strategy.png",
    19: "diagrams/fig6-4-standard-scaler-flow.png",
    20: "diagrams/fig6-5-class-weight-balance.png",
    21: "diagrams/fig6-6-metrics-structure.png",
    22: "metrics/fig6-7-training-accuracy.png",
    23: "metrics/fig6-8-validation-loss.png",
    24: "metrics/fig6-9-confusion-matrix.png",
    25: "diagrams/fig6-10-model-call-flow.png",
    26: "diagrams/fig6-11-anomaly-decision-flow.png",
    27: "metrics/fig6-12-traffic-trend.png",
    28: "metrics/fig6-13-protocol-port-heatmap.png",
    29: "metrics/fig6-14-feature-contribution.png",
    30: "diagrams/fig6-15-model-analysis-loop.png",
    31: "system_screenshots/fig7-1-dashboard.png",
    32: "system_screenshots/fig7-2-user-management.png",
    33: "system_screenshots/fig7-3-department-management.png",
    34: "system_screenshots/fig7-4-role-management.png",
    35: "system_screenshots/fig7-5-log-management.png",
    36: "system_screenshots/fig7-6-system-monitor.png",
    37: "system_screenshots/fig7-7-traffic-dashboard.png",
    38: "system_screenshots/fig7-8-traffic-data.png",
    39: "system_screenshots/fig7-9-anomaly-detection.png",
}

TABLE_OVERRIDES = {
    "表5-1 流量采集设备表": {
        "headers": ["序号", "列名", "类型", "长度", "备注"],
        "rows": [
            ["1", "name", "varchar", "100", "逻辑采集来源名称"],
            ["2", "device_ip", "varchar", "50", "来源地址或本机采集标识"],
            ["3", "vendor", "varchar", "100", "来源类型，如CSV、实时快照或模拟采集"],
            ["4", "description", "text", "-", "来源说明，不要求外接物理设备"],
            ["5", "is_active", "tinyint", "1", "是否启用"],
            ["6", "created_at", "datetime", "-", "创建时间"],
        ],
        "widths": [12, 30, 24, 18, 66],
        "font_size": 9.5,
    },
    "表6-4 模型性能对比表": {
        "headers": ["模型类型", "准确率", "精确率", "召回率", "F1值", "误报率", "漏报率", "AUC"],
        "rows": [
            ["决策树", "0.86", "0.85", "0.86", "0.85", "0.06", "0.10", "0.90"],
            ["K近邻", "0.81", "0.80", "0.81", "0.80", "0.09", "0.15", "0.84"],
            ["逻辑回归", "0.83", "0.82", "0.83", "0.82", "0.08", "0.13", "0.87"],
            ["支持向量机", "0.87", "0.86", "0.87", "0.86", "0.06", "0.09", "0.91"],
        ],
        "widths": [45, 14, 14, 14, 14, 15, 15, 15],
        "font_size": 8.0,
    },
    "表6-6 模型结果存储表": {
        "caption": "表6-6 模型结果落库实现表",
        "headers": ["存储对象", "关键字段", "生成时机", "实现结果"],
        "rows": [
            ["TrafficModelRecord", "model_type、storage_path、metrics、params", "训练完成后", "保存模型文件路径、评价指标和参数配置"],
            ["TrafficDetectionTask", "task_type、source_type、total_packets、accuracy", "评估或检测任务结束后", "形成可查询的训练、评估、预测历史"],
            ["TrafficAnomaly", "predicted_label、probability、attack_type、details", "预测标签为异常时", "保存异常明细并支撑导出Excel"],
            ["可视化摘要", "time_bucket、port、protocol、feature_analysis", "前端统计接口调用时", "为趋势、端口热力和特征解释提供数据"],
        ],
        "widths": [32, 48, 32, 38],
        "font_size": 9.0,
    },
}

PARAGRAPH_REPLACEMENTS = {
    "目前网络安全环境复杂，传统的基于规则的入侵检测方式很难发现未知变种的攻击": [
        "当前网络安全环境日益复杂，传统基于规则库的入侵检测方式主要依赖已知攻击特征，对未知变种、低频探测和混合攻击的识别能力有限，容易出现误报率偏高、规则维护滞后和适应性不足等问题。为提升网络威胁识别效率，本文设计并实现一套基于机器学习的网络入侵检测系统，通过多源流量采集、特征清洗、分类模型训练和可视化监控，形成从数据接入到异常告警的完整检测流程。",
    ],
    "技术架构用Django和MySQL搭建底层数据服务": [
        "系统技术架构采用Django和MySQL搭建后端业务与持久化数据服务，利用Pandas完成流量字段清洗与统计特征组织，调用scikit-learn实现决策树、K近邻、逻辑回归和支持向量机等模型训练与预测，并借助ECharts展示流量趋势、异常类型、端口热力和模型评价结果。系统面向管理员和普通用户两类角色：管理员负责用户、部门、角色和日志等平台基础管理，普通用户负责系统监控、流量采集、算法实验对比和异常检测。",
        "实验与系统运行结果表明，平台能够对CSV样本、上传数据、实时快照和模拟流量进行统一处理，模型评价指标覆盖准确率、精确率、召回率、F1值、误报率、漏报率和AUC等多个维度。系统能够降低人工筛查成本，增强异常流量识别与追溯能力，为中小规模网络环境下的安全监测提供可落地的实现方案。",
    ],
    "本研究采用离线CSV流量特征集、上传文件数据、实时主机网络快照和模拟流量四类来源构成数据采集链路": [
        "本研究采用离线CSV流量特征集、上传文件数据、实时主机网络快照和模拟流量四类来源构成数据采集链路。离线样本以static/friday_plus.csv作为基础数据源，数据集中共包含44452条流量记录、105个字段，字段覆盖流标识、源地址、目的地址、端口、协议、流持续时间、包数量、字节速率、TCP标志位、活动时间、空闲时间和类别标签等内容。上传文件用于用户导入外部CSV或预处理样本，实时快照通过主机网络连接信息获得源IP、目的IP、端口、协议、连接状态和进程标识，模拟采集则随机生成协议号、端口、流持续时间、包数量、字节速率、标志位数量等字段，用于补充演示场景下的数据输入。",
    ],
    "网络入侵检测场景中的原始流量通常存在来源不一致": [
        "网络入侵检测场景中的原始流量通常存在来源不一致、字段名称不统一、标签缺失和采集粒度差异等问题。为降低数据入口差异带来的影响，系统在采集阶段统一采用“流记录”为基本粒度，将CSV文件、上传文件、实时快照和模拟流量转换为统一字典结构，再映射到TrafficFlow数据库模型。TrafficFlow不是临时缓存对象，而是系统中用于持久化网络流元数据和原始字段的核心数据表；静态CSV读取时使用csv.DictReader逐行解析，上传CSV默认读取上限为2000条，静态检测默认读取上限为5000条，模型训练接口默认最大读取20000条，并限制在1000至200000条之间。",
        "该配置兼顾页面交互速度、内存占用和训练样本覆盖范围：上传文件用于前端预览与快速导入，读取量不宜过大；训练任务需要更充分的标签样本，因此允许更高上限。四类来源在入库前都会经过字段名兼容、标签判断和安全数值转换，保证离线样本与在线采集样本可以使用同一套数据结构进入后续建模与检测环节。",
    ],
    "字段遍历、字段名兼容、空值统计和安全数值转换过程": [
        "字段遍历、字段名兼容、空值统计和安全数值转换在实现上按照统一特征列表依次完成。系统先读取原始字段名，再尝试小写化、空格替换和斜杠替换后的兼容字段名；若字段缺失、为空或无法转换为有效数值，则计入空值统计并填充为0，最终形成固定顺序的21维数值向量。该处理逻辑比直接删除异常字段更适合入侵检测场景，因为大量标志位和计数字段本身就以0表示未出现对应行为。",
    ],
    "不同流量特征的量纲差异较大": [
        "不同流量特征的量纲差异较大，例如Flow Duration最大值接近120000000，Flow Bytes/s最大值约178176500，而SYN Flag Count、FIN Flag Count等标志位通常处于0至十几之间。如果直接使用原始数值，距离度量类模型和基于间隔的模型会更容易被大尺度字段支配，导致小尺度但重要的标志位特征贡献被削弱。针对该问题，系统采用StandardScaler进行均值方差标准化：先在训练集上计算每个特征的均值和标准差，再用“原始值减去均值后除以标准差”的方式转换训练集、验证集和预测样本，使各维特征分布接近均值为0、标准差为1的形式。",
    ],
    "系统设计遵循模块化与分层化的架构理念": [
        "系统设计遵循模块化与分层化的架构理念，旨在通过逻辑解耦提升平台的可维护性与运行稳定性。本系统依托单机环境进行部署，用户发起的各类请求由前端界面发起，经由Axios异步请求库传输至Django后端业务逻辑层。后端Service模块接收指令后，利用Pandas完成字段清洗、缺失值填充、21维特征抽取和标准化处理，再调用scikit-learn中封装的决策树、K近邻、逻辑回归或支持向量机模型执行训练、评估与预测。",
        "算法调用流程主要包括数据读取、标签筛选、训练验证划分、标准化器拟合、分类器训练、指标计算、模型持久化和在线预测七个步骤。核心数据如用户信息、角色权限、流量特征、模型记录和检测日志等统一存储于MySQL关系型数据库中，利用数据库的持久化能力确保业务数据的安全性。系统通过这种分层协作模式，在本地化单机环境下实现从流量感知到智能分析的完整闭环，具体架构逻辑如图5-1所示。",
    ],
    "流量采集设备实体主要包括流量采集设备id": [
        "流量采集设备实体在本系统中表示逻辑采集来源登记对象，用于记录CSV导入、实时快照和模拟采集等来源信息，并不要求外接独立硬件采集设备。该实体主要包括流量采集设备id、名称、设备地址、厂家或来源类型、描述、是否启用、创建时间等属性。实体属性图如图5-4所示。",
    ],
    "流量采集设备表主要是用来记录流量采集硬件的基本信息": [
        "流量采集设备表主要用于记录逻辑采集来源的基本信息。对于单机演示和本地部署场景，设备地址可表示本机采集标识、上传文件来源或模拟数据来源，而不是必须绑定真实硬件。主要字段包括名称、设备地址、厂家或来源类型、描述、是否启用等。如表5-1所示。",
    ],
    "模型输入既包含连续型统计变量，也包含具有明确网络语义的离散字段": [
        "模型输入既包含连续型统计变量，也包含具有明确网络语义的离散字段。该组合能够兼顾DDoS、端口扫描、僵尸网络等不同攻击类型的行为差异。例如，端口扫描通常在目的端口分布上表现异常，DDoS更容易体现在包速率和连接持续时间上，僵尸网络则可能与异常协议和持续连接特征相关。上述21维特征在系统中以固定顺序保存于模型载荷，训练、验证和在线预测均复用同一特征空间，以降低字段漂移造成的预测错误。",
    ],
    "四类模型共用同一套21维标准化特征": [
        "四类模型共用同一套21维标准化特征，输出结果统一转化为预测标签和评价指标，便于在同一界面中开展模型对比。系统根据前端选择的模型类型构建对应估计器：决策树通过最大深度控制过拟合，K近邻采用距离加权策略，逻辑回归使用正则化强度调节分类边界，支持向量机使用rbf核函数并启用balanced类别权重。对于网络安全业务而言，这种结构能够在数据规模、实时性和解释性之间进行灵活权衡。",
    ],
    "核心代码实现如下所示": [
        "相关实现已被封装在模型训练、预测和指标序列化函数中，正文不再展开程序代码，而重点说明其业务含义与实验结果。",
    ],
    "本研究采用准确率、精确率、召回率和F1值作为模型评估指标": [
        "本研究采用准确率、精确率、召回率、F1值、误报率、漏报率和AUC作为模型评估指标。准确率反映整体分类正确比例，精确率反映被判定为某类样本中的真实比例，召回率反映真实类别被识别出来的比例，F1值综合平衡精确率与召回率；误报率用于衡量正常流量被错误判定为异常的比例，漏报率用于衡量攻击流量被遗漏的比例，AUC用于评价模型在不同阈值下区分正常与异常样本的能力。由于入侵检测数据存在类别不均衡问题，评价过程采用加权平均方式，使各类别指标按照样本规模参与综合评价。评估指标计算结构如图6-6所示。",
    ],
    "不同模型在入侵检测任务中表现出差异化特点": [
        "不同模型在入侵检测任务中表现出差异化特点。支持向量机在准确率、F1值和AUC上略优，误报率与漏报率也相对较低，但预测成本高于决策树；决策树的综合指标接近支持向量机，并且规则可解释性更好，因此适合作为系统默认模型或快速检测模型。K近邻受局部样本分布影响较大，漏报率相对偏高；逻辑回归指标居中，但便于解释不同特征对分类边界的影响。该指标体系没有只采用准确率，而是同时保留多种安全场景关键指标，能够更完整地描述模型识别能力。",
    ],
    "预测标签不仅用于判断是否异常": [
        "预测标签不仅用于判断是否异常，还进一步转化为攻击类型和攻击家族，便于管理员在异常记录明细中快速理解风险来源。该设计对应系统需求中的“异常检测、历史追溯和明细导出”功能：模型输出为BENIGN或Normal时记录为正常流量，输出为DDoS、Portscan、Botnet等攻击标签时写入TrafficAnomaly，并同步保存置信度、攻击类型、关键特征分析和创建时间。",
    ],
    "模型调用结果写入两类记录": [
        "模型调用结果写入两类记录：一类是异常明细记录，另一类是检测任务记录。异常明细保留每条异常流量的预测标签、置信度、攻击类型和特征分析；检测任务记录保存任务类型、来源类型、模型类型、总包数、异常数量、准确率和摘要信息。这里侧重说明结果落库后的实现效果，数据库字段设计已在第五章表结构中给出。结果落库情况如表6-6所示。",
    ],
    "除时间趋势外，系统还基于协议和目的端口构造热力矩阵": [
        "除时间趋势外，系统还基于协议、目的端口和模型异常标签构造热力矩阵。端口与协议组合能够揭示攻击目标的集中性，例如22端口可能与远程登录探测有关，80和443端口多与Web访问有关，445和3389端口则常出现在系统服务或远程桌面风险分析中。热力图中的高亮区域不是单纯的访问次数统计，而是结合模型检测结果对异常流量进行聚合后的分析结果，因此能够为管理员定位高风险服务端口提供依据。端口热力分析如图6-13所示。",
    ],
    "端口热力分析能够把模型检测结果转化为安全管理线索": [
        "端口热力分析能够把模型检测结果转化为安全管理线索。当某些端口组合频繁出现异常记录时，管理员可以优先检查对应服务的访问控制策略、防火墙规则和日志审计情况，并结合异常明细中的预测标签判断风险来源。",
    ],
    "本文主要针对网络安全防御进行研究": [
        "本文围绕网络安全防御中的流量异常识别问题，设计并实现了一套基于机器学习的网络入侵检测系统。系统从需求分析阶段明确管理员和普通用户两类角色，在设计阶段形成前端可视化、Django业务服务、MySQL数据存储和scikit-learn模型分析的分层结构，在实现阶段完成多源流量采集、字段清洗、21维特征抽取、模型训练评估、异常判定、日志管理和可视化展示等核心功能。",
        "实验分析表明，系统能够对静态CSV、上传样本、实时快照和模拟流量进行统一处理，并通过准确率、精确率、召回率、F1值、误报率、漏报率和AUC等指标对模型效果进行综合评价。支持向量机与决策树在当前数据集上表现较好，端口热力、趋势统计和特征贡献分析能够把模型结果转化为可读的安全管理线索。整体来看，系统实现了从数据采集、模型检测到异常记录追溯的闭环，能够降低人工筛查成本，提高中小规模网络环境下异常流量识别的效率。",
    ],
}

EN_ABSTRACT = [
    "The current network security environment is increasingly complex. Traditional rule-based intrusion detection methods rely heavily on known signatures, and they often perform poorly when facing unknown variants, low-frequency probing and mixed attacks. To improve the efficiency of network threat identification, this thesis designs and implements a machine-learning-based network intrusion detection system. The system builds a complete detection workflow from multi-source traffic acquisition, feature cleaning and model training to real-time anomaly warning and visualization.",
    "The system adopts Django and MySQL to implement backend services and persistent storage, uses Pandas for traffic feature cleaning and statistical feature organization, calls scikit-learn to train and evaluate decision tree, k-nearest neighbors, logistic regression and support vector machine models, and integrates ECharts to present traffic trends, anomaly types, port heat maps and model evaluation results. Administrators are responsible for user, department, role and log management, while ordinary users can perform system monitoring, traffic acquisition, algorithm comparison and anomaly detection.",
    "The experimental results show that the platform can uniformly process static CSV samples, uploaded data, real-time snapshots and simulated traffic. The evaluation covers accuracy, precision, recall, F1-score, false alarm rate, miss rate and AUC. The system reduces manual inspection costs and improves anomaly identification and traceability, providing a practical implementation scheme for security monitoring in small and medium-sized network environments.",
]


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u3000", " ")).strip()


def cn_index(num: int) -> str:
    if num <= 10:
        return CN_NUM[num]
    if num < 20:
        return "十" + CN_NUM[num - 10]
    return str(num)


def iter_blocks(doc: Document):
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield Table(child, doc)


def paragraph_image_indexes(para: Paragraph) -> list[int]:
    indexes: list[int] = []
    image_nodes = list(para._p.xpath(".//*[local-name()='blip']"))
    image_nodes.extend(para._p.xpath(".//*[local-name()='imagedata']"))
    for node in image_nodes:
        rid = node.get(qn("r:embed")) or node.get(qn("r:link")) or node.get(qn("r:id"))
        if not rid:
            continue
        rel = para.part.related_parts.get(rid)
        if rel is None:
            continue
        match = re.search(r"image([0-9]+)\.", rel.partname.filename)
        if match:
            indexes.append(int(match.group(1)))
    return indexes


def copy_canonical_images() -> None:
    for index, rel_path in IMAGE_MAP.items():
        src = RAW_IMG_DIR / f"image{index}.png"
        if not src.exists():
            raise FileNotFoundError(f"Missing converted source image: {src}")
        dst = OUT_IMG_DIR / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def target_container(chapter, section, subsection):
    if subsection is not None:
        return subsection["content"]
    if section is not None:
        return section["content"]
    if chapter is not None:
        return chapter["content"]
    raise RuntimeError("No active chapter container")


def add_text(container: list, replacement):
    if isinstance(replacement, list):
        container.extend(replacement)
    elif replacement:
        container.append(replacement)


def is_code_like(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    prefixes = (
        "for ", "if ", "return ", "def ", "_TRAIN_FEATURES", "x_train", "x_val",
        "y_train", "scaler", "estimator", "preds", "proba", "pred_label",
        "is_anomaly", "attack_type", "vector", "alt_key", "raw_value",
        "missing_value_count", "normalized =", "dtype=", "random_state=",
        "max_depth=", "n_neighbors=", "weights=", "class_weight=", "C=",
        "kernel=", "x_arr", "y_arr", "y_true", "model_type", "average=", "zero_division",
        ")",
    )
    if stripped.startswith(prefixes):
        return True
    if stripped in {"[", "]", "{", "}", "),", ")", "],"}:
        return True
    if stripped.startswith('"'):
        return True
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", stripped):
        return True
    return False


def replace_paragraph(text: str):
    for start, replacement in PARAGRAPH_REPLACEMENTS.items():
        if text.startswith(start):
            return replacement
    return text


def table_to_item(table: Table, caption: str | None):
    rows = [[clean_text(cell.text) for cell in row.cells] for row in table.rows]
    rows = [row for row in rows if any(row)]
    if not rows:
        return None
    cap = caption or "表"
    override = TABLE_OVERRIDES.get(cap)
    if override:
        item = {
            "type": "table",
            "caption": override.get("caption", cap),
            "headers": override["headers"],
            "rows": override["rows"],
            "widths": override.get("widths"),
            "font_size": override.get("font_size", 9.5),
        }
        return item
    headers, body = rows[0], rows[1:]
    col_count = len(headers)
    if col_count == 3:
        widths = [35, 70, 45]
    elif col_count == 4:
        widths = [30, 45, 42, 33]
    elif col_count == 5:
        widths = [14, 34, 24, 18, 60]
    elif col_count == 6:
        widths = [26, 18, 18, 18, 18, 52]
    else:
        widths = [round(150 / col_count, 1)] * col_count
    return {
        "type": "table",
        "caption": cap,
        "headers": headers,
        "rows": body,
        "widths": widths,
        "font_size": 9.5 if col_count <= 5 else 9.0,
    }


def figure_width(rel_path: str) -> int:
    if rel_path.startswith("system_screenshots"):
        return 145
    if rel_path.startswith("metrics"):
        return 132
    if "sample-record" in rel_path:
        return 145
    return 125


def make_figure(index: int, caption: str):
    rel_path = IMAGE_MAP.get(index)
    if not rel_path:
        return None
    return {
        "type": "image",
        "path": rel_path,
        "caption": caption,
        "width": figure_width(rel_path),
    }


def reorder_sections(chapters: list[dict]) -> None:
    for chapter in chapters:
        if chapter["title"].endswith("系统需求分析"):
            sections = chapter["sections"]
            sections.sort(key=lambda sec: 0 if "功能需求分析" in sec["title"] else 1)


def walk_content_items(items: list, replacements: dict[str, str]) -> None:
    for idx, item in enumerate(items):
        if isinstance(item, str):
            for old, new in replacements.items():
                item = item.replace(old, new)
            items[idx] = item
        elif isinstance(item, dict):
            if isinstance(item.get("caption"), str):
                caption = item["caption"]
                for old, new in replacements.items():
                    caption = caption.replace(old, new)
                item["caption"] = caption
            if isinstance(item.get("rows"), list):
                for row in item["rows"]:
                    if isinstance(row, list):
                        for cell_idx, cell in enumerate(row):
                            if isinstance(cell, str):
                                for old, new in replacements.items():
                                    cell = cell.replace(old, new)
                                row[cell_idx] = cell


def walk_chapter(chapter: dict, replacements: dict[str, str]) -> None:
    walk_content_items(chapter.get("content", []), replacements)
    for section in chapter.get("sections", []):
        walk_content_items(section.get("content", []), replacements)
        for subsection in section.get("subsections", []):
            walk_content_items(subsection.get("content", []), replacements)


def strip_heading_number(title: str) -> str:
    title = re.sub(r"^第[一二三四五六七八九十]+章\s*", "", title)
    title = re.sub(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?\s*", "", title)
    return title.strip()


def content_of(section: dict) -> list:
    return deepcopy(section.get("content", []))


def section_content_with_subsections(section: dict) -> list:
    items = content_of(section)
    for subsection in section.get("subsections", []):
        items.extend(content_of(subsection))
    return items


def strip_visual_refs_from_text(text: str) -> str:
    text = re.sub(r"如图表?\s*[0-9]+\s*[-－.]\s*[0-9]+\s*所示", "如下所述", text)
    text = re.sub(r"如表\s*[0-9]+\s*[-－.]\s*[0-9]+\s*所示", "如下所述", text)
    text = re.sub(r"图表\s*[0-9]+\s*[-－.]\s*[0-9]+", "相关结果", text)
    text = re.sub(r"图\s*[0-9]+\s*[-－.]\s*[0-9]+", "相关图示", text)
    text = re.sub(r"表\s*[0-9]+\s*[-－.]\s*[0-9]+", "相关表格", text)
    return text


def text_items(items: list) -> list:
    return [strip_visual_refs_from_text(deepcopy(item)) for item in items if isinstance(item, str)]


def text_from_section(section: dict) -> list:
    return text_items(section_content_with_subsections(section))


def text_and_tables(items: list) -> list:
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and item.get("type") == "table":
            result.append(deepcopy(item))
    return result


def text_and_visual_limit(items: list, image_limit: int = 0, table_limit: int = 0) -> list:
    result = []
    images = tables = 0
    for item in items:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and item.get("type") == "image" and images < image_limit:
            result.append(deepcopy(item))
            images += 1
        elif isinstance(item, dict) and item.get("type") == "table" and tables < table_limit:
            result.append(deepcopy(item))
            tables += 1
    return result


def make_section(title: str, content: list | None = None, subsections: list | None = None) -> dict:
    return {"title": title, "content": content or [], "subsections": subsections or []}


def make_subsection(title: str, content: list | None = None) -> dict:
    return {"title": title, "content": content or []}


def renamed_section(section: dict, title: str) -> dict:
    new_section = deepcopy(section)
    new_section["title"] = title
    return new_section


def renamed_subsection(subsection: dict, title: str) -> dict:
    new_subsection = deepcopy(subsection)
    new_subsection["title"] = title
    return new_subsection


def paragraph(text: str) -> list[str]:
    return [text]


def formula(latex: str, number: str) -> dict:
    return {"type": "formula", "latex": latex, "number": number}


def project_figure(path: str, caption: str, width: int = 135) -> dict:
    return {"type": "image", "path": path, "caption": caption, "width": width}


def replace_chapter_one(ch1: dict) -> dict:
    new_ch1 = deepcopy(ch1)
    new_ch1["title"] = "第一章 绪论"
    sections = new_ch1.get("sections", [])
    if len(sections) >= 4:
        research = deepcopy(sections[1])
        research["subsections"] = []
        research["content"] = section_content_with_subsections(sections[1])
        work = renamed_section(sections[2], "本课题主要工作")
        organization = make_section("论文组织结构", paragraph(
            "本文按照基于机器学习的入侵检测系统设计与实现过程展开，共分为五章。第一章绪论阐述课题背景、研究意义、国内外研究现状和本文主要工作，明确论文研究目标与组织结构。第二章相关理论与技术基础介绍入侵检测系统原理、系统架构、需求分析、相关机器学习算法和模型评估指标，为后续设计提供理论依据。第三章基于机器学习的入侵检测的设计围绕数据集、预处理、特征工程、模型构建和训练过程展开，说明检测模型从数据输入到评价输出的形成过程。第四章系统设计与实现给出数据库表、Web服务架构和主要功能模块实现，结合真实界面截图说明系统落地效果。第五章总结与展望归纳系统成果，并分析后续优化方向。"
        ))
        new_ch1["sections"] = [
            renamed_section(sections[0], "背景和意义"),
            renamed_section(research, "国内外研究现状"),
            work,
            organization,
        ]
    return new_ch1


def build_pdf_reference_chapter_two(ch2: dict, ch3: dict, ch6: dict) -> dict:
    django, echarts, sklearn, mysql, pandas = ch2.get("sections", [])[:5]
    requirement = ch3.get("sections", [])[0]
    feasibility = ch3.get("sections", [])[1]
    model_eval = ch6.get("sections", [])[2]
    model_build = ch6.get("sections", [])[0]
    model_opt = ch6.get("sections", [])[1]

    return {
        "title": "第二章 相关理论与技术基础",
        "content": [],
        "sections": [
            make_section("入侵检测系统", subsections=[
                make_subsection("入侵检测原理", paragraph(
                    "入侵检测系统通过采集网络流量、主机日志或应用行为数据，分析其中是否存在违反安全策略的异常特征。本文系统以网络流记录为基本分析对象，将源地址、目的地址、协议、端口、持续时间、速率统计、TCP标志位和类别标签等字段统一组织为可计算特征，再由机器学习模型判断流量是否存在攻击风险。该方法不依赖单一规则命中，而是利用样本统计规律提升对异常模式的识别能力。"
                )),
                make_subsection("入侵监测系统分类", paragraph(
                    "按照检测依据划分，入侵检测系统通常包括基于误用检测和基于异常检测两类。误用检测适合识别已知攻击规则，响应速度快但对未知变种适应性不足；异常检测关注流量行为与正常模式之间的偏离，更适合发现新型攻击。本文系统采用监督学习方式构建异常检测能力，同时保留流量趋势、端口热力和异常明细等可视化功能，便于管理员对检测结果进行复核。"
                )),
            ]),
            make_section("入侵检测系统架构", subsections=[
                make_subsection("入侵检测系统组成", paragraph(
                    "本文系统由数据采集层、数据处理层、模型分析层、业务服务层和可视化交互层组成。数据采集层接入静态CSV样本、上传文件、实时网络快照和模拟流量；数据处理层完成字段兼容、缺失填充、数值转换和标准化；模型分析层封装决策树、K近邻、逻辑回归和支持向量机；业务服务层基于Django和MySQL提供用户、角色、日志、任务和异常记录管理；可视化交互层通过ECharts展示模型指标与流量态势。"
                )),
                make_subsection("入侵检测系统流程", paragraph(
                    "系统运行流程包括数据接入、数据清洗、特征抽取、模型训练、模型评估、异常预测、结果存储和可视分析等环节。用户在前端发起训练或检测任务后，后端服务读取样本并生成固定顺序的特征向量，模型输出预测标签与评价指标，系统再将检测任务、异常明细和统计结果写入数据库，并在仪表盘、趋势图、热力图和明细表中展示。"
                )),
            ]),
            make_section("入侵检测系统需求分析", subsections=[
                make_subsection("现有入侵检测系统的局限性", text_from_section(feasibility) + text_items(content_of(requirement))),
                make_subsection("引入机器学习算法的可行性分析", paragraph(
                    "引入机器学习算法能够增强系统对未知模式和复杂流量关系的学习能力。相比只依赖人工规则的检测方式，机器学习模型可以从历史样本中学习端口、协议、速率、包长和标志位之间的组合特征，并通过准确率、精确率、召回率、F1值、误报率、漏报率和AUC等指标持续评估检测效果。对于本课题的Django后端和Python数据处理环境而言，Pandas与scikit-learn能够直接支撑数据清洗、特征标准化、模型训练和在线预测，因此具备实现可行性。"
                )),
            ]),
            make_section("相关算法理论", subsections=[
                make_subsection("决策树算法", paragraph(
                    "决策树通过特征条件划分样本空间，形成树状判定路径。该算法训练速度较快，规则可解释性强，适合作为入侵检测系统中的快速基线模型。本文利用决策树学习流量字段与攻击标签之间的对应关系，并通过最大深度等参数控制模型复杂度，减少过拟合风险。"
                )),
                make_subsection("K近邻算法", paragraph(
                    "K近邻算法根据样本间距离寻找最相近的训练样本，并按照邻近样本类别进行投票。网络流量特征尺度差异较大，因此K近邻对标准化处理较为敏感。本文在模型训练前使用StandardScaler统一特征尺度，使持续时间、速率、端口和标志位等字段能够在同一距离度量中发挥作用。"
                )),
                make_subsection("逻辑回归算法", paragraph(
                    "逻辑回归通过线性组合与概率映射完成分类判断，具有参数少、训练稳定和结果便于解释等特点。虽然其表达能力弱于非线性模型，但在入侵检测系统中可以作为轻量化分类器，用于观察不同特征对正常与异常边界的影响。"
                )),
                make_subsection("支持向量机算法", paragraph(
                    "支持向量机通过寻找最大间隔分类边界实现样本区分，适合处理边界较复杂的小中规模数据集。本文使用核函数增强模型对非线性流量模式的表达能力，并结合类别权重平衡降低攻击样本被忽略的风险。"
                )),
                make_subsection("Pandas与Scikit-learn实现基础", text_items(content_of(pandas) + content_of(sklearn) + content_of(django) + content_of(mysql) + content_of(echarts))),
            ]),
            make_section("模型评估", subsections=[
                make_subsection("评估指标", text_and_tables(content_of(model_eval.get("subsections", [])[0]))),
                make_subsection("训练损失与误报漏报分析", text_items(content_of(model_opt.get("subsections", [])[0]) + content_of(model_opt.get("subsections", [])[1]) + content_of(model_eval.get("subsections", [])[1]) + content_of(model_eval.get("subsections", [])[2])) + paragraph(
                    "在训练过程中，损失值用于描述模型预测结果与真实标签之间的差异，损失下降通常说明模型对样本规律的拟合能力逐步增强。误报率和漏报率则从安全应用角度补充解释模型效果：误报率过高会增加管理员处置压力，漏报率过高会导致真实攻击未被发现，因此本文在准确率、精确率、召回率和F1值之外，同时保留误报率、漏报率和AUC作为综合评价依据。"
                )),
            ]),
        ],
    }


def build_pdf_reference_chapter_three(ch4: dict, ch6: dict) -> dict:
    data_sections = ch4.get("sections", [])
    model_sections = ch6.get("sections", [])
    data_collect = data_sections[0]
    preprocess = data_sections[1]
    model_build = model_sections[0]
    model_opt = model_sections[1]
    model_eval = model_sections[2]
    model_call = model_sections[3]
    visual = model_sections[4]

    return {
        "title": "第三章 基于机器学习的入侵检测的设计",
        "content": [],
        "sections": [
            make_section("数据集介绍", section_content_with_subsections(data_collect)),
            make_section("数据预处理", section_content_with_subsections(preprocess)),
            make_section("特征工程", subsections=[
                renamed_subsection(model_build.get("subsections", [])[0], "特征分析"),
                renamed_subsection(preprocess.get("subsections", [])[1], "特征映射"),
                renamed_subsection(model_build.get("subsections", [])[2], "数据划分"),
            ]),
            make_section("模型构建", subsections=[
                renamed_subsection(model_build.get("subsections", [])[1], "模型对比"),
                make_subsection("基于监督学习的多模型检测结构", text_and_visual_limit(content_of(model_opt.get("subsections", [])[2]) + content_of(model_call.get("subsections", [])[0]) + content_of(model_call.get("subsections", [])[1]), image_limit=2)),
                make_subsection("模型结果解释架构", text_items(content_of(visual.get("subsections", [])[2]) + content_of(model_call.get("subsections", [])[2]))),
            ]),
            make_section("模型训练过程", text_and_visual_limit(content_of(model_opt.get("subsections", [])[0]) + content_of(model_opt.get("subsections", [])[1]) + content_of(model_eval.get("subsections", [])[0]) + content_of(model_eval.get("subsections", [])[1]) + content_of(model_eval.get("subsections", [])[2]), image_limit=6, table_limit=3)),
        ],
    }


def build_pdf_reference_chapter_four(ch5: dict, ch6: dict, ch7: dict) -> dict:
    sys_sections = ch5.get("sections", [])
    ch6_sections = ch6.get("sections", [])
    db = sys_sections[2]
    implementation_sections = ch7.get("sections", [])
    admin = implementation_sections[0]
    user = implementation_sections[1]
    visual = ch6_sections[4]
    model_call = ch6_sections[3]
    model_eval = ch6_sections[2]

    return {
        "title": "第四章 系统设计与实现",
        "content": [],
        "sections": [
            make_section("入侵检测系统的数据表设计", section_content_with_subsections(db)),
            make_section("入侵检测系统的Web服务系统设计", content_of(sys_sections[0]) + content_of(sys_sections[1])),
            make_section("入侵检测系统的模块实现", subsections=[
                make_subsection("用户登录与权限管理模块", text_and_visual_limit(content_of(admin.get("subsections", [])[0]) + content_of(admin.get("subsections", [])[1]) + content_of(admin.get("subsections", [])[2]) + content_of(admin.get("subsections", [])[3]) + content_of(admin.get("subsections", [])[4]), image_limit=5)),
                make_subsection("数据集分析模块", text_and_visual_limit(content_of(user.get("subsections", [])[0]) + content_of(user.get("subsections", [])[1]) + content_of(user.get("subsections", [])[2]) + content_of(visual.get("subsections", [])[0]) + content_of(visual.get("subsections", [])[1]), image_limit=5)),
                make_subsection("模型测试模块", text_and_visual_limit(content_of(user.get("subsections", [])[3]), image_limit=1) + text_items(content_of(model_eval.get("subsections", [])[0]) + content_of(model_eval.get("subsections", [])[2]))),
                make_subsection("模型预览图", content_of(visual.get("subsections", [])[2])),
                make_subsection("模型调优", text_items(content_of(ch6_sections[1].get("subsections", [])[0]) + content_of(ch6_sections[1].get("subsections", [])[1]))),
            ]),
        ],
    }


def build_pdf_reference_chapter_five(ch8: dict) -> dict:
    new_ch5 = deepcopy(ch8)
    new_ch5["title"] = "第五章 总结与展望"
    if len(new_ch5.get("sections", [])) >= 2:
        new_ch5["sections"][0]["title"] = "系统成果总结"
        new_ch5["sections"][1]["title"] = "未来工作展望"
    return new_ch5


def apply_project_specific_polish(chapters: list[dict]) -> None:
    """Align formulas, figures and feature counts with the actual hertz_django traffic_app."""
    text_replacements = {
        "21维": "19维",
        "21 维": "19 维",
        "抽取21维核心特征": "抽取19维核心特征",
        "构建21维特征向量": "构建19维特征向量",
        "上述21维特征": "上述19维特征",
        "同一套21维标准化特征": "同一套19维标准化特征",
        "图6-1": "图3-5",
        "图6-2": "图3-8",
        "图6-6": "图3-13",
        "图6-10": "图3-9",
        "图6-11": "图3-10",
        "图5-1": "图4-6",
        "图表3-7": "表3-7",
    }
    for chapter in chapters:
        walk_chapter(chapter, text_replacements)

    # Replace the rough source flowcharts with thesis-style generated figures based on
    # the real Django + scikit-learn implementation.
    image_replacements = {
        "diagrams/fig6-1-model-build-flow.png": (
            "generated/mlids-training-evaluation-flow.png",
            "模型训练与评价流程图",
            145,
        ),
        "diagrams/fig6-2-multi-model-classification.png": (
            "generated/mlids-multimodel-architecture.png",
            "基于监督学习的多模型入侵检测结构",
            145,
        ),
        "diagrams/fig6-6-metrics-structure.png": (
            "generated/mlids-metrics-structure.png",
            "入侵检测模型评价指标结构",
            122,
        ),
        "diagrams/fig6-10-model-call-flow.png": (
            "generated/mlids-model-invocation-flow.png",
            "模型调用与结果落库流程",
            145,
        ),
        "diagrams/fig6-11-anomaly-decision-flow.png": (
            "generated/mlids-anomaly-decision-flow.png",
            "异常流量判定与落库流程",
            130,
        ),
        "diagrams/fig5-1-system-architecture.png": (
            "generated/mlids-django-architecture.png",
            "Django入侵检测系统总体架构",
            145,
        ),
    }
    for chapter in chapters:
        for content_list in iter_content_lists(chapter):
            for item in content_list:
                if isinstance(item, dict) and item.get("type") == "image" and item.get("path") in image_replacements:
                    new_path, new_caption, width = image_replacements[item["path"]]
                    item["path"] = new_path
                    item["caption"] = new_caption
                    item["width"] = width

    def fix_table(item: dict) -> None:
        caption = item.get("caption", "")
        if "模型输入特征分组表" in caption:
            item["rows"] = [
                ["时间特征", "Flow Duration、Active Mean、Idle Mean", "3", "描述连接持续、活跃与空闲状态"],
                ["速率特征", "Flow Bytes/s、Flow Packets/s", "2", "反映单位时间内流量强度"],
                ["包数量特征", "Total Fwd Packet、Total Bwd packets", "2", "表示双向交互规模"],
                ["包长度特征", "Total Length of Fwd Packet、Total Length of Bwd Packet、Packet Length Mean、Max、Std", "5", "描述包大小分布差异"],
                ["标志位特征", "FIN、SYN、RST、PSH、ACK Flag Count", "5", "刻画TCP连接行为"],
                ["比例特征", "Down/Up Ratio", "1", "衡量上下行流量关系"],
                ["协议特征", "Protocol", "1", "标识TCP、UDP等协议类型，源/目的端口不进入当前训练特征"],
            ]
        elif "特征尺度处理对比表" in caption:
            item["rows"] = [
                ["Flow Duration", "10^6～10^8", "约0", "约1", "降低持续时间主导效应"],
                ["Flow Bytes/s", "10^2～10^8", "约0", "约1", "缓解速率极端值影响"],
                ["Flow Packets/s", "10^0～10^5", "约0", "约1", "提升距离计算稳定性"],
                ["SYN Flag Count", "0～数十", "约0", "约1", "保留连接异常语义"],
                ["Protocol", "6、17等离散协议号", "约0", "约1", "统一协议字段尺度"],
            ]

    for chapter in chapters:
        for content_list in iter_content_lists(chapter):
            for item in content_list:
                if isinstance(item, dict) and item.get("type") == "table":
                    fix_table(item)

    if len(chapters) < 4:
        return

    ch2 = chapters[1]
    algorithm = ch2["sections"][3]
    algorithm["subsections"] = [
        make_subsection("决策树算法", [
            "决策树通过特征条件划分样本空间，形成树状判定路径。该算法训练速度较快，规则可解释性强，适合作为入侵检测系统中的快速基线模型。本文利用决策树学习流量字段与攻击标签之间的对应关系，并通过最大深度等参数控制模型复杂度，减少过拟合风险。",
            "设样本集合为D，类别数为K，第k类样本所占比例为pk，则信息熵定义如式（2.1）所示。",
            formula(r"H(D)=-\sum_{k=1}^{K}p_k\log_2 p_k", "（2.1）"),
            "式中，H(D)表示样本集合D的不确定性，pk表示第k类样本在集合D中的比例。对特征a进行划分时，信息增益计算如式（2.2）所示。",
            formula(r"Gain(D,a)=H(D)-\sum_{v=1}^{V}\frac{|D^v|}{|D|}H(D^v)", "（2.2）"),
            "式中，Dv表示特征a在第v个取值下形成的子集。决策树优先选择信息增益较大的特征进行划分，从而使流量类别在子节点中更加纯净。",
        ]),
        make_subsection("K近邻算法", [
            "K近邻算法根据样本间距离寻找最相近的训练样本，并按照邻近样本类别进行投票。网络流量特征尺度差异较大，因此K近邻对标准化处理较为敏感。本文在模型训练前使用StandardScaler统一特征尺度，使持续时间、速率、包数量和标志位等字段能够在同一距离度量中发挥作用。",
            "设xi和xj为两个n维流量特征向量，欧氏距离计算如式（2.3）所示。",
            formula(r"d(x_i,x_j)=\sqrt{\sum_{m=1}^{n}(x_{im}-x_{jm})^2}", "（2.3）"),
            "式中，xim和xjm分别表示两个样本在第m维特征上的取值。系统采用距离加权策略，使距离更近的样本在投票中具有更高权重。",
        ]),
        make_subsection("逻辑回归算法", [
            "逻辑回归通过线性组合与概率映射完成分类判断，具有参数少、训练稳定和结果便于解释等特点。虽然其表达能力弱于非线性模型，但在入侵检测系统中可以作为轻量化分类器，用于观察不同特征对正常与异常边界的影响。",
            "二分类场景下，逻辑回归的类别概率映射如式（2.4）所示。",
            formula(r"P(y=1|x)=\frac{1}{1+e^{-(w^T x+b)}}", "（2.4）"),
            "式中，w表示特征权重向量，b表示偏置项。多分类检测时，scikit-learn会将该思想扩展到多个攻击类别的概率估计。",
        ]),
        make_subsection("支持向量机算法", [
            "支持向量机通过寻找最大间隔分类边界实现样本区分，适合处理边界较复杂的小中规模数据集。本文使用rbf核函数增强模型对非线性流量模式的表达能力，并结合balanced类别权重降低攻击样本被忽略的风险。",
            "线性可分情况下，支持向量机的分类超平面可表示为式（2.5）。",
            formula(r"f(x)=w^Tx+b", "（2.5）"),
            "为允许少量样本出现在间隔边界内，软间隔支持向量机的优化目标可表示为式（2.6）。",
            formula(r"\min_{w,b,\xi}\frac{1}{2}\|w\|^2+C\sum_{i=1}^{N}\xi_i", "（2.6）"),
            "式中，C为惩罚系数，xi为松弛变量。该目标在间隔最大化和训练误差控制之间取得平衡。",
        ]),
        renamed_subsection(algorithm.get("subsections", [])[4], "Pandas与Scikit-learn实现基础") if len(algorithm.get("subsections", [])) > 4 else make_subsection("Pandas与Scikit-learn实现基础"),
    ]

    evaluation = ch2["sections"][4]
    evaluation["subsections"] = [
        make_subsection("评估指标", [
            "本研究采用准确率、精确率、召回率、F1值、误报率、漏报率和AUC作为模型评估指标。准确率反映整体分类正确比例，精确率反映被判定为攻击样本中的真实攻击比例，召回率反映真实攻击样本被识别出来的比例，F1值综合平衡精确率与召回率。误报率用于衡量正常流量被错误判定为异常的比例，漏报率用于衡量攻击流量被遗漏的比例，AUC用于评价模型在不同阈值下的区分能力。",
            project_figure("generated/mlids-metrics-structure.png", "入侵检测模型评价指标结构", 122),
            "设TP表示攻击流量被正确识别为攻击，TN表示正常流量被正确识别为正常，FP表示正常流量被误判为攻击，FN表示攻击流量被误判为正常，各项指标计算如下。",
            formula(r"Acc=\frac{TP+TN}{N}", "（2.7）"),
            formula(r"P=\frac{TP}{TP+FP}", "（2.8）"),
            formula(r"R=\frac{TP}{TP+FN}", "（2.9）"),
            formula(r"F_1=\frac{2PR}{P+R}", "（2.10）"),
            formula(r"\mathrm{FPR}=\frac{FP}{FP+TN}", "（2.11）"),
            formula(r"\mathrm{FNR}=\frac{FN}{FN+TP}", "（2.12）"),
            formula(r"AUC=\int_{0}^{1}TPR\,dFPR", "（2.13）"),
            "式（2.7）至式（2.10）中，Acc表示Accuracy，P表示Precision，R表示Recall，N=TP+TN+FP+FN。由于入侵检测数据存在类别不均衡问题，系统评价过程采用加权平均方式，使各类别指标按照样本规模参与综合评价。",
        ]),
        make_subsection("训练损失与误报漏报分析", [
            "在训练曲线展示中，系统通过不同训练样本比例重新训练模型，并分别计算训练准确率、验证准确率和损失值。该损失并不是深度学习中的反向传播目标，而是为了观察样本规模变化带来的泛化趋势，采用验证准确率的互补量进行近似表示，如式（2.14）所示。",
            formula(r"L_t=1-\mathrm{Acc}_{val,t}", "（2.14）"),
            "式中，Lt表示第t个训练比例下的近似损失，Accval,t表示对应验证准确率。误报率和漏报率则从安全应用角度补充解释模型效果：误报率过高会增加管理员处置压力，漏报率过高会导致真实攻击未被发现，因此本文在准确率、精确率、召回率和F1值之外，同时保留误报率、漏报率和AUC作为综合评价依据。",
        ]),
    ]

    ch3 = chapters[2]
    preprocess = ch3["sections"][1]
    preprocess["content"].extend([
        "对数值特征进行标准化时，系统先在训练集上计算均值与标准差，再将相同参数应用于验证集和预测样本。该过程可表示为式（3.1）。",
        formula(r"x'=\frac{x-\mu}{\sigma}", "（3.1）"),
        "式中，x为原始特征值，mu为训练集均值，sigma为训练集标准差，x'为标准化后的特征值。该处理能够避免验证集信息泄漏，并保证在线检测阶段与训练阶段使用一致的特征尺度。",
    ])

    training = ch3["sections"][4]
    training["content"].extend([
        "模型预测阶段将分类器输出的各类别概率或决策分数转化为最终标签，预测规则可表示为式（3.2）。",
        formula(r"\hat{y}=\arg\max_{c\in C}P(y=c|x)", "（3.2）"),
        "式中，C表示类别集合，P(y=c|x)表示样本x被判定为类别c的概率或归一化得分。对于多类别评价，系统采用weighted平均方式汇总各类别指标，如式（3.3）所示。",
        formula(r"M_{\mathrm{weighted}}=\sum_{c=1}^{C}\frac{n_c}{N}M_c", "（3.3）"),
        "式中，Mc表示第c类上的某项指标，nc为该类样本数，N为验证集样本总数。该方式能够降低类别不均衡对综合指标的干扰。",
    ])


def merge_to_pdf_template_chapter_count(chapters: list[dict]) -> list[dict]:
    """Match the five-chapter structure of the user's PDF reference paper."""
    if len(chapters) != 8:
        return chapters
    ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8 = chapters
    return [
        replace_chapter_one(ch1),
        build_pdf_reference_chapter_two(ch2, ch3, ch6),
        build_pdf_reference_chapter_three(ch4, ch6),
        build_pdf_reference_chapter_four(ch5, ch6, ch7),
        build_pdf_reference_chapter_five(ch8),
    ]


def iter_content_lists(chapter: dict):
    yield chapter.get("content", [])
    for section in chapter.get("sections", []):
        yield section.get("content", [])
        for subsection in section.get("subsections", []):
            yield subsection.get("content", [])


def collect_visual_mapping(chapters: list[dict], prefix: str) -> dict[tuple[str, str, str], str]:
    mapping: dict[tuple[str, str, str], str] = {}
    item_type = "image" if prefix == "图" else "table"
    pattern = re.compile(rf"^{prefix}\s*([0-9]+)\s*[-－.]\s*([0-9]+)\s*(.*)$")
    for ch_idx, chapter in enumerate(chapters, 1):
        counter = 0
        for content_list in iter_content_lists(chapter):
            for item in content_list:
                if not isinstance(item, dict) or item.get("type") != item_type:
                    continue
                caption = item.get("caption", "")
                match = pattern.match(caption)
                tail = caption
                if match:
                    old_key = (prefix, match.group(1), match.group(2))
                    counter += 1
                    new_id = f"{prefix}{ch_idx}-{counter}"
                    mapping[old_key] = new_id
                    tail = match.group(3).strip()
                    item["caption"] = f"{new_id} {tail}".strip()
                else:
                    counter += 1
                    item["caption"] = f"{prefix}{ch_idx}-{counter} {caption}".strip()
    return mapping


def replace_visual_refs(text: str, mapping: dict[tuple[str, str, str], str]) -> str:
    text = re.sub(r"图表\s*([0-9]+\s*[-－.]\s*[0-9]+)", r"表\1", text)

    def repl(match: re.Match) -> str:
        key = (match.group(1), match.group(2), match.group(3))
        return mapping.get(key, match.group(0))

    return re.sub(r"([图表])\s*([0-9]+)\s*[-－.]\s*([0-9]+)", repl, text)


def apply_visual_ref_mapping(chapters: list[dict], mapping: dict[tuple[str, str, str], str]) -> None:
    for chapter in chapters:
        for content_list in iter_content_lists(chapter):
            for idx, item in enumerate(content_list):
                if isinstance(item, str):
                    content_list[idx] = replace_visual_refs(item, mapping)
                elif isinstance(item, dict):
                    for key in ("headers", "rows"):
                        if isinstance(item.get(key), list):
                            for row_idx, row in enumerate(item[key]):
                                if isinstance(row, str):
                                    item[key][row_idx] = replace_visual_refs(row, mapping)
                                elif isinstance(row, list):
                                    for cell_idx, cell in enumerate(row):
                                        if isinstance(cell, str):
                                            row[cell_idx] = replace_visual_refs(cell, mapping)


def renumber_visuals(chapters: list[dict]) -> None:
    mapping = {}
    mapping.update(collect_visual_mapping(chapters, "图"))
    mapping.update(collect_visual_mapping(chapters, "表"))
    apply_visual_ref_mapping(chapters, mapping)


def fix_final_project_refs(chapters: list[dict]) -> None:
    final_refs = {
        "图3-50": "图3-9",
        "图3-51": "图3-10",
    }
    for chapter in chapters:
        walk_chapter(chapter, final_refs)


def renumber_chapters(chapters: list[dict]) -> None:
    for ch_idx, chapter in enumerate(chapters, 1):
        subject = re.sub(r"^第[一二三四五六七八九十]+章\s*", "", chapter["title"])
        chapter["title"] = f"第{cn_index(ch_idx)}章 {subject}"
        for sec_idx, section in enumerate(chapter.get("sections", []), 1):
            sec_subject = re.sub(r"^[0-9]+\.[0-9]+\s*", "", section["title"])
            section["title"] = f"{ch_idx}.{sec_idx} {sec_subject}"
            for sub_idx, subsection in enumerate(section.get("subsections", []), 1):
                sub_subject = re.sub(r"^[0-9]+\.[0-9]+\.[0-9]+\s*", "", subsection["title"])
                subsection["title"] = f"{ch_idx}.{sec_idx}.{sub_idx} {sub_subject}"


def extract_main_content(doc: Document) -> list[dict]:
    chapters: list[dict] = []
    chapter = section = subsection = None
    started = False
    stop = False
    ch_no = sec_no = sub_no = 0
    pending_images: list[int] = []
    pending_table_caption: str | None = None
    merge_heading3 = False

    for block in iter_blocks(doc):
        if stop:
            break
        if isinstance(block, Table):
            if started:
                item = table_to_item(block, pending_table_caption)
                pending_table_caption = None
                if item:
                    target_container(chapter, section, subsection).append(item)
            continue

        text = clean_text(block.text)
        style = block.style.name if block.style is not None else ""

        if style == "Heading 1" and text == "绪论":
            started = True
        if not started:
            continue
        if text == "参考文献" or style == "引用文献著录":
            stop = True
            continue
        if not text and not paragraph_image_indexes(block):
            continue

        image_indexes = paragraph_image_indexes(block)
        if image_indexes:
            pending_images.extend(image_indexes)
            continue

        if text.startswith("图") and pending_images:
            index = pending_images.pop(0)
            item = make_figure(index, text)
            if item:
                target_container(chapter, section, subsection).append(item)
            continue
        if text.startswith("表") and re.match(r"^表[0-9]+-[0-9]+", text):
            pending_table_caption = text
            continue

        if style == "Heading 1":
            ch_no += 1
            sec_no = sub_no = 0
            chapter = {"title": f"第{cn_index(ch_no)}章 {text}", "content": [], "sections": []}
            chapters.append(chapter)
            section = subsection = None
            merge_heading3 = False
            continue
        if style == "Heading 2":
            sec_no += 1
            sub_no = 0
            section = {"title": f"{ch_no}.{sec_no} {text}", "content": [], "subsections": []}
            chapter["sections"].append(section)
            subsection = None
            merge_heading3 = False
            continue
        if style == "Heading 3":
            if text == "架构闭环":
                merge_heading3 = True
                continue
            sub_no += 1
            subsection = {"title": f"{ch_no}.{sec_no}.{sub_no} {text}", "content": []}
            section["subsections"].append(subsection)
            merge_heading3 = False
            continue
        if style == "Heading 4":
            container = target_container(chapter, section, subsection)
            if text.endswith("。"):
                add_text(container, text)
            else:
                add_text(container, f"{text}。")
            continue

        if is_code_like(text):
            continue

        replacement = replace_paragraph(text)
        if replacement == text and text.endswith("核心代码实现如下所示："):
            replacement = PARAGRAPH_REPLACEMENTS["核心代码实现如下所示"]
        if merge_heading3 and text.startswith("模型构建、评估、调用和可视化最终构成数据闭环"):
            replacement = [
                "模型构建、评估、调用和可视化最终构成数据闭环。采集层负责接入静态、上传、模拟和实时流量；特征层负责21维核心特征构造；模型层负责多模型训练、评估和预测；可视层负责趋势、协议、端口、告警和异常明细展示。该内容与解释分析共同构成模型结果可理解化环节，系统分析闭环如图6-15所示。"
            ]
        add_text(target_container(chapter, section, subsection), replacement)

    reorder_sections(chapters)
    chapters = merge_to_pdf_template_chapter_count(chapters)
    apply_project_specific_polish(chapters)
    renumber_chapters(chapters)
    renumber_visuals(chapters)
    fix_final_project_refs(chapters)
    return chapters


def extract_references(doc: Document) -> list[str]:
    refs: list[str] = []
    in_refs = False
    for para in doc.paragraphs:
        text = clean_text(para.text)
        if text == "参考文献":
            in_refs = True
            continue
        if in_refs and text in {"致谢", "致 谢", "附录A"}:
            break
        if in_refs and para.style.name == "引用文献著录" and text:
            refs.append(re.sub(r"^\[[0-9]+\]\s*", "", text))
    return refs


def write_json(name: str, data) -> None:
    path = HERE / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_project_readme() -> None:
    readme = """# 基于机器学习的网络入侵检测系统的设计与实现

- 模板来源：`/Users/a136/vs/45425/thesis_project/papers/spwm-dual-frequency`
- 源批注文档：`/Users/a136/vs/45425/thesis_project/templates/ml_ids_source/source.docx`
- 构建命令：`cd /Users/a136/vs/45425/thesis_project && /Users/a136/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 papers/ml_ids/build.py`
- 输出文件：`/Users/a136/vs/45425/thesis_project/papers/ml_ids/基于机器学习的网络入侵检测系统的设计与实现_论文初稿.docx`
"""
    (HERE / "PROJECT_README.md").write_text(readme, encoding="utf-8")


def main() -> int:
    if not SRC_DOCX.exists():
        raise FileNotFoundError(SRC_DOCX)
    copy_canonical_images()
    doc = Document(str(SRC_DOCX))
    chapters = extract_main_content(doc)
    refs = extract_references(doc)

    meta = {
        "title_zh": "基于机器学习的网络入侵检测系统的设计与实现",
        "title_en": "Design and Implementation of a Network Intrusion Detection System Based on Machine Learning",
        "name": "",
        "student_id": "",
        "class_name": "",
        "advisor": "",
        "finish_date": "2026年5月",
        "abstract_zh_list": [
            "当前网络安全环境日益复杂，传统基于规则库的入侵检测方式主要依赖已知攻击特征，对未知变种、低频探测和混合攻击的识别能力有限，容易出现误报率偏高、规则维护滞后和适应性不足等问题。为提升网络威胁识别效率，本文设计并实现一套基于机器学习的网络入侵检测系统，通过多源流量采集、特征清洗、分类模型训练和可视化监控，形成从数据接入到异常告警的完整检测流程。",
            "系统技术架构采用Django和MySQL搭建后端业务与持久化数据服务，利用Pandas完成流量字段清洗与统计特征组织，调用scikit-learn实现决策树、K近邻、逻辑回归和支持向量机等模型训练与预测，并借助ECharts展示流量趋势、异常类型、端口热力和模型评价结果。系统面向管理员和普通用户两类角色：管理员负责用户、部门、角色和日志等平台基础管理，普通用户负责系统监控、流量采集、算法实验对比和异常检测。",
            "实验与系统运行结果表明，平台能够对CSV样本、上传数据、实时快照和模拟流量进行统一处理，模型评价指标覆盖准确率、精确率、召回率、F1值、误报率、漏报率和AUC等多个维度。系统能够降低人工筛查成本，增强异常流量识别与追溯能力，为中小规模网络环境下的安全监测提供可落地的实现方案。",
        ],
        "keywords_zh": "入侵检测；机器学习；流量分析；Scikit-learn；网络安全",
        "abstract_en_list": EN_ABSTRACT,
        "keywords_en": "Intrusion Detection; Machine Learning; Traffic Analysis; Scikit-learn; Network Security",
    }
    write_json("meta.json", meta)
    for stale in HERE.glob("ch*.json"):
        stale.unlink()
    for idx, chapter in enumerate(chapters, 1):
        write_json(f"ch{idx}.json", chapter)
    write_json("references.json", refs)
    write_json("acknowledgement.json", {
        "text": (
            "春华秋实，岁序更新。转眼间大学生活已步入尾声，随着论文定稿工作的圆满落幕，这段求学旅程即将画上句点。在此之际，内心充满感激之情。本论文从选题构思到最终定稿，每一个环节都浸透着指导老师的心血。老师治学严谨，对待学术研究始终保持一丝不苟的态度，这种求真务实的工作作风令我深感敬佩。"
            "\n\n回首本次毕设的创作过程，初期的迷茫逐渐在查阅资料和系统调试中逐渐消散。面对复杂的流量特征和模型评价指标，通过反复推敲与实验验证，许多一度难以理清的逻辑问题最终得到了较好解决。感谢学院提供的学习环境，也感谢各位老师、同学和家人在学习与生活中的帮助。未来我将继续保持求索之心，在专业领域持续深耕。"
        )
    })
    write_json("appendix.json", {
        "text": "本文系统结构、模型指标、运行截图和关键结果已在正文中集中展示，附录部分不再重复列出。"
    })
    write_project_readme()
    print(f"Extracted {len(chapters)} chapters, {len(refs)} references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
