# 第3章需要的图（2张）

要求：白底黑线，学术论文风格，宋体/黑体中文字，无彩色装饰。宽高比例控制在4:3或3:4左右，不要做成超宽横条。放到Word里A4页面宽度（约15cm）时文字仍可辨认。

---

## 图1：数据仓库ODS-DWD-ADS分层架构图

文件名：`warehouse_layers.png`

### 布局
采用从上到下的分层布局，共5行：

**第1行：数据源**
4个圆角矩形横排：
- Kaggle 2020 CSV（319795条，18字段）
- Kaggle 2022 CSV（246022条，40字段）
- UCI Cleveland（303条，14字段）
- UCI Cost Data（2字段）

↓ 向下箭头

**第2行：ODS层（原始数据层）**
一个大矩形框，标题"ODS层 — 原始数据存储"，内部4个小圆柱体（数据库图标）横排：
- ods_heart_2020_raw（18列）
- ods_heart_2022_raw（40列）
- ods_uci_cleveland_raw（14列）
- ods_uci_cost_raw（2列）
框右侧注释：OpenCSVSerde / STRING类型 / 原样载入

↓ 向下箭头，箭头旁标注"INSERT OVERWRITE / 类型转换 / Yes→1 / ?→NULL"

**第3行：DWD层（清洗明细层）**
一个大矩形框，标题"DWD层 — 清洗标准化"，内部5个小圆柱体横排：
- dwd_heart_2020_clean（21列）
- dwd_heart_2022_clean（45列）
- dwd_uci_cleveland_clean（17列）
- dwd_uci_cost_clean（7列）
- dwd_heart_feature_sample（28列，统一表）← 这个用粗边框标注为"统一特征表"
框右侧注释：DECIMAL / INT类型 / risk_label派生 / 缺失值处理

↓ 向下箭头，箭头旁标注"GROUP BY多维聚合"

**第4行：ADS层（应用聚合层）**
一个大矩形框，标题"ADS层 — 应用聚合"，内部9个小圆柱体分两排：
第一排5个：ads_heart_overview / ads_heart_by_age / ads_heart_by_sex / ads_heart_by_bmi / ads_heart_lifestyle
第二排4个：ads_heart_comorbidity / ads_uci_clinical_risk / ads_uci_cost_analysis / ads_model_metrics
框右侧注释：年龄/性别/BMI/习惯/共病/临床 六维统计

↓ 向下箭头，箭头旁标注"Python同步脚本（PyHive → PyMySQL）"

**第5行：应用端**
3个圆角矩形横排：
- MySQL ADS表
- Django REST API
- Vue3 + ECharts 前端
用箭头从左到右串联

### 样式
- 每一层用一个大矩形框包住，左侧写层名
- 层与层之间用粗箭头连接
- 圆柱体表示数据表
- 整体高度大于宽度（纵向排列）
- 推荐尺寸：宽1200px，高1600px

---

## 图2：ETL数据处理流程图

文件名：`heart-disease-etl-flow.png`

### 布局
采用标准流程图（从上到下），用圆角矩形表示步骤，菱形表示判断，箭头连接：

```
[开始]
    ↓
[CSV原始文件上传至HDFS]
    ↓
[Hive建ODS外部表（4张）]
  注：OpenCSVSerde，全STRING类型
    ↓
[INSERT OVERWRITE写入DWD层]
  注：STRING→DECIMAL/INT
  注：Yes/No→1/0
  注：?→NULL
  注：派生risk_label、sex_code
    ↓
[UNION ALL合并为统一特征表]
  注：dwd_heart_feature_sample（28列）
  注：缺失字段NULL填充
    ↓
[GROUP BY多维聚合写入ADS层]
  注：9张聚合表
  注：年龄/性别/BMI/习惯/共病/临床
    ↓
[Python脚本同步至MySQL]
  注：PyHive读 → PyMySQL写
  注：全量清空+批量插入
    ↓
[Django API查询MySQL ADS表]
    ↓
[Vue3前端展示分析图表]
    ↓
[结束]
```

### 样式
- 标准流程图符号（圆角起止、矩形步骤）
- 每个步骤框右侧或下方可附小字注释
- 纵向排列，宽度适中
- 推荐尺寸：宽800px，高1400px
