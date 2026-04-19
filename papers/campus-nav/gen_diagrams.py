"""生成校园导航系统论文图表：单实体ER图 + 总ER图（Kroki neato+pos）"""
import math
import requests
import os
import zlib
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")


def kroki_png(dot_src, engine="graphviz"):
    compressed = zlib.compress(dot_src.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    url = f"https://kroki.io/{engine}/png/{encoded}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def save(filename, data):
    path = os.path.join(IMG_DIR, filename)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  ✓ {filename} ({len(data)//1024}KB)")


def entity_er(entity_name, attrs, pk_attrs=None):
    """生成单实体 ER 图的 DOT 代码（属性椭圆围绕实体框）"""
    pk_attrs = pk_attrs or []
    lines = [
        'graph {',
        '  layout=neato;',
        '  overlap=false;',
        '  sep="+6";',
        '  node [fontname="SimSun", fontsize=12];',
        '  edge [len=1.5];',
        f'  entity [shape=box, style=bold, label="{entity_name}", pos="0,0!"];',
    ]
    n = len(attrs)
    radius = 1.8
    for i, attr in enumerate(attrs):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = round(radius * math.cos(angle), 2)
        y = round(radius * math.sin(angle), 2)
        node_id = f"a{i}"
        if attr in pk_attrs:
            label = f"<U>{attr}</U>"
            lines.append(f'  {node_id} [shape=ellipse, label=<{label}>, pos="{x},{y}!"];')
        else:
            lines.append(f'  {node_id} [shape=ellipse, label="{attr}", pos="{x},{y}!"];')
        lines.append(f'  entity -- {node_id};')
    lines.append('}')
    return '\n'.join(lines)


# ---- 7个实体定义 ----
entities = {
    "er-user": {
        "name": "用户",
        "attrs": ["用户编号", "用户名", "密码", "角色", "注册时间"],
        "pk": ["用户编号"]
    },
    "er-poi": {
        "name": "兴趣点",
        "attrs": ["编号", "名称", "类型", "经度", "纬度", "描述", "创建者ID", "创建时间"],
        "pk": ["编号"]
    },
    "er-announcement": {
        "name": "公告",
        "attrs": ["公告编号", "标题", "内容", "类型", "激活状态", "发布者ID", "创建时间"],
        "pk": ["公告编号"]
    },
    "er-navlog": {
        "name": "导航日志",
        "attrs": ["日志编号", "用户ID", "起点", "终点", "距离", "时长", "创建时间"],
        "pk": ["日志编号"]
    },
    "er-category": {
        "name": "兴趣点分类",
        "attrs": ["分类编号", "分类名称", "图标", "颜色", "排序号"],
        "pk": ["分类编号"]
    },
    "er-building": {
        "name": "建筑物",
        "attrs": ["建筑编号", "建筑名称", "轮廓坐标", "层数", "用途"],
        "pk": ["建筑编号"]
    },
    "er-favorite": {
        "name": "收藏记录",
        "attrs": ["收藏编号", "用户ID", "兴趣点ID", "收藏时间"],
        "pk": ["收藏编号"]
    },
}

# ---- 总 ER 图（只有实体和关系，Kroki neato+pos）----
summary_dot = '''graph {
  layout=neato;
  overlap=false;
  sep="+10";
  node [fontname="SimSun", fontsize=13];
  edge [fontname="SimSun", fontsize=10, len=2.5];

  /* 第一行：收藏记录 -- 用户 -- 建筑物 */
  fav      [shape=box, style=bold, label="收藏记录",   pos="-3,4!"];
  user     [shape=box, style=bold, label="用户",       pos="3,5!"];
  building [shape=box, style=bold, label="建筑物",     pos="9,5!"];

  /* 第二行：公告 -- 兴趣点 -- 导航日志 */
  notice   [shape=box, style=bold, label="公告",       pos="-1,1!"];
  poi      [shape=box, style=bold, label="兴趣点",     pos="5,1!"];
  navlog   [shape=box, style=bold, label="导航日志",   pos="9,1!"];

  /* 第三行：分类 */
  category [shape=box, style=bold, label="兴趣点分类", pos="5,-2!"];

  /* 关系节点 */
  r1 [shape=diamond, label="收藏", pos="0,4.5!"];
  r2 [shape=diamond, label="发布", pos="0,3!"];
  r3 [shape=diamond, label="创建", pos="4,3!"];
  r4 [shape=diamond, label="产生", pos="7,3!"];
  r5 [shape=diamond, label="属于", pos="5,-0.5!"];
  r6 [shape=diamond, label="避障", pos="9,3!"];

  /* 连线 */
  user -- r1 [label="1"];
  r1 -- fav [label="n"];
  user -- r2 [label="1"];
  r2 -- notice [label="n"];
  user -- r3 [label="1"];
  r3 -- poi [label="n"];
  user -- r4 [label="1"];
  r4 -- navlog [label="n"];
  poi -- r5 [label="n"];
  r5 -- category [label="1"];
  building -- r6 [label="n"];
  r6 -- navlog [label=""];
}'''


if __name__ == "__main__":
    print("生成单实体ER图...")
    for filename, info in entities.items():
        dot = entity_er(info["name"], info["attrs"], info["pk"])
        save(f"{filename}.png", kroki_png(dot))

    print("生成总ER图...")
    save("er-summary.png", kroki_png(summary_dot))
    print("完成！")
