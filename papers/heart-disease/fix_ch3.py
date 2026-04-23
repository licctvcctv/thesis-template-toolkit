"""AIGC break: ch3.json — 数据来源与数据仓库"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "ch3.json")
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

replacements = {
    # === 3.1 数据集介绍 (69.82, 57.03) ===
    "Kaggle 2020数据集来源于美国疾病控制与预防中心（CDC）的行为风险因素监测系统（BRFSS），覆盖2020年约40万人的电话调查结果，经过清洗后剩余319795条记录。":
        "Kaggle 2020这份数据集，原始来源是美国CDC的行为风险因素监测系统（BRFSS）。2020年CDC通过电话调查了大约40万人，清洗完剩下319795条。",

    "18个字段中，HeartDisease为二值目标变量（Yes/No），其余17个字段包括BMI、吸烟、饮酒、中风、身体健康天数、精神健康天数、行走困难、性别、年龄段、种族、糖尿病、运动习惯、整体健康评价、睡眠时长、哮喘、肾病和皮肤癌。":
        "一共18个字段。HeartDisease是目标变量，只有Yes和No两个值。剩下17个字段覆盖了BMI、吸烟、饮酒、中风、身体健康天数、精神健康天数、行走困难、性别、年龄段、种族、糖尿病、运动习惯、整体健康评价、睡眠时长、哮喘、肾病、皮肤癌。",

    "Kaggle 2020数据集的心脏病分布如图3-1所示，阳性样本占比约8.6%，属于典型的类别不均衡。":
        "心脏病阳性样本只占8.6%——非常典型的类别不均衡，图3-1画出了这个分布。",

    "Kaggle 2022数据集是2020版的扩展，字段从18个增加到40个，新增了疫苗接种记录、COVID感染状态、口腔健康等维度。原始版本包含445132条记录（含缺失值），清洗后246022条。UCI Cleveland数据集由Cleveland Clinic收集，包含303名患者的13个临床检测指标。":
        "Kaggle 2022是2020版本的加强版，字段从18个扩到40个，多了疫苗接种、COVID感染状态、口腔健康这些维度。原始445132条记录里有不少缺失值，清洗完剩246022条。UCI Cleveland数据集小得多，Cleveland Clinic收集的303名患者，13个临床检测指标。",

    # === 3.3 ODS (58.89) ===
    "ODS（Operational Data Store）层的职责是原样存储来自各数据源的原始数据，不做任何业务逻辑处理。本文在ODS层建立了4张Hive外部表，表3-2列出了各表的字段数和数据来源。":
        "ODS层干的事情就是把原始数据原封不动存进来，不改任何东西。这一层建了4张Hive外部表，具体见表3-2。",

    # === 3.4 DWD (65.87) ===
    "DWD（Data Warehouse Detail）层的职责是对ODS层的原始数据进行清洗、类型转换和字段标准化，产出可直接用于分析的明细数据。本文在DWD层建立了5张表，各表的职责如表3-3所示。":
        "DWD层接ODS层的原始数据，主要做三件事：清洗脏数据、转数据类型、统一字段名。处理完之后就是能直接拿来分析的明细数据了。这一层建了5张表，见表3-3。",

    "UCI Cleveland数据的清洗重点是缺失值处理。ca和thal两个字段中的问号(?)通过CASE WHEN替换为NULL。目标变量num从0-4的五分类简化为二分类：num>0则risk_label=1。年龄字段按10岁一档划分为年龄段，以便和Kaggle数据集对齐。":
        "UCI Cleveland数据集的问题主要是缺失值。ca和thal两个字段里有问号（?），用CASE WHEN换成了NULL。目标变量num原来是0到4五个值，这里简化成二分类：num>0就算有病，risk_label设为1。年龄按10岁一档分段，方便跟Kaggle那边对齐。",

    # === 3.4 统一特征表 (68.3) ===
    "统一特征样本表dwd_heart_feature_sample是DWD层的核心输出。该表通过UNION ALL将三个数据集的共有维度（risk_label、age_band、sex_code、bmi、smoking_flag等）合并为一张28列的宽表。Kaggle数据集缺少的临床指标字段（如trestbps、chol）用NULL填充，UCI数据集缺少的生活习惯字段同样用NULL填充。每条记录带有source_dataset字段标识来源，便于在ADS层按数据集分组统计。":
        "DWD层最关键的一张表是dwd_heart_feature_sample。做法是把三个数据集都有的维度（risk_label、age_band、sex_code、bmi、smoking_flag这些）用UNION ALL拼成一张28列的宽表。Kaggle那边没有的临床指标（trestbps、chol之类）填NULL，UCI那边没有的生活习惯字段也填NULL。每条记录多挂一个source_dataset字段标来源，ADS层按数据集分组的时候要用。",

    # === 3.5 ADS (58.5) ===
    "ADS（Application Data Service）层面向应用场景，对DWD层的明细数据做多维聚合，产出可直接供可视化和API查询使用的结果表。本文在ADS层建立了9张聚合表，覆盖6个分析维度，表结构汇总如表3-4所示。":
        "ADS层是直接面向应用的。DWD层的明细数据在这里按各种维度做GROUP BY聚合，产出的结果表前端可以直接拿来画图、后端可以直接拿来查。一共9张聚合表，6个分析维度，详见表3-4。",
}

count = 0
for old, new in replacements.items():
    if old in raw:
        raw = raw.replace(old, new)
        count += 1
with open(path, 'w', encoding='utf-8') as f:
    f.write(raw)
print(f"ch3.json: {count}/{len(replacements)} replacements applied")
