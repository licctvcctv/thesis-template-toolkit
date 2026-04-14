"""
生成第3章所需的图表：
1. 数据集样本展示（每类1张眼底图拼网格）
2. 数据预处理流程展示（原图 + 4步处理合一张）
3. 数据集类别分布图（饼图+柱状图组合）
"""
import os
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import cv2

rcParams['font.sans-serif'] = ['Songti SC', 'SimSun', 'SimHei', 'PingFang SC']
rcParams['axes.unicode_minus'] = False

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, 'images')
DATASET = '/tmp/odir_dataset/ODIR-5K'
TRAIN_DIR = os.path.join(DATASET, 'Training Images')

df = pd.read_excel(os.path.join(DATASET, 'data.xlsx'))
CLASSES_CN = ['正常', '糖尿病视网膜病变', '青光眼', '白内障', '年龄相关黄斑变性', '高血压', '近视', '其他']
CLASSES_EN = ['N', 'D', 'G', 'C', 'A', 'H', 'M', 'O']

np.random.seed(42)


def find_sample_for_class(cls_en, exclude_ids=set()):
    """找到该类别标签为1且其他类别尽量为0的样本"""
    mask = df[cls_en] == 1
    # 尽量找单标签样本
    other_cols = [c for c in CLASSES_EN if c != cls_en]
    single = mask & (df[other_cols].sum(axis=1) == 0)
    candidates = df[single] if single.sum() > 0 else df[mask]
    candidates = candidates[~candidates['ID'].isin(exclude_ids)]
    if len(candidates) == 0:
        candidates = df[mask]
    row = candidates.sample(1).iloc[0]
    # 优先用左眼
    img_name = row['Left-Fundus']
    img_path = os.path.join(TRAIN_DIR, img_name)
    if not os.path.exists(img_path):
        img_name = row['Right-Fundus']
        img_path = os.path.join(TRAIN_DIR, img_name)
    return img_path, row['ID']


