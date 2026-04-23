"""AIGC break: meta.json — 摘要 + 结论"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "meta.json")
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

replacements = {
    # === 摘要 (69.9) ===
    "心血管疾病长期占据全球致死病因首位，早期风险识别对降低发病率和死亡率至关重要。":
        "心血管疾病的致死人数多年来一直排在全球第一位。能不能在发病之前把高风险的人筛出来，直接关系到发病率和死亡率能不能降下去。",

    "本文围绕心脏病健康数据，设计并实现了一套涵盖离线数据仓库、统计分析、机器学习预测和Web可视化的大数据分析系统。":
        "这篇论文做的事情是：拿心脏病相关的健康数据，搭一套从离线数据仓库、统计分析、机器学习预测到Web可视化都能跑通的大数据分析系统。",

    "数据方面，系统整合了Kaggle 2020心脏病调查数据集（319795条记录、18个字段）、Kaggle 2022扩展版（246022条、40个字段）以及UCI Cleveland临床数据集（303条、13个临床指标），在Hadoop平台上通过Hive构建了ODS-DWD-ADS三层数据仓库，完成数据清洗、字段标准化和多维聚合，最终将ADS层结果同步至MySQL供在线查询。":
        "数据一共用了三份：Kaggle 2020心脏病调查（319795条、18个字段）、Kaggle 2022扩展版（246022条、40个字段）、UCI Cleveland临床数据（303条、13个临床指标）。三份数据全部灌进Hadoop，用Hive搭了ODS-DWD-ADS三层仓库，做完清洗、字段对齐和多维聚合之后，ADS层的结果同步到MySQL给线上用。",

    "分析维度覆盖年龄、性别、BMI、生活习惯、共病史和UCI临床指标六个方面。":
        "分析的角度有六个：年龄、性别、BMI、生活习惯、共病史、UCI临床指标。",

    "在Kaggle 2020数据集上训练了逻辑回归、SGD、随机森林和Extra Trees四种分类模型，以AUC为主要选择标准。逻辑回归以0.8207的AUC胜出，召回率达到78.30%；在UCI Cleveland数据集上，同一模型AUC达到0.9665，准确率86.89%。":
        "在Kaggle 2020数据上跑了逻辑回归、SGD、随机森林、Extra Trees四个模型，拿AUC当主要选型标准。最后逻辑回归AUC=0.8207排第一，召回率78.30%。换到UCI Cleveland数据集上，同一个模型AUC到了0.9665，准确率86.89%。",

    "系统前端采用Vue3配合ECharts搭建可视化大屏和多页分析界面，后端基于Django REST Framework提供数据查询与在线预测接口，用户输入健康指标后即可获得心脏病风险等级和关键影响因素。":
        "前端用Vue3+ECharts画了可视化大屏和多页分析界面，后端是Django REST Framework，提供数据查询和在线预测两类接口。用户把自己的健康指标填进去，就能拿到心脏病风险等级和影响最大的几个因素。",

    "整个系统以Docker Compose容器化部署，前后端分离，具备一定的工程可用性。":
        "整套系统用Docker Compose打包部署，前后端分开跑，工程上基本能用。",

    # === 结论 (68.16) ===
    "本文以心脏病健康数据为研究对象，完成了数据仓库构建、多维统计分析、机器学习建模和Web系统开发四项工作。":
        "这篇论文围绕心脏病健康数据，做了四件事：建数据仓库、跑多维统计、训练机器学习模型、开发Web系统。",

    "数据层面，三个公开数据集经ODS-DWD-ADS三层Hive数据仓库完成了清洗和标准化，9张ADS聚合表覆盖了年龄、性别、BMI、生活习惯、共病史和UCI临床指标六个分析维度。":
        "数据这块，三份公开数据集走了ODS-DWD-ADS三层Hive仓库，清洗和标准化之后产出9张ADS聚合表，分别对应年龄、性别、BMI、生活习惯、共病史、UCI临床指标六个维度。",

    "模型层面，Kaggle数据集上逻辑回归以0.8207的AUC和78.30%的召回率胜出，UCI数据集上AUC达到0.9665。":
        "模型这块，Kaggle数据上逻辑回归AUC=0.8207、召回率78.30%，排第一。UCI数据上同一模型AUC到了0.9665。",

    "系统层面，Vue3+ECharts前端提供可视化大屏和分页分析界面，Django后端提供RESTful查询和在线预测接口，Docker Compose实现容器化部署。":
        "系统这块，Vue3+ECharts负责可视化大屏和分页分析界面，Django后端负责RESTful查询和在线预测，Docker Compose负责容器化部署。",

    "系统目前存在以下不足：Kaggle数据集正负样本严重不均衡（阳性仅约8.6%），导致模型精确率偏低（23.31%）；数据仓库未接入实时数据流，仅支持离线批处理；预测模型只输出风险概率，缺少可解释性分析。":
        "目前的问题也比较明显。Kaggle数据集阳性只有8.6%，正负样本差太多，模型精确率只有23.31%。数据仓库只能离线批处理，没接实时数据流。预测模型也只输出一个概率值，没有可解释性分析。",

    "后续可从三方面改进：引入SMOTE过采样或Focal Loss来缓解类别不均衡；在Hive基础上加入Spark Streaming支持准实时分析；结合SHAP值为预测结果提供特征级解释，提升医疗场景下的可信度。":
        "后面如果要改，样本不平衡的问题可以试SMOTE过采样或者Focal Loss；实时性的问题可以在Hive旁边加一路Spark Streaming；可解释性的问题可以用SHAP值给每个预测结果标出哪些特征影响最大。",
}

count = 0
for old, new in replacements.items():
    if old in raw:
        raw = raw.replace(old, new)
        count += 1
with open(path, 'w', encoding='utf-8') as f:
    f.write(raw)
print(f"meta.json: {count}/{len(replacements)} replacements applied")
