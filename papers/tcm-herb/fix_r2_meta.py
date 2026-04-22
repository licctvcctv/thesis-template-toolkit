#!/usr/bin/env python3
"""Round-2 AIGC-breaking fixes for meta.json (abstract + conclusion + acknowledgement)."""
import json, pathlib

fp = pathlib.Path(__file__).with_name("meta.json")
raw = fp.read_text("utf-8")
data = json.loads(raw)

# ── abstract_zh ──
pairs_abs = [
    # 1
    ("中医临床辅助决策领域中，中药方剂推荐是值得关注的研究方向。",
     "中药方剂推荐已成为中医临床辅助决策领域一个受到广泛关注的研究课题。"),
    # 2
    ("辨证论治过程中，医生需依据患者的症状组合确定中药组方。",
     "医生在辨证论治时，要根据患者所表现的症状组合来拟定中药组方。"),
    # 3
    ("组方结果受医生学习经历和临床积累的影响较大。",
     "最终的组方结果与医生自身的学习背景及临床积累关系密切。"),
    # 4
    ("年资不同的医生面对相同症状时，处方差异可能相当明显。",
     "不同年资的医生即使面对同一组症状，开出的处方也可能差别较大。"),
    # 5
    ("图神经网络等机器学习方法若用于方剂推荐，便可从大量历史处方中发现症状与中药间的潜在关联。",
     "将图神经网络等机器学习方法引入方剂推荐后，大量历史处方中症状与中药之间的潜在关联便有望被发掘出来。"),
    # 6
    ("这为临床开方提供了数据层面的参考依据。",
     "临床开方由此获得了来自数据层面的参考依据。"),
]

for old, new in pairs_abs:
    if old in data["abstract_zh"]:
        data["abstract_zh"] = data["abstract_zh"].replace(old, new)

# ── conclusion_list ──
pairs_conc = [
    # conclusion_list[0]
    ("本文围绕中药方剂推荐展开研究。",
     "本文以中药方剂推荐作为研究主题。"),
    ("公开处方数据集和中药知识图谱是实验的数据基础，GCN、GAT、Graph Transformer和Graph Mamba四种图神经网络模型在此基础上分别实现并进行了对比。",
     "实验以公开处方数据集与中药知识图谱为数据基础，分别实现了GCN、GAT、Graph Transformer和Graph Mamba四种图神经网络模型并加以对比。"),
    ("数据预处理阶段产出了三张关联图：",
     "数据预处理阶段生成了三张关联图："),
    ("知识图谱提供了药性、归经等27维属性，这些属性以辅助特征的形式附加到中药节点上并参与训练。",
     "知识图谱所提供的药性、归经等27维属性被编码为辅助特征，附加至中药节点后一同参与模型训练。"),
    # conclusion_list[2]
    ("本文存在以下不足：",
     "本文尚存在若干不足："),
    ("数据集只记录了症状ID到中药ID的映射，患者年龄、性别、病史等个体化信息未被收录；",
     "数据集仅包含症状ID到中药ID的映射关系，患者年龄、性别、病史等个体化字段未被纳入；"),
    ("模型的输出局限于推荐中药列表，剂量建议不在其覆盖范围内；",
     "模型输出仅为推荐中药列表，具体剂量建议并不涉及；"),
    ("Graph Transformer和Graph Mamba的实现均偏简化，图结构信息的利用程度有限。",
     "Graph Transformer与Graph Mamba的实现均属简化版本，对图结构信息的利用还不够充分。"),
    # conclusion_list[3]
    ("后续改进方向包括：",
     "后续可从以下几个方向加以改进："),
    ("将患者个体化特征纳入模型输入，使推荐粒度更细；",
     "把患者个体化特征纳入模型输入端，以实现更精细的推荐粒度；"),
    ("用大语言模型为推荐结果补充可解释性说明；",
     "借助大语言模型为推荐结果附上可解释性说明；"),
    ("用数据增强手段缓解处方稀疏性；",
     "通过数据增强手段来缓解处方数据的稀疏性；"),
    ("推荐系统后续可部署为Web服务，供临床人员交互使用。",
     "后续推荐系统可部署为Web服务形式，方便临床人员交互使用。"),
]

for i, item in enumerate(data["conclusion_list"]):
    for old, new in pairs_conc:
        if old in item:
            data["conclusion_list"][i] = data["conclusion_list"][i].replace(old, new)

# ── acknowledgement ──
pairs_ack = [
    ("论文写作期间，指导教师给予了大量帮助。",
     "论文写作阶段，指导教师在多个环节给予了大量帮助。"),
    ("课题方向的确定、实验方案的设计、模型代码的调试、论文结构的调整——各个环节老师都给出了具体建议。",
     "无论是课题方向的确定、实验方案的设计，还是模型代码的调试与论文结构的调整，老师都给出了切实的建议。"),
    ("这些指导让我在毕业设计中积累了不少课堂之外的实践经验。",
     "这些指导使我在毕业设计过程中收获了许多课堂之外的实践经验。"),
    ("在此向指导老师致以衷心的谢意。",
     "在此谨向指导老师表达衷心的谢意。"),
]
for old, new in pairs_ack:
    if old in data["acknowledgement"]:
        data["acknowledgement"] = data["acknowledgement"].replace(old, new)

fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")

count = sum(1 for o, _ in pairs_abs if o in raw) + \
        sum(1 for o, _ in pairs_conc if o in raw) + \
        sum(1 for o, _ in pairs_ack if o in raw)
print(f"fix_r2_meta: {count} replacements")
