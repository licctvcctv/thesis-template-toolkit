import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# 0. 路径调试
# ==========================================
print("当前工作目录:", os.getcwd())
print("脚本所在目录:", os.path.dirname(os.path.abspath(__file__)))
print()

# ==========================================
# 1. 核心风格配置
# ==========================================
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['lines.linewidth'] = 2.5

# ==========================================
# 2. 创建画布 (1行2列布局)
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# ==========================================
# 3. 定义实验配置字典 (已修正路径)
# ==========================================
exp_configs = {
    "YOLOv8s (Baseline)": {
        "csv": "training_logs/yolov8s_baseline/results1.csv",
        "color": "#1f77b4",
        "ls": "-",
        "marker": ""
    },
    "+GhostConv": {
        "csv": "training_logs/yolov8s_ghost/results2.csv",
        "color": "#2ca02c",
        "ls": "-.",
        "marker": ""
    },
    "+Ghost+CBAM": {
        "csv": "training_logs/yolov8s_ghost_cbam/results3.csv",
        "color": "#ff7f0e",
        "ls": "--",
        "marker": ""
    },
    "Ghost+CBAM+Wise-IoU": {
        "csv": "training_logs/yolov8s_wise_iou/results4.csv",
        "color": "#d62728",
        "ls": ":",
        "marker": ""
    }
}

# ==========================================
# 4. 定义通用绘图函数
# ==========================================
def plot_metric(ax, metric_col, y_label, title, y_lim):
    for name, cfg in exp_configs.items():
        # 1. 读取数据
        try:
            df = pd.read_csv(cfg["csv"])
        except FileNotFoundError:
            print(f"警告: 找不到文件 {cfg['csv']}，跳过该模型")
            continue

        # 提取数据
        x = df["epoch"]
        y_raw = df[metric_col]  # 保留原始数据用于找最大值

        # (可选) 曲线平滑处理: 使用滑动平均让曲线更好看
        # 注意：绘图用平滑曲线，但标注最大值用原始数据！
        y_smooth = y_raw.rolling(window=5, min_periods=1).mean()

        # 2. 绘制平滑曲线
        line, = ax.plot(x, y_smooth, label=name, color=cfg["color"], 
                        linestyle=cfg["ls"], alpha=0.9)

        # 3. 寻找并标注最大值 (Best值) —— 基于原始数据！
        max_idx = y_raw.idxmax()  # 在原始数据上找最大值，确保数值准确
        max_x = x[max_idx]
        max_y = y_raw[max_idx]    # 使用原始数据的最高点

        # 绘制那个实心圆点（在原始数据的真实峰值位置）
        ax.scatter(max_x, max_y, color=cfg["color"], s=80, zorder=10, edgecolor='white', linewidth=1.5)

        # 在圆点旁边标注数值
        ax.annotate(f"{max_y:.4f}", 
                    xy=(max_x, max_y), 
                    xytext=(8, 5), 
                    textcoords='offset points',
                    color=cfg["color"], 
                    fontweight='bold', 
                    fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8, ec=cfg["color"]))

    # 4. 设置坐标轴与网格
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Epoch (训练轮次)", fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_ylim(y_lim)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(loc='lower right', frameon=True, fancybox=True, shadow=True, fontsize=9)

# ==========================================
# 5. 开始绘图
# ==========================================
plot_metric(
    ax1, 
    metric_col="metrics/mAP50(B)", 
    y_label="mAP@50", 
    title="mAP@50 性能对比",
    y_lim=(0.05, 0.42)
)

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
plt.tight_layout()
plt.savefig("result_map_comparison.png", bbox_inches="tight", dpi=300)
plt.savefig("result_map_comparison.pdf", bbox_inches="tight")

print("绘图完成！图片已保存。")
plt.show()