# ===== 图1: 数据集样本展示 (2行4列, 每类一张) =====
def gen_dataset_samples():
    fig, axes = plt.subplots(2, 4, figsize=(14, 7.5))
    used_ids = set()
    for i, (cn, en) in enumerate(zip(CLASSES_CN, CLASSES_EN)):
        r, c = i // 4, i % 4
        img_path, pid = find_sample_for_class(en, used_ids)
        used_ids.add(pid)
        img = Image.open(img_path).convert('RGB').resize((300, 300))
        axes[r][c].imshow(np.array(img))
        axes[r][c].set_title(cn, fontsize=14, fontweight='bold')
        axes[r][c].axis('off')
    plt.suptitle('ODIR-5K数据集各类别眼底图像样本', fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = os.path.join(IMG_DIR, 'fig_dataset_samples.png')
    plt.savefig(out, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'  生成: fig_dataset_samples.png')


# ===== 图2: 数据预处理流程 (1行5列: 原图→灰度→去噪→均衡→归一化) =====
def gen_preprocess_demo():
    # 用正常类的一张图做演示
    img_path, _ = find_sample_for_class('N')
    img_pil = Image.open(img_path).convert('RGB').resize((224, 224))
    img_np = np.array(img_pil)

    # OpenCV处理
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(denoised)
    # 归一化到0-1
    normalized = equalized.astype(np.float32) / 255.0
    mean, std = 0.485, 0.229
    normalized = (normalized - mean) / std
    # 映射回可视化范围
    norm_vis = ((normalized - normalized.min()) / (normalized.max() - normalized.min()) * 255).astype(np.uint8)

    stages = [
        ('原始图像', img_np, True),
        ('灰度化', gray, False),
        ('高斯去噪', denoised, False),
        ('直方图均衡化', equalized, False),
        ('归一化', norm_vis, False),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(16, 3.5))
    for idx, (title, img, is_color) in enumerate(stages):
        if is_color:
            axes[idx].imshow(img)
        else:
            axes[idx].imshow(img, cmap='gray')
        axes[idx].set_title(title, fontsize=13, fontweight='bold')
        axes[idx].axis('off')
        # 画箭头连线
        if idx < 4:
            fig.text((idx + 1) / 5 - 0.015, 0.5, '→', fontsize=28, ha='center', va='center',
                     transform=fig.transFigure, color='#333')

    plt.suptitle('眼底图像预处理流程', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'fig_preprocess_pipeline.png')
    plt.savefig(out, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'  生成: fig_preprocess_pipeline.png')


# ===== 图3: 数据增强效果 (2行4列展示增强变换) =====
def gen_augmentation_demo():
    from PIL import ImageEnhance, ImageFilter
    img_path, _ = find_sample_for_class('D')
    img_pil = Image.open(img_path).convert('RGB').resize((224, 224))

    # 用PIL实现增强效果
    flipped = img_pil.transpose(Image.FLIP_LEFT_RIGHT)
    rotated = img_pil.rotate(12, fillcolor=(0, 0, 0))
    bright = ImageEnhance.Brightness(img_pil).enhance(1.3)
    contrast = ImageEnhance.Contrast(img_pil).enhance(1.3)
    rot_flip = flipped.rotate(10, fillcolor=(0, 0, 0))
    bright_contrast = ImageEnhance.Contrast(ImageEnhance.Brightness(img_pil).enhance(1.2)).enhance(1.2)
    combined = ImageEnhance.Contrast(ImageEnhance.Brightness(flipped.rotate(8, fillcolor=(0,0,0))).enhance(1.15)).enhance(1.15)

    augments = [
        ('原始图像', img_pil),
        ('水平翻转', flipped),
        ('随机旋转(15°)', rotated),
        ('亮度调节', bright),
        ('对比度调节', contrast),
        ('旋转+翻转', rot_flip),
        ('亮度+对比度', bright_contrast),
        ('综合增强', combined),
    ]

    fig, axes = plt.subplots(2, 4, figsize=(14, 7.5))
    for i, (title, img) in enumerate(augments):
        r, c = i // 4, i % 4
        axes[r][c].imshow(np.array(img))
        axes[r][c].set_title(title, fontsize=13, fontweight='bold')
        axes[r][c].axis('off')
    plt.suptitle('数据增强效果展示', fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = os.path.join(IMG_DIR, 'fig_augmentation_demo.png')
    plt.savefig(out, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'  生成: fig_augmentation_demo.png')


# ===== 图4: 数据集类别分布 (水平柱状图 + 饼图) =====
def gen_distribution():
    counts = [2436, 2280, 398, 392, 266, 218, 332, 1882]
    total = sum(counts)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={'width_ratios': [1.2, 1]})

    # 柱状图
    colors = ['#4C72B0', '#4C72B0', '#DD8452', '#DD8452', '#DD8452', '#C44E52', '#DD8452', '#4C72B0']
    y_pos = np.arange(len(CLASSES_CN))
    bars = ax1.barh(y_pos, counts, color=colors, edgecolor='white', height=0.6)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(CLASSES_CN, fontsize=12)
    ax1.set_xlabel('样本数量', fontsize=12)
    ax1.set_title('各类别样本数量', fontsize=14, fontweight='bold')
    ax1.invert_yaxis()
    for bar, count in zip(bars, counts):
        ax1.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                f'{count} ({count/total*100:.1f}%)', va='center', fontsize=10)
    ax1.set_xlim(0, max(counts) * 1.25)

    # 饼图
    # 合并小类
    pie_labels = ['正常', 'DR', '其他', '青光眼', '白内障', 'AMD', '高血压', '近视']
    pie_counts = counts
    pie_colors = ['#4C72B0', '#55A868', '#8172B2', '#DD8452', '#C44E52', '#937860', '#DA8BC3', '#8C8C8C']
    wedges, texts, autotexts = ax2.pie(pie_counts, labels=pie_labels, autopct='%1.1f%%',
                                        colors=pie_colors, startangle=90, textprops={'fontsize': 10})
    ax2.set_title('类别占比分布', fontsize=14, fontweight='bold')

    plt.suptitle('ODIR-5K数据集类别分布', fontsize=16, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(IMG_DIR, 'fig_data_distribution.png')
    plt.savefig(out, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'  生成: fig_data_distribution.png')


gen_dataset_samples()
gen_preprocess_demo()
gen_augmentation_demo()
gen_distribution()
print('\n第3章图表生成完毕。')
