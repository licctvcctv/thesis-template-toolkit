"""批量生成单实体ER图 + 总ER图，通过 Kroki API。"""
import requests
import os
import zlib
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")

def kroki_url(dot_src, fmt="png", engine="graphviz"):
    """生成 Kroki URL"""
    compressed = zlib.compress(dot_src.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return f"https://kroki.io/{engine}/{fmt}/{encoded}"

def save_diagram(dot_src, filename, engine="graphviz"):
    url = kroki_url(dot_src, "png", engine)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    path = os.path.join(IMG_DIR, filename)
    with open(path, "wb") as f:
        f.write(resp.content)
    print(f"  ✓ {filename} ({len(resp.content)//1024}KB)")

# ---- 单实体 ER 图模板 ----
def entity_er(entity_name, attrs, pk_attrs=None):
    """生成单实体 ER 图的 DOT 代码"""
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
    # 按圆形分布属性
    import math
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


# ---- 各实体定义 ----
entities = {
    "er-user": {
        "name": "用户",
        "attrs": ["用户编号", "用户名", "密码", "真实姓名", "手机号", "身份证号", "余额", "状态", "用户类型"],
        "pk": ["用户编号"]
    },
    "er-machine": {
        "name": "机器",
        "attrs": ["机器编号", "机器名称", "机器类型", "所属区域", "行号", "列号", "状态", "配置"],
        "pk": ["机器编号"]
    },
    "er-reservation": {
        "name": "预约记录",
        "attrs": ["预约编号", "用户ID", "机器ID", "开始时间", "结束时间", "预约状态"],
        "pk": ["预约编号"]
    },
    "er-session": {
        "name": "上机记录",
        "attrs": ["记录编号", "用户ID", "机器ID", "预约ID", "开始时间", "结束时间", "使用时长", "消费金额", "会话状态"],
        "pk": ["记录编号"]
    },
    "er-transaction": {
        "name": "交易记录",
        "attrs": ["交易编号", "用户ID", "交易类型", "金额", "交易后余额", "备注", "关联业务ID"],
        "pk": ["交易编号"]
    },
    "er-price": {
        "name": "费率配置",
        "attrs": ["配置编号", "费率名称", "开始时间", "结束时间", "单价", "机器类型", "优先级"],
        "pk": ["配置编号"]
    },
    "er-notice": {
        "name": "公告",
        "attrs": ["公告编号", "标题", "内容", "公告类型", "发布状态", "发布人"],
        "pk": ["公告编号"]
    }
}

# ---- 总 ER 图（只有实体和关系，无属性）----
summary_dot = '''graph {
  layout=neato;
  overlap=false;
  sep="+10";
  node [fontname="SimSun", fontsize=13];
  edge [fontname="SimSun", fontsize=10, len=2.5];

  /* 第一行：交易记录 -- 用户 -- 机器 */
  trans    [shape=box, style=bold, label="交易记录", pos="-3,4!"];
  user     [shape=box, style=bold, label="用户",     pos="3,5!"];
  machine  [shape=box, style=bold, label="机器",     pos="9,5!"];

  /* 第二行：公告 -- 预约记录 -- 上机记录 */
  notice   [shape=box, style=bold, label="公告",     pos="-1,1!"];
  reserv   [shape=box, style=bold, label="预约记录", pos="5,1!"];
  session  [shape=box, style=bold, label="上机记录", pos="9,1!"];

  /* 第三行：费率配置 */
  price    [shape=box, style=bold, label="费率配置", pos="9,-2!"];

  /* 关系节点 */
  r3 [shape=diamond, label="产生", pos="0,4.5!"];
  r2 [shape=diamond, label="使用", pos="6,5!"];
  r6 [shape=diamond, label="发布", pos="0,3!"];
  r1 [shape=diamond, label="预约", pos="4,3!"];
  r4 [shape=diamond, label="分配", pos="9,3!"];
  r7 [shape=diamond, label="关联", pos="7,1!"];
  r5 [shape=diamond, label="适用", pos="9,-0.5!"];

  /* 用户四条线分别朝不同方向，互不交叉 */
  user -- r3 [label="1"];
  r3 -- trans [label="n"];
  user -- r2 [label="1"];
  r2 -- machine [label="n"];
  user -- r6 [label="1"];
  r6 -- notice [label="n"];
  user -- r1 [label="1"];
  r1 -- reserv [label="n"];

  /* 机器→上机记录 垂直向下 */
  machine -- r4 [label="1"];
  r4 -- session [label="n"];

  /* 预约记录→上机记录 水平 */
  reserv -- r7 [label="1"];
  r7 -- session [label="1"];

  /* 上机记录→费率配置 垂直向下 */
  session -- r5 [label="n"];
  r5 -- price [label="1"];
}'''

if __name__ == "__main__":
    print("生成单实体ER图...")
    for filename, info in entities.items():
        dot = entity_er(info["name"], info["attrs"], info["pk"])
        save_diagram(dot, f"{filename}.png")

    print("生成总ER图...")
    save_diagram(summary_dot, "er-summary.png")
    print("全部完成！")
