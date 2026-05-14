import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 查找可用的中文字体
available_fonts = [f.name for f in fm.fontManager.ttflist]
chinese_fonts = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'Arial Unicode MS']
for font in chinese_fonts:
    if font in available_fonts:
        plt.rcParams['font.sans-serif'] = [font]
        break

# ---------------------- 1. 替换为你的实验数据 ----------------------
model_names = [
    'YOLOv8s',
    'YOLOv8s-Ghost',
    'YOLOv8s-Ghost-CBAM',
    'YOLOv8s-Improved'
]
fps_values = [143.70, 184.30, 157.40, 165.00]
# 对应原图的配色，可自行修改
colors = ['#3388dd', '#22bb99', '#f7941d', '#e64a3e']

# ---------------------- 2. 画布与基础柱状图绘制 ----------------------
plt.figure(figsize=(10, 6), dpi=150)  # 画布大小与清晰度

bars = plt.bar(model_names, fps_values, color=colors, width=0.8)

# ---------------------- 3. 复刻原图样式细节 ----------------------
plt.title('模型对比: FPS (batch=1)', fontsize=12, fontweight='bold')
plt.ylabel('FPS (batch=1)', fontsize=10)

# Y轴刻度与范围，和原图完全对齐
plt.ylim(0, 220)
plt.yticks([0, 25, 50, 75, 100, 125, 150, 175, 200])

# 水平网格线，置于柱子下方
plt.grid(axis='y', color='lightgray', linestyle='-', linewidth=0.8)
plt.gca().set_axisbelow(True)

# 柱子顶部数值标注
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        height + 2,
        f'{height:.2f}',
        ha='center', va='bottom', fontsize=9, fontweight='medium'
    )

# X轴标签角度优化，避免重叠
plt.xticks(rotation=25, ha='right', fontsize=9)

# 隐藏上、右边框，优化美观度
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

# 自动调整布局，避免标签截断
plt.tight_layout()

# 显示图片，取消下方注释可保存300DPI高清图
plt.show()
# plt.savefig('yolov8s_fps_comparison.png', dpi=300, bbox_inches='tight')