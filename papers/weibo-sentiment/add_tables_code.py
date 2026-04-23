"""
给ch1加业务总线矩阵表和业务构成分析表，给ch4各节加Hive SQL代码
"""
import json

HERE = '/Users/a136/vs/45425/thesis_project/papers/weibo-sentiment'

# ============ ch1: 加两张表 ============
with open(f'{HERE}/ch1.json', 'r', encoding='utf-8') as f:
    ch1 = json.load(f)

# 在1.2节的表1-1后面追加表1-2和表1-3
sec12 = ch1['sections'][1]  # 1.2 项目内容与目标

# 表1-2 业务总线矩阵表
table_1_2 = {
    "type": "table",
    "caption": "表1-2 业务总线矩阵表",
    "headers": ["数据域", "业务流程", "维度表", "", "事实表", "", "数据表", "", ""],
    "rows": []
}
# 简化headers，用实际可渲染的方式
table_1_2 = {
    "type": "table",
    "caption": "表1-2 业务总线矩阵表",
    "headers": ["数据域", "业务流程", "话题维度表", "情感维度表", "时间维度表", "热搜事实表", "评论事实表", "ODS原始表", "DWS汇总表"],
    "rows": [
        ["情感分布分析域", "正向情感率", "✓", "", "✓", "", "✓", "", "✓"],
        ["", "情感演变趋势", "✓", "✓", "✓", "", "✓", "", "✓"],
        ["", "分类情感交叉", "✓", "✓", "✓", "✓", "✓", "", "✓"],
        ["话题热度分析域", "每日平均热度", "✓", "", "✓", "✓", "", "✓", "✓"],
        ["", "热度Top10", "✓", "", "✓", "✓", "", "✓", "✓"],
        ["", "沸点频率", "✓", "", "✓", "✓", "", "✓", "✓"],
        ["", "关键词Top20", "✓", "", "✓", "✓", "", "✓", ""],
        ["舆情风险监控域", "负向预警指数", "✓", "✓", "✓", "", "✓", "", "✓"],
        ["", "热度波动率", "✓", "", "✓", "✓", "", "", "✓"],
        ["", "传播深度", "✓", "", "✓", "", "✓", "", "✓"],
        ["综合评价域", "互动活跃指数", "✓", "", "✓", "", "✓", "", "✓"],
        ["", "话题存活中位数", "✓", "", "✓", "✓", "", "", "✓"],
        ["", "分类分布", "✓", "", "✓", "✓", "", "✓", ""],
        ["复合融合域", "舆情健康评分", "✓", "✓", "✓", "", "", "", "✓"],
        ["", "正负面比值趋势", "", "✓", "✓", "", "✓", "", "✓"],
        ["", "情感波动率", "", "✓", "✓", "", "✓", "", "✓"],
    ]
}

# 表1-3 业务构成分析表
table_1_3 = {
    "type": "table",
    "caption": "表1-3 业务构成分析表",
    "headers": ["原生指标", "衍生指标", "派生指标"],
    "rows": [
        ["每日正向情感率", "各日正面评论占比变化", "情感健康趋势指数"],
        ["每日负向情感率", "各日负面评论占比变化", "负面舆情预警等级"],
        ["中性情感率", "各日中性评论稳定性", ""],
        ["每日平均热度", "各日话题热度环比变化", "热度异常波动信号"],
        ["热度Top10", "各日头部话题更替频率", ""],
        ["沸点频率", "各日沸点话题占比", "舆情剧烈程度指数"],
        ["关键词Top20", "各日高频词TF-IDF变化", ""],
        ["负向预警指数", "负面率+偏差+波动率加权", "四级预警等级"],
        ["热度波动率", "各日话题热度标准差", "运动素质均衡指数"],
        ["传播深度", "各话题评论数量与人均参与度", ""],
        ["互动活跃指数", "ln(评论数+1)*平均点赞*10", "社区共鸣效应"],
        ["话题存活中位数", "各日话题持续时长中位数", ""],
        ["舆情健康评分", "正面率*40+非负面*30+稳定*30", "发展潜力指数"],
        ["正负面比值趋势", "正面/负面评论数比值序列", ""],
        ["情感波动率", "7日滚动正负面率标准差", "健康风险预警指数"],
        ["7日趋势预测", "多项式回归外推7日", ""],
    ]
}

# 添加说明文字和两张表
text_1_2 = "项目的业务总线矩阵如表1-2所示，表中列出了五大数据域下各业务流程与维度表、事实表、数据表之间的对应关系。"
text_1_3 = "项目业务构成分析如表1-3所示，将16项指标按原生指标、衍生指标和派生指标三个层次进行分类。"

