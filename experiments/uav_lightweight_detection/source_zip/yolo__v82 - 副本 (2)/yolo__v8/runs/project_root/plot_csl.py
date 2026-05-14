import pandas as pd
import matplotlib.pyplot as plt

# -------------------------- 1. 全局配置 --------------------------
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['lines.linewidth'] = 2

# -------------------------- 2. 模型配置【完全使用你提供的正确版本】 --------------------------
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

# -------------------------- 3. 创建画布：2行3列 --------------------------
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# -------------------------- 4. 子图配置 --------------------------
plot_configs = [
    # 第一行：训练集
    (axes[0,0], "train/box_loss", "训练集 Box Loss", 0.75, 2.55),
    (axes[0,1], "train/cls_loss", "训练集 Cls Loss", 0.45, 2.15),
    (axes[0,2], "train/dfl_loss", "训练集 DFL Loss", 0.5, 1.5),
    # 第二行：验证集
    (axes[1,0], "val/box_loss", "验证集 Box Loss", 0.75, 2.2),
    (axes[1,1], "val/cls_loss", "验证集 Cls Loss", 0.55, 1.75),
    (axes[1,2], "val/dfl_loss", "验证集 DFL Loss", 0.45, 1.25)
]

# -------------------------- 5. 循环绘图 --------------------------
for idx, (ax, col_name, title, y_min, y_max) in enumerate(plot_configs):
    for model_name, cfg in exp_configs.items():
        # 读取数据
        df = pd.read_csv(cfg["csv"])
        epochs = df["epoch"]
        loss_data = df[col_name]
        
        # 绘制曲线
        ax.plot(epochs, loss_data, label=model_name,
                color=cfg["color"], linestyle=cfg["ls"])
    
    # 子图样式
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Epoch", fontsize=10)
    ax.set_ylabel("Loss", fontsize=10)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, alpha=0.3)
    
    # 只在第一个子图显示图例
    if idx == 0:
        ax.legend(fontsize=9, loc="upper right")

# -------------------------- 6. 保存并显示 --------------------------
plt.tight_layout()
plt.savefig("Loss对比曲线图.png", bbox_inches="tight")
print("Loss曲线图绘制完成！")
plt.show()