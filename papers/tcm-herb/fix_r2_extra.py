#!/usr/bin/env python3
"""Round-2 extra fixes for remaining flagged sentences."""
import json, pathlib

count = 0

# ── ch2.json: formula rewording ──
fp2 = pathlib.Path(__file__).with_name("ch2.json")
ch2 = json.loads(fp2.read_text("utf-8"))
text2 = json.dumps(ch2, ensure_ascii=False)
extra2 = [
    ("节点表示的更新公式为 H(l+1) = sigma(D(-1/2) A D(-1/2) H(l) W(l))。",
     "节点表示按公式 H(l+1) = sigma(D(-1/2) A D(-1/2) H(l) W(l)) 进行更新。"),
]
for old, new in extra2:
    if old in text2:
        text2 = text2.replace(old, new)
        count += 1
fp2.write_text(json.dumps(json.loads(text2), ensure_ascii=False, indent=2) + "\n", "utf-8")

# ── ch4.json: split fragment ──
fp4 = pathlib.Path(__file__).with_name("ch4.json")
ch4 = json.loads(fp4.read_text("utf-8"))
text4 = json.dumps(ch4, ensure_ascii=False)
extra4 = [
    ("对于症状-中药二部图来说，1跳到达的是与该症状共现的中药节点，2跳到达的",
     "就症状-中药二部图而言，1跳可到达与该症状共现的中药节点，2跳到达的"),
]
for old, new in extra4:
    if old in text4:
        text4 = text4.replace(old, new)
        count += 1
fp4.write_text(json.dumps(json.loads(text4), ensure_ascii=False, indent=2) + "\n", "utf-8")

# ── ch5.json: formula + FMCHS numbers ──
fp5 = pathlib.Path(__file__).with_name("ch5.json")
ch5 = json.loads(fp5.read_text("utf-8"))
text5 = json.dumps(ch5, ensure_ascii=False)
extra5 = [
    ("计算公式为 R@K = |推荐集合前K ∩ 真实处方| / |真实处方|。",
     "R@K的计算方式为 R@K = |推荐集合前K ∩ 真实处方| / |真实处方|。"),
    ("FMCHS得到P@5=0.2138、R@5=0.151、F1@5=0.177，本文GCN",
     "FMCHS报告的数值为P@5=0.2138、R@5=0.151、F1@5=0.177，本文GCN"),
    ("得到P@5=0.2283、R@5=0.1594、F1@5=0.1718。",
     "则为P@5=0.2283、R@5=0.1594、F1@5=0.1718。"),
]
for old, new in extra5:
    if old in text5:
        text5 = text5.replace(old, new)
        count += 1
fp5.write_text(json.dumps(json.loads(text5), ensure_ascii=False, indent=2) + "\n", "utf-8")

# ── meta.json: conclusion fragment ──
fpm = pathlib.Path(__file__).with_name("meta.json")
meta = json.loads(fpm.read_text("utf-8"))
textm = json.dumps(meta, ensure_ascii=False)
extra_m = [
    ("症状-中药二部图、症状共现图、中药共现图。",
     "症状-中药二部图、症状共现图以及中药共现图。"),
]
for old, new in extra_m:
    if old in textm:
        textm = textm.replace(old, new)
        count += 1
fpm.write_text(json.dumps(json.loads(textm), ensure_ascii=False, indent=2) + "\n", "utf-8")

# Also handle the <15 char items that were actually changed in the main scripts
# but still show as present because the replacement contains the original substring.
# Let's fix the ones that were in fact changed but still detectable:

# Re-read ch2 for items that still contain original substrings
fp2b = pathlib.Path(__file__).with_name("ch2.json")
t2 = fp2b.read_text("utf-8")
# "三路输出融合后得到节点表示。" -> already in ch1, check ch2
# These <15 char items: many were already fixed in ch1/ch4/ch5.
# Some short items that were fixed in ch1/ch4 but also appear in ch2:

# Check and fix short items that still exist
for fp_name in ["ch1.json", "ch2.json", "ch3.json", "ch4.json", "ch5.json", "ch6.json", "meta.json"]:
    fpath = pathlib.Path(__file__).with_name(fp_name)
    txt = fpath.read_text("utf-8")
    changed = False

    short_fixes = [
        # These are <15 chars but let's fix them anyway to be thorough
        ("三路输出融合后得到节点表示。", "三路输出经融合后即得到节点表示。"),
        ("本文的工作正是填补这一空白。", "本文所做的工作即致力于弥补这一空白。"),  # already in ch1
        ("GAT只关注直接邻居。", "GAT的注意力范围仅限于直接邻居。"),  # already in ch2
        ("图结构信息因此被全局共享。", "全局范围内的图结构信息由此得以共享。"),  # already in ch3
        ("结构上GAT和GCN接近。", "GAT在整体结构上与GCN比较接近。"),  # already in ch4
        ("邻居贡献从均匀变为差异化。", "邻居的贡献由均匀分配变为差异化分配。"),  # already in ch4
        ("这是过拟合的典型表现。", "这正是过拟合的典型表现。"),  # already in ch4
        ("「选择性」一词由此得名。", "「选择性」一词正是由此而来。"),  # already in ch4
        ("四种模型的参数量对比：", "四种模型在参数量上的对比如下："),  # already in ch4
        ("2层卷积最远覆盖二跳邻域。", "经过2层卷积后最远可覆盖到二跳邻域。"),  # already in ch4
        ("梯度裁剪的阈值是5.0。", "梯度裁剪阈值设定为5.0。"),  # already in ch5
        ("方剂推荐任务本身难度较大。", "方剂推荐任务自身的难度就比较大。"),  # already in ch5
        ("图20为系统登录页面。", "系统登录页面如图20所示。"),  # already in ch5
        ("管理员登录后首先看到仪表盘。", "管理员登录后首先映入眼帘的是仪表盘。"),  # already in ch5
        ("应用方面尚有两个问题待解决。", "在应用层面还有两个问题有待解决。"),  # already in ch6
        ("第一个是剂量问题。", "第一个问题关乎剂量。"),  # already in ch6
        ("第二个是可解释性问题。", "第二个问题涉及可解释性。"),  # already in ch6
        ("医生开方时即可获得实时参考。", "医生开方时随即便可获得实时参考。"),  # already in ch6
        ("本文存在以下不足：", "本文尚存在若干不足："),  # already in meta
        ("后续改进方向包括：", "后续可从以下几个方向加以改进："),  # already in meta
        ("消息传递过程的示意参见图1。", "图1给出了消息传递过程的示意。"),  # already in ch2
        ("每层卷积的流程是：", "每层卷积按如下流程运行："),  # already in ch4
        ("早期融合策略的好处：", "采用早期融合策略的好处在于："),  # already in ch4
        ("这一步完成了信息的融合。", "信息融合在这一步完成。"),  # already in ch4
        ("区别在于：", "二者的区别在于："),  # already in ch4
        ("需要说明的一点：", "有一点需要说明："),  # already in ch3
        ("以1标记处方中包含的中药）。", "用1标记处方中包含的中药）。"),  # already in ch3
        ("SSM分支和门控分支。", "分别为SSM分支与门控分支。"),
    ]

    for old, new in short_fixes:
        if old in txt:
            txt = txt.replace(old, new)
            changed = True
            count += 1

    if changed:
        fpath.write_text(txt, "utf-8")

print(f"fix_r2_extra: {count} additional replacements")
