"""生成Flask CMS论文图表（参考网吧项目风格）"""
import math
import os
import zlib
import base64
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")


def kroki_png(source, engine="graphviz"):
    compressed = zlib.compress(source.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    url = f"https://kroki.io/{engine}/png/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def save(filename, data):
    path = os.path.join(IMG_DIR, filename)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  ✓ {filename} ({len(data)//1024}KB)")


# ============================================================
# 1. 系统架构图（横向分层 + 左侧花括号标签，参考网吧风格）
# ============================================================
def gen_system_arch():
    """参考网吧架构图：纵向分层，每层一个大框，左侧竖排标签"""
    dot = r'''digraph {
  graph [rankdir=TB, fontname="SimHei", fontsize=13, dpi=150,
         splines=false, nodesep=0.5, ranksep=0.6, compound=true,
         label="企业官网CMS系统架构图", labelloc=t, labelfontsize=16];
  node [fontname="SimSun", fontsize=11, shape=box, style="rounded",
        height=0.45, fixedsize=false];
  edge [style=invis];

  /* ---- 客户端 ---- */
  subgraph cluster_client {
    label="客\n户\n端"; labelloc=l; labeljust=l; fontsize=13;
    style=bold; margin=16;
    c1 [label="浏览器（PC / 移动端）", width=4.0];
  }

  /* ---- 表现层 ---- */
  subgraph cluster_pres {
    label="表\n现\n层"; labelloc=l; labeljust=l; fontsize=13;
    style=bold; margin=16;
    p1 [label="Bootstrap 5\n响应式页面", width=2.0];
    p2 [label="Jinja2\n模板引擎", width=2.0];
    p3 [label="自定义CSS", width=1.6];
    p1 -> p2 -> p3 [style=invis];
  }

  /* ---- 业务逻辑层 ---- */
  subgraph cluster_biz {
    label="服\n务\n应\n用\n层"; labelloc=l; labeljust=l; fontsize=13;
    style=bold; margin=16;

    b1 [label="用户认证"]; b2 [label="文章管理"];
    b3 [label="栏目管理"]; b4 [label="单页管理"];
    b5 [label="媒体管理"];

    b1 -> b2 -> b3 -> b4 -> b5 [style=invis];

    b6 [label="Flask-Login\n会话管理"]; b7 [label="Flask-WTF\n表单/CSRF"];
    b8 [label="用户管理"]; b9 [label="留言管理"];
    b10 [label="站点设置"];

    b6 -> b7 -> b8 -> b9 -> b10 [style=invis];

    {rank=same; b1; b2; b3; b4; b5}
    {rank=same; b6; b7; b8; b9; b10}
  }

  /* ---- 数据层 ---- */
  subgraph cluster_data {
    label="数\n据\n层"; labelloc=l; labeljust=l; fontsize=13;
    style=bold; margin=16;
    d1 [label="用户表"]; d2 [label="角色表"];
    d3 [label="文章表"]; d4 [label="栏目表"];
    d5 [label="单页表"]; d6 [label="媒体表"];
    d7 [label="设置表"]; d8 [label="留言表"];

    d1 -> d2 -> d3 -> d4 -> d5 -> d6 -> d7 -> d8 [style=invis];
    {rank=same; d1; d2; d3; d4; d5; d6; d7; d8}
  }

  /* ---- 运行环境 ---- */
  subgraph cluster_env {
    label="运\n行\n环\n境"; labelloc=l; labeljust=l; fontsize=13;
    style=bold; margin=16;
    e1 [label="Python 3.10+"]; e2 [label="Flask 3.0"];
    e3 [label="Bootstrap 5.3"]; e4 [label="SQLite"];
    e5 [label="pytest"];

    e1 -> e2 -> e3 -> e4 -> e5 [style=invis];
    {rank=same; e1; e2; e3; e4; e5}
  }

  /* 层间连接（不可见，仅控制布局） */
  c1 -> p1 [lhead=cluster_pres];
  p2 -> b1 [lhead=cluster_biz];
  b2 -> d1 [lhead=cluster_data];
  d1 -> e1 [lhead=cluster_env];
}'''
    save("system_architecture.png", kroki_png(dot))


# ============================================================
# 2. 功能结构图（树形结构，参考网吧风格）
# ============================================================
def gen_function_structure():
    """参考网吧功能结构图：紧凑树形，叶子节点竖排"""
    dot = '''graph {
  layout=neato;
  overlap=false;
  sep="+5";
  size="14,10!";
  dpi=150;
  node [fontname="SimSun", fontsize=12, shape=box, style=bold];

  root [label="企业官网CMS系统", width=3.0, height=0.6, pos="7,9!"];

  /* 三个子系统 */
  front [label="前台展示模块", width=2.2, height=0.6, pos="2,7!"];
  auth  [label="用户认证模块", width=2.2, height=0.6, pos="7,7!"];
  admin [label="后台管理模块", width=2.2, height=0.6, pos="12,7!"];

  root -- front;
  root -- auth;
  root -- admin;

  /* 前台叶子 */
  f1 [label="首页\\n展示", width=0.9, height=1.0, pos="0,4.5!"];
  f2 [label="文章\\n详情", width=0.9, height=1.0, pos="1.2,4.5!"];
  f3 [label="栏目\\n浏览", width=0.9, height=1.0, pos="2.4,4.5!"];
  f4 [label="全文\\n搜索", width=0.9, height=1.0, pos="3.6,4.5!"];
  f5 [label="联系\\n表单", width=0.9, height=1.0, pos="4.8,4.5!"];
  front -- f1; front -- f2; front -- f3; front -- f4; front -- f5;

  /* 认证叶子 */
  a1 [label="用户\\n登录", width=0.9, height=1.0, pos="5.8,4.5!"];
  a2 [label="用户\\n登出", width=0.9, height=1.0, pos="7,4.5!"];
  a3 [label="权限\\n验证", width=0.9, height=1.0, pos="8.2,4.5!"];
  auth -- a1; auth -- a2; auth -- a3;

  /* 后台叶子 */
  m1 [label="文章\\n管理", width=0.9, height=1.0, pos="9.4,4.5!"];
  m2 [label="栏目\\n管理", width=0.9, height=1.0, pos="10.6,4.5!"];
  m3 [label="单页\\n管理", width=0.9, height=1.0, pos="11.8,4.5!"];
  m4 [label="媒体\\n管理", width=0.9, height=1.0, pos="13,4.5!"];
  m5 [label="用户\\n管理", width=0.9, height=1.0, pos="14.2,4.5!"];
  m6 [label="留言\\n管理", width=0.9, height=1.0, pos="15.4,4.5!"];
  m7 [label="站点\\n设置", width=0.9, height=1.0, pos="16.6,4.5!"];
  admin -- m1; admin -- m2; admin -- m3; admin -- m4;
  admin -- m5; admin -- m6; admin -- m7;
}'''
    save("function_structure.png", kroki_png(dot))


# ============================================================
# 3. 用例图 - 管理员（椭圆散射风格，参考网吧）
# ============================================================
def gen_usecase_admin():
    dot = '''graph {
  layout=neato;
  overlap=false;
  sep="+8";
  node [fontname="SimSun", fontsize=13];
  edge [len=2.2];

  admin [shape=box, label="管理员", style=bold, pos="0,0!",
         width=1.2, height=0.6];

  uc1 [shape=ellipse, label="文章管理", pos="-3.5,2.5!"];
  uc2 [shape=ellipse, label="栏目管理", pos="-2,3.5!"];
  uc3 [shape=ellipse, label="用户管理", pos="2,3.5!"];
  uc4 [shape=ellipse, label="媒体管理", pos="3.5,2.5!"];
  uc5 [shape=ellipse, label="单页管理", pos="-3.5,-2.5!"];
  uc6 [shape=ellipse, label="留言管理", pos="-2,-3.5!"];
  uc7 [shape=ellipse, label="站点设置", pos="2,-3.5!"];
  uc8 [shape=ellipse, label="仪表盘",   pos="3.5,-2.5!"];

  admin -- uc1;
  admin -- uc2;
  admin -- uc3;
  admin -- uc4;
  admin -- uc5;
  admin -- uc6;
  admin -- uc7;
  admin -- uc8;
}'''
    save("usecase_admin.png", kroki_png(dot))


# ============================================================
# 4. 用例图 - 访客
# ============================================================
def gen_usecase_visitor():
    dot = '''graph {
  layout=neato;
  overlap=false;
  sep="+8";
  node [fontname="SimSun", fontsize=13];
  edge [len=2.2];

  visitor [shape=box, label="访客", style=bold, pos="0,0!",
           width=1.0, height=0.6];

  uc1 [shape=ellipse, label="浏览首页",   pos="-3,2!"];
  uc2 [shape=ellipse, label="查看文章",   pos="0,3!"];
  uc3 [shape=ellipse, label="栏目浏览",   pos="3,2!"];
  uc4 [shape=ellipse, label="全文搜索",   pos="-3,-2!"];
  uc5 [shape=ellipse, label="提交留言",   pos="0,-3!"];
  uc6 [shape=ellipse, label="查看单页",   pos="3,-2!"];

  visitor -- uc1;
  visitor -- uc2;
  visitor -- uc3;
  visitor -- uc4;
  visitor -- uc5;
  visitor -- uc6;
}'''
    save("usecase_visitor.png", kroki_png(dot))


# ============================================================
# 5. 单实体ER图（陈氏表示法，椭圆属性围绕实体）
# ============================================================
def entity_er(name, attrs, pk_attrs=None):
    pk_attrs = pk_attrs or []
    lines = [
        'graph {',
        '  layout=neato;',
        '  overlap=false;',
        '  sep="+6";',
        '  node [fontname="SimSun", fontsize=12];',
        '  edge [len=1.5];',
        f'  entity [shape=box, style=bold, label="{name}", pos="0,0!"];',
    ]
    n = len(attrs)
    radius = 1.8
    for i, attr in enumerate(attrs):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = round(radius * math.cos(angle), 2)
        y = round(radius * math.sin(angle), 2)
        nid = f"a{i}"
        if attr in pk_attrs:
            label = f"<U>{attr}</U>"
            lines.append(f'  {nid} [shape=ellipse, label=<{label}>, pos="{x},{y}!"];')
        else:
            lines.append(f'  {nid} [shape=ellipse, label="{attr}", pos="{x},{y}!"];')
        lines.append(f'  entity -- {nid};')
    lines.append('}')
    return '\n'.join(lines)


entities = {
    "er-user": {
        "name": "用户", "pk": ["用户编号(PK)"],
        "attrs": ["用户编号(PK)", "用户名", "邮箱", "密码哈希", "状态", "角色", "最后登录"]
    },
    "er-article": {
        "name": "文章", "pk": ["文章编号(PK)"],
        "attrs": ["文章编号(PK)", "标题", "别名", "摘要", "正文", "状态",
                  "置顶", "浏览量", "栏目ID", "作者ID"]
    },
    "er-category": {
        "name": "栏目", "pk": ["栏目编号(PK)"],
        "attrs": ["栏目编号(PK)", "名称", "别名", "类型", "排序", "导航显示", "父栏目ID"]
    },
    "er-media": {
        "name": "媒体资源", "pk": ["资源编号(PK)"],
        "attrs": ["资源编号(PK)", "原始文件名", "存储文件名", "MIME类型", "文件大小", "上传者ID"]
    },
    "er-page": {
        "name": "单页", "pk": ["页面编号(PK)"],
        "attrs": ["页面编号(PK)", "标题", "别名", "内容", "状态", "导航显示"]
    },
    "er-message": {
        "name": "联系留言", "pk": ["留言编号(PK)"],
        "attrs": ["留言编号(PK)", "姓名", "邮箱", "电话", "留言内容", "处理状态"]
    },
}


# ============================================================
# 6. 总ER图（实体+关系菱形，参考网吧风格）
# ============================================================
def gen_er_summary():
    dot = '''graph {
  layout=neato;
  overlap=false;
  sep="+10";
  node [fontname="SimSun", fontsize=13];
  edge [fontname="SimSun", fontsize=10, len=2.5];

  /* 第一行 */
  role     [shape=box, style=bold, label="角色",     pos="-3,5!"];
  user     [shape=box, style=bold, label="用户",     pos="3,5!"];
  media    [shape=box, style=bold, label="媒体资源", pos="9,5!"];

  /* 第二行 */
  category [shape=box, style=bold, label="栏目",     pos="-1,1!"];
  article  [shape=box, style=bold, label="文章",     pos="5,1!"];
  page     [shape=box, style=bold, label="单页",     pos="11,1!"];

  /* 第三行 */
  setting  [shape=box, style=bold, label="站点设置", pos="1,-3!"];
  message  [shape=box, style=bold, label="联系留言", pos="7,-3!"];

  /* 关系 */
  r1 [shape=diamond, label="属于",   pos="0,5!"];
  r2 [shape=diamond, label="撰写",   pos="4,3!"];
  r3 [shape=diamond, label="上传",   pos="6,5!"];
  r4 [shape=diamond, label="归属",   pos="2,1!"];
  r5 [shape=diamond, label="父子",   pos="-1,3!"];

  role -- r1 [label="1"];
  r1 -- user [label="N"];
  user -- r2 [label="1"];
  r2 -- article [label="N"];
  user -- r3 [label="1"];
  r3 -- media [label="N"];
  category -- r4 [label="1"];
  r4 -- article [label="N"];
  category -- r5 [label="1"];
  r5 -- category [label="N"];
}'''
    save("er-diagram.png", kroki_png(dot))


# ============================================================
# 7. 业务流程图（标准流程图，参考网吧风格）
# ============================================================
def gen_business_flow():
    """传统流程图：矩形操作+菱形判断+圆角起止，参考网吧风格"""
    dot = r'''digraph {
  graph [rankdir=TB, fontname="SimSun", fontsize=12, dpi=150,
         splines=ortho, nodesep=0.5, ranksep=0.6];
  node [fontname="SimSun", fontsize=12, width=2.8, height=0.5];
  edge [fontsize=11, fontname="SimSun"];

  start [label="开始", shape=ellipse, width=1.5];
  s1  [label="访客浏览企业官网首页", shape=box];
  d1  [label="是否查看文章?", shape=diamond, width=2.5, height=0.8];
  s2  [label="选择栏目或搜索关键词", shape=box];
  s3  [label="浏览文章列表", shape=box];
  s4  [label="查看文章详情", shape=box];
  s5  [label="系统自动增加浏览量", shape=box];
  d2  [label="是否提交留言?", shape=diamond, width=2.5, height=0.8];
  s6  [label="填写联系表单", shape=box];
  s7  [label="系统验证CSRF和表单数据", shape=box];
  d3  [label="验证通过?", shape=diamond, width=2.0, height=0.7];
  s8  [label="保存留言到数据库", shape=box];
  s9  [label="显示提交成功提示", shape=box];
  s10 [label="显示错误提示", shape=box];
  d4  [label="是否为管理员?", shape=diamond, width=2.5, height=0.8];
  s11 [label="输入用户名和密码", shape=box];
  s12 [label="系统验证身份", shape=box];
  d5  [label="验证通过?", shape=diamond, width=2.0, height=0.7];
  s13 [label="进入后台管理仪表盘", shape=box];
  s14 [label="执行内容管理操作\n（文章/栏目/单页/媒体/用户/留言/设置）", shape=box, height=0.7];
  s15 [label="提示登录失败", shape=box];
  end_ [label="结束", shape=ellipse, width=1.5];

  start -> s1 -> d1;
  d1 -> s2 [label="是"];
  s2 -> s3 -> s4 -> s5;
  d1 -> d2 [label="否"];
  d2 -> s6 [label="是"];
  s6 -> s7 -> d3;
  d3 -> s8 [label="是"];
  s8 -> s9;
  d3 -> s10 [label="否"];
  d2 -> d4 [label="否"];
  s5 -> d4;
  s9 -> d4;
  s10 -> d4;
  d4 -> s11 [label="是"];
  s11 -> s12 -> d5;
  d5 -> s13 [label="是"];
  s13 -> s14 -> end_;
  d5 -> s15 [label="否"];
  s15 -> end_;
  d4 -> end_ [label="否"];
}'''
    save("business_flow.png", kroki_png(dot))


# ============================================================
# 8. 登录时序图
# ============================================================
def gen_login_sequence():
    src = r'''@startuml
skinparam monochrome true
skinparam defaultFontName SimSun
skinparam defaultFontSize 12
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam shadowing false

actor 用户
participant 浏览器
participant "Flask路由" as F
participant "WTForms" as W
participant "User模型" as U
participant "Flask-Login" as L
database "SQLite" as DB

用户 -> 浏览器 : 访问登录页面
浏览器 -> F : GET /auth/login
activate F
F --> 浏览器 : 渲染登录表单
deactivate F

用户 -> 浏览器 : 提交用户名密码
浏览器 -> F : POST /auth/login
activate F
F -> W : 表单验证+CSRF校验
activate W

alt 验证失败
  W --> F : 校验错误
  F --> 浏览器 : 返回错误提示
else 验证通过
  W --> F : 校验通过
  deactivate W
  F -> U : 查询用户记录
  activate U
  U -> DB : SELECT by username
  DB --> U : 用户记录
  U -> U : check_password_hash()

  alt 密码错误
    U --> F : 验证失败
    F --> 浏览器 : 返回错误提示
  else 密码正确
    U --> F : 验证成功
    deactivate U
    F -> L : login_user()
    activate L
    L -> DB : 更新last_login_at
    L --> F : 会话创建成功
    deactivate L
    F --> 浏览器 : 重定向到后台仪表盘
  end
end
deactivate F
@enduml'''
    save("login_sequence.png", kroki_png(src, engine="plantuml"))


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    os.makedirs(IMG_DIR, exist_ok=True)

    print("1. 系统架构图...")
    gen_system_arch()

    print("2. 功能结构图...")
    gen_function_structure()

    print("3. 管理员用例图...")
    gen_usecase_admin()

    print("4. 访客用例图...")
    gen_usecase_visitor()

    print("5. 单实体ER图...")
    for fname, info in entities.items():
        dot = entity_er(info["name"], info["attrs"], info.get("pk"))
        save(f"{fname}.png", kroki_png(dot))

    print("6. 总ER图...")
    gen_er_summary()

    print("7. 业务流程图...")
    gen_business_flow()

    print("8. 登录时序图...")
    gen_login_sequence()

    print("\n全部完成!")
