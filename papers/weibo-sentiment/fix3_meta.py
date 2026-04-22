#!/usr/bin/env python3
"""R3 fix for meta.json: convert passive inversions to active voice."""
import json

path = "meta.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False, indent=2)

replacements = [
    # === abstract_zh (9 flagged) ===
    (
        "社交媒体的持续扩张使微博平台上沉淀了规模庞大的用户评论数据。",
        "社交媒体不断扩张，微博平台因而积累了规模庞大的用户评论数据。"
    ),
    (
        "舆情信息的高效提取与趋势预测已成为该领域当前亟需攻克的关键问题。",
        "如何高效提取舆情信息并完成趋势预测，是该领域当前亟需攻克的关键问题。"
    ),
    (
        "一套依托Hadoop生态系统的处理系统在本文中被设计与实现，用以满足微博舆情情感分析与预测的需求。",
        "本文设计并实现了一套依托Hadoop生态系统的处理系统，旨在满足微博舆情情感分析与预测的需求。"
    ),
    (
        "四层数据仓库架构（ODS-DWD-DWS-ADS）被系统所采用。",
        "系统采用四层数据仓库架构（ODS-DWD-DWS-ADS）。"
    ),
    (
        "数据清洗与多层聚合由Hive承担，关键词提取与话题热度预测则交由PySpark执行。",
        "Hive负责数据清洗与多层聚合，PySpark则执行关键词提取与话题热度预测。"
    ),
    (
        "朴素贝叶斯、逻辑回归、支持向量机和随机森林四种模型共同组成了基于scikit-learn构建的情感分类管线。",
        "本文基于scikit-learn构建情感分类管线，纳入朴素贝叶斯、逻辑回归、支持向量机和随机森林四种模型。"
    ),
    (
        "5万条微博评论数据集被用于实验验证，逻辑回归模型在其中取得了0.6196的最优F1分数。",
        "实验在5万条微博评论数据集上展开验证，逻辑回归模型取得0.6196的最优F1分数。"
    ),
    (
        "情感正向率、负向预警指数、舆情健康评分等维度被16项舆情业务指标所覆盖，这些指标由系统另行设计。",
        "系统另行设计了16项舆情业务指标，覆盖情感正向率、负向预警指数、舆情健康评分等维度。"
    ),
    (
        "多项式回归承担了7日趋势预测与可视化展示的计算任务。",
        "7日趋势预测与可视化展示的计算任务由多项式回归方法完成。"
    ),
    # === conclusion_list[0] ===
    (
        "微博舆情监控的实际需求驱动了本文的研究工作，一套以Hadoop生态系统为技术底座的情感分析与预测系统由此被设计并实现。",
        "本文围绕微博舆情监控的实际需求开展研究，设计并实现了一套以Hadoop生态系统为技术底座的情感分析与预测系统。"
    ),
    (
        "7日多维度趋势预测与可视化由多项式回归实现。",
        "多项式回归方法完成了7日多维度趋势预测与可视化功能。"
    ),
]

count = 0
for old, new in replacements:
    if old in json_str:
        json_str = json_str.replace(old, new)
        count += 1
    else:
        print(f"WARNING: not found: {old[:40]}...")

with open(path, "w", encoding="utf-8") as f:
    f.write(json_str)

print(f"fix3_meta.py: {count} replacements applied")