sec12['content'].extend([text_1_2, table_1_2, text_1_3, table_1_3])

with open(f'{HERE}/ch1.json', 'w', encoding='utf-8') as f:
    json.dump(ch1, f, ensure_ascii=False, indent=2)
print("ch1.json: 添加表1-2和表1-3")


# ============ ch4: 各节加Hive SQL代码 ============
with open(f'{HERE}/ch4.json', 'r', encoding='utf-8') as f:
    ch4 = json.load(f)

# 代码块用文本段落表示，以"代码"开头作为标识
code_blocks = {
    "4.1.1": "三类情感比例趋势的核心Hive SQL如下：SELECT stat_date, SUM(positive_count)/SUM(total_count) AS positive_ratio, SUM(neutral_count)/SUM(total_count) AS neutral_ratio, SUM(negative_count)/SUM(total_count) AS negative_ratio FROM dws_topic_sentiment_daily GROUP BY stat_date ORDER BY stat_date。计算逻辑是按天聚合三类评论计数再除以总数，结果写入ADS层。",

    "4.1.2": "正负面比值的计算SQL为：SELECT stat_date, SUM(positive_count)/GREATEST(SUM(negative_count),1) AS pn_ratio FROM dws_topic_sentiment_daily GROUP BY stat_date ORDER BY stat_date。分母用GREATEST函数兜底，防止负面评论数为零时除零报错。7日趋势预测部分在Python端用numpy.polyfit做2次多项式拟合。",

    "4.1.3": "分来源情感趋势的SQL为：SELECT stat_date, source, SUM(positive_count)/SUM(total_count) AS pos_ratio, SUM(negative_count)/SUM(total_count) AS neg_ratio FROM dws_topic_sentiment_daily GROUP BY stat_date, source ORDER BY stat_date, source。按source字段分组后分别计算各来源的正面率和负面率。",

    "4.2.1": "评论量与负面比例联动查询SQL为：SELECT stat_date, SUM(total_count) AS daily_comments, SUM(negative_count)/SUM(total_count) AS neg_ratio FROM dws_topic_sentiment_daily GROUP BY stat_date ORDER BY stat_date。左轴取daily_comments画柱状图，右轴取neg_ratio画折线图，双轴叠加展示。",

    "4.3.1": "负向预警指数的计算包含三个维度的加权融合。SQL核心部分为：SELECT stat_date, (neg_ratio_score*50 + deviation_score*30 + volatility_score*20) AS alert_index FROM (SELECT stat_date, negative_ratio*100 AS neg_ratio_score, ABS(negative_count - AVG(negative_count) OVER(ORDER BY stat_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)) / GREATEST(STDDEV(negative_count) OVER(ORDER BY stat_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 0.01) * 10 AS deviation_score, STDDEV(negative_ratio) OVER(ORDER BY stat_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) * 100 AS volatility_score FROM dws_topic_sentiment_daily) t。三个分项分别对应负面率水平、负面数量偏差和短期波动率，按50:30:20加权合成。",

    "4.3.2": "情感波动率用7日滚动窗口计算标准差：SELECT stat_date, STDDEV(positive_ratio) OVER(ORDER BY stat_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS pos_volatility, STDDEV(negative_ratio) OVER(ORDER BY stat_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS neg_volatility FROM dws_topic_sentiment_daily ORDER BY stat_date。正面和负面分别算，窗口大小固定为7天。",

    "4.4.1": "舆情健康评分的合成SQL为：SELECT a.stat_date, a.positive_ratio*40 + (1-b.negative_ratio)*30 + (1-LEAST(c.pos_volatility*10, 1))*30 AS health_score FROM ads_sentiment_positive_ratio a JOIN dws_topic_sentiment_daily b ON a.stat_date=b.stat_date JOIN ads_heat_volatility c ON a.stat_date=c.stat_date。正面率权重40%，非负面率权重30%，稳定性权重30%，三项加起来归一化到0-100分。",
}

# 遍历ch4的所有subsection，在每个subsection的content末尾（图表之前）插入代码段
count = 0
for sec in ch4['sections']:
    for sub in sec.get('subsections', []):
        title = sub['title']
        # 匹配 4.1.1 等编号
        for key, code_text in code_blocks.items():
            if key in title:
                sub['content'].append(code_text)
                count += 1
                break

with open(f'{HERE}/ch4.json', 'w', encoding='utf-8') as f:
    json.dump(ch4, f, ensure_ascii=False, indent=2)
print(f"ch4.json: 添加{count}段指标计算代码")
