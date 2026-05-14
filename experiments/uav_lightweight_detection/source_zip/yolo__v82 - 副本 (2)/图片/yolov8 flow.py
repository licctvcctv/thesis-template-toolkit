from graphviz import Digraph
import os

# 初始化有向图，配置全局基础属性
dot = Digraph(
    name="YOLOv8_Network_Structure",
    format="png",
    encoding="utf-8"
)

# 确保输出目录存在
output_dir = os.path.dirname(os.path.abspath(__file__)) or "."
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 全局节点样式：矩形、填充色、SimHei字体（支持中文）
dot.attr("node", shape="box", style="filled", fontname="SimHei", fontsize="12")
# 图的排列方向：从上到下
dot.attr(rankdir="TB")
# 箭头样式
dot.attr("edge", arrowhead="normal", arrowsize="0.8")

# ====================== 1. 输入节点 ======================
dot.node("input", label="Input", fillcolor="#f8cecc")

# ====================== 2. 骨干网络（虚线框模块） ======================
with dot.subgraph(name="cluster_backbone") as backbone:
    backbone.attr(
        label="骨干网络",
        style="dashed",
        fontname="SimHei",
        fontsize="14"
    )
    # 骨干网络节点（从上到下顺序）
    backbone.node("conv1", label="Conv", fillcolor="#fff2cc")
    backbone.node("conv2", label="Conv", fillcolor="#fff2cc")
    backbone.node("c2f1", label="C2f", fillcolor="#d5e8d4")
    backbone.node("conv3", label="Conv", fillcolor="#fff2cc")
    backbone.node("c2f2", label="C2f", fillcolor="#d5e8d4")
    backbone.node("conv4", label="Conv", fillcolor="#fff2cc")
    backbone.node("c2f3", label="C2f", fillcolor="#d5e8d4")
    backbone.node("conv5", label="Conv", fillcolor="#fff2cc")
    backbone.node("c2f4", label="C2f", fillcolor="#d5e8d4")
    backbone.node("sppf", label="SPPF", fillcolor="#f8cbad")

# ====================== 3. 颈部网络（虚线框模块） ======================
with dot.subgraph(name="cluster_neck") as neck:
    neck.attr(
        label="颈部网络",
        style="dashed",
        fontname="SimHei",
        fontsize="14"
    )
    # 颈部网络节点
    neck.node("upsample1", label="Upsample", fillcolor="#ffe6cc")
    neck.node("concat1", label="Concat", fillcolor="#e1d5e7")
    neck.node("c2f5", label="C2f", fillcolor="#d5e8d4")
    neck.node("upsample2", label="Upsample", fillcolor="#ffe6cc")
    neck.node("concat2", label="Concat", fillcolor="#e1d5e7")
    neck.node("c2f6", label="C2f", fillcolor="#d5e8d4")
    neck.node("conv6", label="Conv", fillcolor="#fff2cc")
    neck.node("concat3", label="Concat", fillcolor="#e1d5e7")
    neck.node("c2f7", label="C2f", fillcolor="#d5e8d4")
    neck.node("conv7", label="Conv", fillcolor="#fff2cc")
    neck.node("concat4", label="Concat", fillcolor="#e1d5e7")
    neck.node("c2f8", label="C2f", fillcolor="#d5e8d4")

# ====================== 4. 检测头（虚线框模块） ======================
with dot.subgraph(name="cluster_detect") as detect:
    detect.attr(
        label="检测头",
        style="dashed",
        fontname="SimHei",
        fontsize="14"
    )
    # 检测头3个输出节点
    detect.node("detect1", label="Detect", fillcolor="#b2ebf2")
    detect.node("detect2", label="Detect", fillcolor="#b2ebf2")
    detect.node("detect3", label="Detect", fillcolor="#b2ebf2")

# ====================== 5. 节点连接关系（完全匹配原图箭头） ======================
# 骨干网络串行连接
dot.edge("input", "conv1")
dot.edge("conv1", "conv2")
dot.edge("conv2", "c2f1")
dot.edge("c2f1", "conv3")
dot.edge("conv3", "c2f2")
dot.edge("c2f2", "conv4")
dot.edge("conv4", "c2f3")
dot.edge("c2f3", "conv5")
dot.edge("conv5", "c2f4")
dot.edge("c2f4", "sppf")

# 上采样+特征融合路径
dot.edge("sppf", "upsample1")
dot.edge("upsample1", "concat1")
dot.edge("c2f3", "concat1")  # 骨干跳连
dot.edge("concat1", "c2f5")
dot.edge("c2f5", "upsample2")
dot.edge("upsample2", "concat2")
dot.edge("c2f2", "concat2")  # 骨干跳连
dot.edge("concat2", "c2f6")

# 检测头连接
dot.edge("c2f6", "detect1")

# 下采样+特征融合路径
dot.edge("c2f6", "conv6")
dot.edge("conv6", "concat3")
dot.edge("c2f5", "concat3")  # 跨层跳连
dot.edge("concat3", "c2f7")
dot.edge("c2f7", "detect2")

dot.edge("c2f7", "conv7")
dot.edge("conv7", "concat4")
dot.edge("sppf", "concat4")  # 底层跳连
dot.edge("concat4", "c2f8")
dot.edge("c2f8", "detect3")

# ====================== 6. 同级节点对齐（和原图布局一致） ======================
with dot.subgraph() as rank1:
    rank1.attr(rank="same")
    rank1.node("c2f6")
    rank1.node("detect1")

with dot.subgraph() as rank2:
    rank2.attr(rank="same")
    rank2.node("c2f7")
    rank2.node("detect2")

with dot.subgraph() as rank3:
    rank3.attr(rank="same")
    rank3.node("c2f8")
    rank3.node("detect3")

# 渲染生成图片：指定完整输出路径避免权限和路径问题
output_path = os.path.join(output_dir, "YOLOv8_Network_Structure")
dot.render(output_path, cleanup=True)
print(f"框图已生成，文件名为：{output_path}.png")