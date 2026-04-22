import json

path = "/Users/a136/vs/45425/thesis_project/papers/weibo-sentiment/meta.json"
with open(path, "r", encoding="utf-8") as f:
    raw = f.read()

pairs = [
    # 1: passive→active, clause reorder
    (
        "微博平台伴随社交媒体扩张积累了海量用户评论数据。",
        "社交媒体的持续扩张使微博平台上沉淀了规模庞大的用户评论数据。"
    ),
    # 2: split structure, subject swap
    (
        "从中高效提取舆情信息、完成趋势预测，是当前亟待解决的问题。",
        "舆情信息的高效提取与趋势预测已成为该领域当前亟需攻克的关键问题。"
    ),
    # 3: clause reorder, voice change
    (
        "本文围绕微博舆情情感分析与预测需求，设计并实现了一套依托Hadoop生态系统的处理系统。",
        "一套依托Hadoop生态系统的处理系统在本文中被设计与实现，用以满足微博舆情情感分析与预测的需求。"
    ),
    # 4: split into two, rearrange
    (
        "系统采用四层数据仓库架构（ODS-DWD-DWS-ADS），Hive负责数据清洗与多层聚合，PySpark负责关键词提取与话题热度预测。",
        "四层数据仓库架构（ODS-DWD-DWS-ADS）被系统所采用。数据清洗与多层聚合由Hive承担，关键词提取与话题热度预测则交由PySpark执行。"
    ),
    # 5: voice change, clause reorder
    (
        "情感分类管线基于scikit-learn构建，包含朴素贝叶斯、逻辑回归、支持向量机和随机森林四种模型。",
        "朴素贝叶斯、逻辑回归、支持向量机和随机森林四种模型共同组成了基于scikit-learn构建的情感分类管线。"
    ),
    # 6: subject-object swap, clause reorder
    (
        "实验在5万条微博评论数据集上展开，结果显示逻辑回归模型取得了最优F1分数0.6196。",
        "5万条微博评论数据集被用于实验验证，逻辑回归模型在其中取得了0.6196的最优F1分数。"
    ),
    # 7: rearrange, voice change
    (
        "系统另设计了16项舆情业务指标，覆盖情感正向率、负向预警指数、舆情健康评分等维度。",
        "情感正向率、负向预警指数、舆情健康评分等维度被16项舆情业务指标所覆盖，这些指标由系统另行设计。"
    ),
    # 8: active voice, subject swap
    (
        "7日趋势预测与可视化展示则由多项式回归完成。",
        "多项式回归承担了7日趋势预测与可视化展示的计算任务。"
    ),
    # 9: clause reorder, merge/restructure
    (
        "本文针对微博舆情监控的实际需求，设计并实现了一套依托Hadoop生态系统的情感分析与预测系统。",
        "微博舆情监控的实际需求驱动了本文的研究工作，一套以Hadoop生态系统为技术底座的情感分析与预测系统由此被设计并实现。"
    ),
]

for old, new in pairs:
    if old not in raw:
        print(f"WARNING: not found: {old[:30]}...")
    else:
        raw = raw.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(raw)

print("fix2_meta.py done")
