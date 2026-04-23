# 需要画的图（共8张）

画完后放到 `../images/` 目录下，文件名必须和下面一致。

---

## 第一组（5张）

### 1. system_architecture.png — 系统总体架构图

参考：`ref_system_arch.png`（分层矩形风格）+ `ref_dw_architecture.png`（数仓分层风格）

标题：心脏病健康数据分析系统架构图

从上到下五层：

- 客户端：浏览器 / Web客户端
- 展示层：Vue3 + Naive UI + ECharts（可视化大屏、分页分析界面、风险预测页面）
- 服务层：Django REST Framework（用户认证、数据查询API、在线预测API）
- 数据层：MySQL（ADS聚合表、用户表、预测记录表）| scikit-learn模型文件（joblib）
- 大数据层：Hadoop HDFS + Hive数据仓库（ODS → DWD → ADS）| MapReduce ETL
- 运行环境：Python 3.10 | Django 4.2 | Vue3 + Vite | MySQL 8.0 | Hadoop 3.x | Docker Compose

---

### 2. warehouse_layers.png — 数据仓库三层架构图

参考：`ref_etl_flow.png`（从左到右的数据流向风格）

标题：Hive数据仓库ODS-DWD-ADS分层架构

从左到右的数据流：

- 数据源（左）：3个图标
  - Kaggle 2020 CSV（319795条，18字段）
  - Kaggle 2022 CSV（246022条，40字段）
  - UCI Cleveland（303条，14字段）
- ODS层：4张外部表（STRING类型，OpenCSVSerde，原样存储）
  - ods_heart_2020_raw
  - ods_heart_2022_raw
  - ods_uci_cleveland_raw
  - ods_uci_cost_raw
- DWD层：5张清洗表（类型转换、缺失值处理、字段标准化）
  - dwd_heart_2020_clean（21列）
  - dwd_heart_2022_clean（45列）
  - dwd_uci_cleveland_clean（17列）
  - dwd_uci_cost_clean（7列）
  - dwd_heart_feature_sample（28列，统一表）
- ADS层：9张聚合表（GROUP BY多维统计）
  - ads_heart_overview
  - ads_heart_by_age
  - ads_heart_by_sex
  - ads_heart_by_bmi
  - ads_heart_lifestyle
  - ads_heart_comorbidity
  - ads_uci_clinical_risk
  - ads_uci_cost_analysis
  - ads_model_metrics
- 输出（右）：MySQL离线同步（Python脚本）→ Django API

---

### 3. etl_flow.png — ETL数据处理流程图

参考：`ref_etl_flow.png`

标题：数据处理ETL流程

从左到右：

CSV原始文件 → 上传HDFS → Hive ODS建外部表（原样载入） → HiveQL INSERT OVERWRITE → DWD清洗层（类型转换、Yes/No→1/0、?→NULL、字段派生risk_label） → HiveQL GROUP BY聚合 → ADS应用层（9张维度统计表） → Python sync脚本 → MySQL ADS表 → Django REST API查询

---

### 4. model_pipeline.png — 机器学习模型训练流程图

参考：`ref_model_pipeline.png`（并行训练多模型风格）

标题：心脏病预测模型训练流程

从左到右：

- 原始数据：dwd_heart_feature_sample
- 预处理：
  - 数值特征（BMI、PhysicalHealth、MentalHealth、SleepTime）→ SimpleImputer(中位数) → StandardScaler
  - 分类特征（13个字段）→ SimpleImputer(众数) → OneHotEncoder
- 数据集划分：80%训练集 / 20%验证集（分层抽样，seed=42）
- 并行训练4个模型（4个分支）：
  - 逻辑回归
  - SGD线性分类器
  - 随机森林（250棵树）
  - Extra Trees（300棵树）
- 模型评估：Accuracy、Precision、Recall、F1、AUC
- 最优模型选择（奖杯图标）：按AUC排序选最高
- 输出：保存model.joblib + metrics.json + feature_importance.json

---

### 5. function_structure.png — 系统功能模块图

参考：`ref_func_structure.png`（树形层级结构）

标题：心脏病健康数据分析系统

第一级4个模块，第二级子功能：

- 数据分析模块
  - 年龄分析
  - 生活习惯分析
  - 临床指标分析
  - 相关性分析
  - 数据集对比
- 机器学习模块
  - 模型训练
  - 模型对比
  - 特征重要性
  - 风险预测
- 数据管理模块
  - 数据总览
  - 数据清洗
  - 仓库分层
- 系统管理模块
  - 系统监控
  - 日志管理
  - 用户管理

---

## 第二组（3张）

### 6. hadoop_architecture.png — Hadoop架构示意图

参考：`ref_layered_arch.png`（分层矩形风格）

标题：Hadoop分布式计算框架架构

从上到下四层：

- 应用层：Hive（数据仓库） | MapReduce（批处理计算）
- 资源调度层：YARN（ResourceManager + NodeManager）
- 存储层：HDFS（NameNode + DataNode，128MB数据块，3副本）
- 基础设施层：集群节点（多台服务器）

---

### 7. hive_architecture.png — Hive工作原理图

参考：`ref_dw_architecture.png`（带数据流箭头的架构图）

标题：Hive数据仓库工作原理

画出以下组件和数据流向：

- 用户接口（左上）：CLI / JDBC / Web UI → 输入HiveQL
- Driver驱动器（中间，最大的框）：
  - 解析器（SQL Parser）→ 编译器（Compiler）→ 优化器（Optimizer）→ 执行器（Executor）
- MetaStore元数据（下方）：MySQL存储表结构、分区信息、HDFS路径映射
- 执行引擎（右侧）：MapReduce / Tez → YARN资源调度
- 存储（底部）：HDFS（读写数据文件）
- 数据流箭头：用户SQL → Driver解析优化 → 生成MapReduce任务 → YARN调度执行 → HDFS读写 → 结果返回用户

---

### 8. prediction_flow.png — 在线预测流程图

参考：`ref_flow_chart.png`（标准流程图：圆角起止 + 矩形步骤 + 菱形判断）

标题：在线心脏病风险预测流程

从上到下：

- 开始
- 用户填写健康指标表单（16字段：BMI、年龄段、性别、吸烟等）
- 前端POST请求发送至 /api/predict
- Django接口接收数据
- 菱形判断：模型是否已加载？
  - 否 → 加载model.joblib和Pipeline → 回到主流程
  - 是 → 继续
- 缺失字段补充默认值（数值取中位数，分类取众数）
- OneHotEncoder + StandardScaler特征预处理
- 逻辑回归模型推理，输出概率值P
- 菱形判断：风险等级划分
  - P ≥ 0.67 → 高风险（红色）
  - 0.33 ≤ P < 0.67 → 中风险（黄色）
  - P < 0.33 → 低风险（绿色）
- 保存预测记录到数据库
- 返回结果（概率、风险等级、影响因素Top3）
- 前端渲染结果卡片
- 结束
