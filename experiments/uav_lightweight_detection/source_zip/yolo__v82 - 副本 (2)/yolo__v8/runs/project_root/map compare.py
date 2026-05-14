import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. 数据配置区（修改这里的数值即可）
# ==========================================
# 模型名称
models = ["YOLOv8s", "+Ghost", "+Ghost+CBAM", "+Wise-IoU (完整)"]

# 指标名称
metrics = ["mAP@50", "mAP@50-95", "Precision", "Recall"]

# 数据矩阵：4个模型 × 4个指标
# 行：模型，列：指标
data = np.array([
    # mAP@50   mAP@50-95  Precision  Recall
    [0.4132,   0.2433,     0.5289,    0.3963],   # YOLOv8s
    [0.3782,   0.2177,     0.4723,    0.3784],   # +Ghost
    [0.3814,   0.2217,     0.4853,    0.3791],   # +Ghost+CBAM
    [0.3867,   0.2273,     0.4937,    0.3867],   # +Wise-IoU
])

# 颜色配置（与图片一致）
colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]

# ==========================================
# 2. 绘图配置
# ==========================================
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(10, 6))

# 柱状图参数
n_metrics = len(metrics)
n_models = len(models)
bar_width = 0.18
x = np.arange(n_metrics)

# 绘制每个模型的柱子
for i in range(n_models):
    offset = (i - n_models/2 + 0.5) * bar_width
    bars = ax.bar(x + offset, data[i], width=bar_width, 
                   color=colors[i], label=models[i], edgecolor='white', linewidth=0.5)
    
    # 在柱子上方标注数值
    for bar, val in zip(bars, data[i]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{val:.4f}', ha='center', va='bottom', fontsize=8, 
                color=colors[i], fontweight='bold')

# ==========================================
# 3. 图表美化
# ==========================================
ax.set_ylabel('指标值', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=11)
ax.set_ylim(0, 0.62)
ax.legend(loc='upper right', frameon=True, fontsize=9)
ax.grid(axis='y', linestyle='--', alpha=0.3)

# 添加虚线参考线
for y in [0.2, 0.4, 0.6]:
    ax.axhline(y=y, color='gray', linestyle=':', alpha=0.3, linewidth=0.8)

plt.tight_layout()
plt.savefig("model_comparison_bar.png", bbox_inches="tight", dpi=300)
plt.savefig("model_comparison_bar.pdf", bbox_inches="tight")
plt.show()