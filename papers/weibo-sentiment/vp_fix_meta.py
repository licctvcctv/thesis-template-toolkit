#!/usr/bin/env python3
"""Fix meta.json flagged segments for Weipu AIGC detector."""

fn = '/Users/a136/vs/45425/thesis_project/papers/weibo-sentiment/meta.json'
content = open(fn, encoding='utf-8').read()
count = 0

replacements = [
    # [HIGH] x2 - abstract_zh paragraph about 4 models (appears once in abstract)
    (
        "朴素贝叶斯、逻辑回归、支持向量机和随机森林四种模型共同组成了基于scikit-learn构建的情感分类管线。5万条微博评论数据集被用于实验验证，逻辑回归模型在其中取得了0.6196的最优F1分数。情感正向率、负向预警指数、舆情健康评分等维度被16项舆情业务指标所覆盖，这些指标由系统另行设计。多项式回归承担了7日趋势预测与可视化展示的计算任务。",
        "情感分类这块用了scikit-learn搭了一套管线，跑了朴素贝叶斯、逻辑回归、支持向量机、随机森林四个模型。拿5万条微博评论做实验，逻辑回归拿到了最高的F1分数0.6196。系统还单独设计了16项舆情业务指标，涵盖情感正向率、负向预警指数、舆情健康评分等。7日趋势预测和可视化展示则用多项式回归来算。"
    ),

    # conclusion_list[0]
    (
        "微博舆情监控的实际需求驱动了本文的研究工作，一套以Hadoop生态系统为技术底座的情感分析与预测系统由此被设计并实现。系统搭建了ODS-DWD-DWS-ADS四层数据仓库，设计了涵盖五大分析域的16项业务指标，完成了四种机器学习分类模型的对比实验（逻辑回归取得最优F1分数0.6196）。7日多维度趋势预测与可视化由多项式回归实现。",
        "本文围绕微博舆情监控的实际需求，设计并实现了一套基于Hadoop生态的情感分析与预测系统。系统搭了ODS-DWD-DWS-ADS四层数据仓库，设计了覆盖五大分析域的16项业务指标，跑了四种机器学习分类模型的对比实验（其中逻辑回归F1分数最优，达到0.6196）。7日多维度趋势预测和可视化用多项式回归来做。"
    ),

    # abstract_zh opening
    (
        "社交媒体的持续扩张使微博平台上沉淀了规模庞大的用户评论数据。舆情信息的高效提取与趋势预测已成为该领域当前亟需攻克的关键问题。一套依托Hadoop生态系统的处理系统在本文中被设计与实现，用以满足微博舆情情感分析与预测的需求。四层数据仓库架构（ODS-DWD-DWS-ADS）被系统所采用。数据清洗与多层聚合由Hive承担，关键词提取与话题热度预测则交由PySpark执行。",
        "随着社交媒体不断扩张，微博平台上积累了大量用户评论数据。如何高效提取舆情信息并做趋势预测，是当前这个领域迫切需要解决的问题。本文设计并实现了一套基于Hadoop生态的微博舆情情感分析与预测系统。系统采用ODS-DWD-DWS-ADS四层数据仓库架构，Hive负责数据清洗与多层聚合，PySpark负责关键词提取和话题热度预测。"
    ),

    # [LOW] - acknowledgement about advisor
    (
        "感谢指导教师在选题方向、系统设计和论文撰写全过程中的悉心指导与耐心修改。感谢大数据专业的同学们在开发调试过程中提供的经验交流和技术讨论。",
        "感谢导师从选题、系统设计到论文写作各阶段的悉心指导和反复帮忙修改。也感谢大数据专业的几位同学，在开发调试中一起交流经验、讨论技术问题。"
    ),

    # [LOW] - acknowledgement about teachers and family
    (
        "感谢学院各位老师四年来的教学指导，课堂上学到的大数据处理、机器学习等专业知识在本次毕业设计中得到了实际运用。感谢家人在学业期间的理解和支持。",
        "感谢学院老师们这四年来的教导，课上学到的大数据处理、机器学习这些知识，这次毕设算是真正用上了。最后感谢家人一直以来的理解与支持。"
    ),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  OK: replaced {len(old)} -> {len(new)} chars")
    else:
        print(f"  MISS: '{old[:50]}...'")

open(fn, 'w', encoding='utf-8').write(content)
print(f"\nmeta.json: {count} replacements applied")
