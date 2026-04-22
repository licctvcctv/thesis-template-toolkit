import os
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "meta.json")
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()
replacements = {
    # 1 med - abstract opening
    "随着社交媒体的快速发展，微博平台积累了海量用户评论数据，如何从中高效提取舆情信息并进行趋势预测成为亟待解决的问题。":
    "微博平台伴随社交媒体扩张积累了海量用户评论数据。从中高效提取舆情信息、完成趋势预测，是当前亟待解决的问题。",

    # 2 med
    "本文设计并实现了一套基于Hadoop生态系统的微博舆情情感分析与预测系统。":
    "本文围绕微博舆情情感分析与预测需求，设计并实现了一套依托Hadoop生态系统的处理系统。",

    # 3-5 med (continuous sentence in abstract)
    "系统采用四层数据仓库架构（ODS-DWD-DWS-ADS），利用Hive完成数据清洗与多层聚合，通过PySpark实现关键词提取与话题热度预测，并基于scikit-learn构建了包含朴素贝叶斯、逻辑回归、支持向量机和随机森林在内的多模型情感分类管线。":
    "系统采用四层数据仓库架构（ODS-DWD-DWS-ADS），Hive负责数据清洗与多层聚合，PySpark负责关键词提取与话题热度预测。情感分类管线基于scikit-learn构建，包含朴素贝叶斯、逻辑回归、支持向量机和随机森林四种模型。",

    # 6 med
    "在5万条微博评论数据集上的实验表明，逻辑回归模型取得了最优的F1分数0.6196。":
    "实验在5万条微博评论数据集上展开，结果显示逻辑回归模型取得了最优F1分数0.6196。",

    # 7-8 med
    "系统还设计了16项舆情业务指标，涵盖情感正向率、负向预警指数、舆情健康评分等维度，并通过多项式回归实现7日趋势预测与可视化展示。":
    "系统另设计了16项舆情业务指标，覆盖情感正向率、负向预警指数、舆情健康评分等维度。7日趋势预测与可视化展示则由多项式回归完成。",

    # 9 low - conclusion_list first item
    "本文围绕微博舆情监控的实际需求，设计并实现了一套基于Hadoop生态系统的情感分析与预测系统，搭建了ODS-DWD-DWS-ADS四层数据仓库，设计了涵盖五大分析域的16项业务指标，构建了四种机器学习分类模型的对比实验（逻辑回归取得最优F1分数0.6196），并通过多项式回归实现了7日多维度趋势预测与可视化。":
    "本文针对微博舆情监控的实际需求，设计并实现了一套依托Hadoop生态系统的情感分析与预测系统。系统搭建了ODS-DWD-DWS-ADS四层数据仓库，设计了涵盖五大分析域的16项业务指标，完成了四种机器学习分类模型的对比实验（逻辑回归取得最优F1分数0.6196）。7日多维度趋势预测与可视化由多项式回归实现。",
}
count = 0
for old, new in replacements.items():
    if old in raw:
        raw = raw.replace(old, new)
        count += 1
with open(path, 'w', encoding='utf-8') as f:
    f.write(raw)
print(f"meta.json: {count}/{len(replacements)} applied")
