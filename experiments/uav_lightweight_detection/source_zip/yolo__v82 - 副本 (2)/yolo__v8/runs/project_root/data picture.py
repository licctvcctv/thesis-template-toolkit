import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm

# ========== 1. 设置中文字体（Windows 环境） ==========
# 优先尝试 Windows 常见中文字体
chinese_fonts = ['SimHei', 'SimSun', 'Microsoft YaHei', 'KaiTi', 'FangSong']
font_found = False

for font_name in chinese_fonts:
    try:
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        font_found = True
        print(f"使用字体: {font_name}")
        break
    except:
        continue

if not font_found:
    # 手动指定字体文件路径（备用方案）
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
        'C:/Windows/Fonts/msyh.ttc',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            plt.rcParams['font.family'] = fm.FontProperties(fname=fp).get_name()
            plt.rcParams['axes.unicode_minus'] = False
            print(f"使用字体文件: {fp}")
            break

# ========== 2. 准备数据（来自你第一张图） ==========
categories = ['pedestrian', 'people', 'bicycle', 'car', 'van', 
              'truck', 'tricycle', 'awning-tricycle', 'bus', 'motor']
instances = [79335, 27059, 10480, 144866, 24956, 
             12875, 4812, 3246, 6926, 29646]

# 颜色（尽量还原你第一张图）
colors = ['#0000CD', '#00CED1', '#7FFF00', '#00FA9A', '#191970', 
          '#FF69B4', '#FF0000', '#FFFF00', '#32CD32', '#9400D3']

# ========== 3. 创建画布 ==========
fig, axes = plt.subplots(2, 2, figsize=(14, 11))
plt.subplots_adjust(hspace=0.38, wspace=0.30)  # 调整间距，防止标题重叠

# ========== 4. 辅助函数：添加子图标题 ==========
def add_subplot_title(ax, title_text, y_offset=-0.16, fontsize=13):
    """在子图正下方添加 (a) xxx 格式的标题"""
    ax.text(0.5, y_offset, title_text, transform=ax.transAxes,
            fontsize=fontsize, ha='center', va='top', fontweight='normal')

# ========== 5. 绘制 4 张子图 ==========

# --- (a) 训练集类别分类（左上）---
ax = axes[0, 0]
bars = ax.bar(range(len(categories)), instances, color=colors, width=0.6)
ax.set_ylabel('instances', fontsize=12)
ax.set_xticks(range(len(categories)))
ax.set_xticklabels(categories, rotation=90, fontsize=10)
ax.set_ylim(0, 160000)
ax.tick_params(axis='y', labelsize=10)

# 在柱子上方标注数值
for bar, val in zip(bars, instances):
    height = bar.get_height()
    ax.annotate(f'{int(val)}', 
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4), textcoords="offset points", 
                ha='center', va='bottom', fontsize=9, rotation=0)

add_subplot_title(ax, '(a) 训练集类别分类')

# --- (b) 先验框尺寸（右上）---
ax = axes[0, 1]
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')  # 不需要坐标轴

# 绘制同心矩形框（模拟先验框）
box_colors = ['#FF69B4', '#DA70D6', '#BA55D3', '#9370DB', 
              '#8A2BE2', '#7B68EE', '#6A5ACD', '#483D8B']
for i in range(8):
    wh = 0.06 * (i + 1)
    rect = Rectangle((0.5 - wh/2, 0.5 - wh/2), wh, wh, 
                     fill=False, edgecolor=box_colors[i], 
                     linewidth=1.8, alpha=0.7 - i*0.05)
    ax.add_patch(rect)

add_subplot_title(ax, '(b) 先验框尺寸')

# --- (c) 预测框位置（左下）---
ax = axes[1, 0]
# 生成模拟的 x-y 分布数据（中心偏下，符合你的图）
np.random.seed(42)
x = np.random.normal(0.42, 0.18, 8000)
y = np.random.normal(0.38, 0.16, 8000)
# 截断到 [0,1] 范围内
x = np.clip(x, 0, 1)
y = np.clip(y, 0, 1)

hist = ax.hist2d(x, y, bins=60, cmap='Blues', alpha=0.9, cmin=1)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.tick_params(labelsize=10)

add_subplot_title(ax, '(c) 预测框位置')

# --- (d) 目标宽高分布（右下）---
ax = axes[1, 1]
np.random.seed(123)
# 模拟宽高数据（小目标居多，符合你的图特征）
w = np.random.exponential(0.06, 4000)
h = np.random.exponential(0.06, 4000)
# 截断
w = np.clip(w, 0, 0.6)
h = np.clip(h, 0, 0.6)

ax.scatter(w, h, s=8, c='#6495ED', alpha=0.35, edgecolors='none')
ax.set_xlabel('width', fontsize=12)
ax.set_ylabel('height', fontsize=12)
ax.set_xlim(0, 0.6)
ax.set_ylim(0, 0.6)
ax.tick_params(labelsize=10)

add_subplot_title(ax, '(d) 目标宽高分布')

# ========== 6. 保存到本地 ==========
# 修改为你本地的实际路径
save_path = 'E:/yolo__v82/figure_with_titles.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f"图片已保存到: {save_path}")
plt.show()