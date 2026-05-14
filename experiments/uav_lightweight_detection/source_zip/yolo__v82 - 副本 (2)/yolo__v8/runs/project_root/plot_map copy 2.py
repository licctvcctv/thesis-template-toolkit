import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ==========================================
# 1. 核心风格配置 (根据你的需求修改这里)
# ==========================================
# 设置图片清晰度 (DPI)，期刊论文一般要求 300-600
plt.rcParams['figure.dpi'] = 300

# 设置字体大小
plt.rcParams['font.size'] = 12

# 解决中文显示问题 (非常重要！)
# Windows系统通常用 'SimHei' 或 'Microsoft YaHei'
# Mac系统通常用 'Arial Unicode MS' 或 'Heiti TC'
# Linux系统需要安装中文字体后指定
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示为方块的问题

# 设置线条默认宽度
plt.rcParams['lines.linewidth'] = 2.5

# ==========================================
# 2. 创建画布 (1行2列布局)
# ==========================================
# figsize 控制图片的宽高比，单位是英寸
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
# ==========================================
# 3. 定义实验配置字典
# ==========================================
# 结构说明:
# "显示在图例上的名字": {
#     "csv": "文件路径",
#     "color": "线条颜色 (支持英文单词或Hex颜色码)",
#     "ls": "线条样式 (- 实线, -- 虚线, -. 点划线, : 点线)",
#     "marker": "标记点 (可选, 比如 'o', 's', '^')"
# }

exp_configs = {
    "YOLOv8s (Baseline)": {
        "csv": "training_logs/yolov8s_baseline/results.csv",
        "color": "#1f77b4", # 经典蓝
        "ls": "-",
        "marker": ""
    },
    "+GhostConv": {
        "csv": "training_logs/yolov8s_ghost/results.csv",
        "color": "#2ca02c", # 生机绿
        "ls": "-.",
        "marker": ""
    },
    "+Ghost+CBAM": {
        "csv": "training_logs/yolov8s_ghost_cbam/results.csv",
        "color": "#ff7f0e", # 活力橙
        "ls": "--",
        "marker": ""
    },
    "+Wise-IoU": {
        "csv": "training_logs/yolov8s_wise_iou/results.csv",
        "color": "#d62728", # 中国红
        "ls": ":",
        "marker": ""
    }
}
# ==========================================
# 4. 定义通用绘图函数
# ==========================================
def plot_metric(ax, metric_col, y_label, title, y_lim):
    """
    ax: 子图对象 (ax1 或 ax2)
    metric_col: CSV里对应的列名
    y_label: Y轴显示的文字
    title: 子图标题
    y_lim: Y轴范围 (最小值, 最大值)
    """
    
    for name, cfg in exp_configs.items():
        # 1. 读取数据
        try:
            df = pd.read_csv(cfg["csv"])
        except FileNotFoundError:
            print(f"警告: 找不到文件 {cfg['csv']}，跳过该模型")
            continue

        # 提取数据
        x = df["epoch"]
        y = df[metric_col]
        
        # (可选进阶) 曲线平滑处理: 使用滑动平均让曲线更好看
        # window=5 表示每5个点取一次平均，可根据需要调整
    y = y.rolling(window=5, min_periods=1).mean()

        # 2. 绘制曲线
        line, = ax.plot(x, y, label=name, color=cfg["color"], 
                        linestyle=cfg["ls"], alpha=0.9)

        # 3. 寻找并标注最大值 (Best值)
        max_idx = y.idxmax() # 找到最大值对应的索引
        max_x = x[max_idx]
        max_y = y[max_idx]
        
        # 绘制那个实心圆点
        ax.scatter(max_x, max_y, color=cfg["color"], s=80, zorder=10, edgecolor='white', linewidth=1.5)
        
        # 在圆点旁边标注数值
        # xytext=(10, 5) 表示文字在点的右上方偏移10,5像素
        ax.annotate(f"{max_y:.4f}", 
                    xy=(max_x, max_y), 
                    xytext=(8, 5), 
                    textcoords='offset points',
                    color=cfg["color"], 
                    fontweight='bold', 
                    fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8, ec=cfg["color"])) # 加个白色背景框更清晰

    # 4. 设置坐标轴与网格
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Epoch (训练轮次)", fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_ylim(y_lim)
    ax.grid(True, linestyle='--', alpha=0.3) # 网格线设为虚线
    ax.legend(loc='lower right', frameon=True, fancybox=True, shadow=True, fontsize=9) # 图例样式
    # ==========================================
# 5. 开始绘图
# ==========================================

# 左图: mAP@50
# 注意: 列名必须和你的CSV里的表头完全一致！
# YOLOv8 通常是 "metrics/mAP50(B)"
# YOLOv5 通常是 "metrics/mAP_0.5"
plot_metric(
    ax1, 
    metric_col="metrics/mAP50(B)", 
    y_label="mAP@50", 
    title="mAP@50 性能对比",
    y_lim=(0.05, 0.42) # 根据你的实际数据范围调整
)

# 右图: mAP@50-95
plot_metric(
    ax2, 
    metric_col="metrics/mAP50-95(B)", 
    y_label="mAP@50-95", 
    title="mAP@50-95 性能对比",
    y_lim=(0.02, 0.26)
)

# ==========================================
# 6. 调整布局并保存
# ==========================================
# tight_layout() 自动调整子图间距，防止标题重叠
plt.tight_layout()

# 保存图片
# bbox_inches="tight" 防止图例被切掉
# 建议保存为 PNG (用于Word) 或 PDF (用于LaTeX论文)
plt.savefig("result_map_comparison.png", bbox_inches="tight", dpi=300)
plt.savefig("result_map_comparison.pdf", bbox_inches="tight")

print("绘图完成！图片已保存。")

# 显示图片
plt.show()