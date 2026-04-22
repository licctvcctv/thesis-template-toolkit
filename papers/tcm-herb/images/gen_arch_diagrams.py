#!/usr/bin/env python3
"""Generate 4 model architecture diagrams for TCM thesis."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Font setup for Chinese
plt.rcParams['font.sans-serif'] = ['Heiti TC', 'SimHei', 'PingFang SC', 'STHeiti', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# Color palette
C_BLUE = '#D6EAF8'       # light blue
C_BLUE_D = '#AED6F1'     # darker blue
C_GREEN = '#D5F5E3'      # light green
C_GREEN_D = '#ABEBC6'    # darker green
C_ORANGE = '#FDEBD0'     # light orange
C_ORANGE_D = '#F5CBA7'   # darker orange
C_PURPLE = '#E8DAEF'     # light purple
C_PURPLE_D = '#D2B4DE'   # darker purple
C_GRAY = '#F2F3F4'       # light gray
C_YELLOW = '#FEF9E7'     # light yellow
C_YELLOW_D = '#F9E79F'
C_RED_L = '#FDEDEC'
C_RED_D = '#F5B7B1'
C_EDGE = '#566573'       # dark gray for edges
C_ARROW = '#7F8C8D'      # gray arrows
C_TEXT = '#2C3E50'        # dark text


def rounded_box(ax, x, y, w, h, text, facecolor, edgecolor=C_EDGE, fontsize=9,
                fontweight='normal', text_color=C_TEXT, lw=1.0, zorder=2):
    """Draw a rounded rectangle box with centered text."""
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.05",
                         facecolor=facecolor, edgecolor=edgecolor,
                         linewidth=lw, zorder=zorder)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            fontweight=fontweight, color=text_color, zorder=zorder+1)
    return box


def arrow(ax, x1, y1, x2, y2, color=C_ARROW, lw=1.2, style='->', zorder=1):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw),
                zorder=zorder)


def bracket_text(ax, x, y, text, fontsize=7, color='#7F8C8D'):
    """Draw small annotation text."""
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            color=color, style='italic', zorder=3)


# ============================================================
# 1. GCN Architecture
# ============================================================
def draw_gcn():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.33), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # --- Input layer ---
    rounded_box(ax, 2, 6.3, 1.8, 0.45, '症状节点特征', C_BLUE, fontsize=9, fontweight='bold')
    rounded_box(ax, 5, 6.3, 1.8, 0.45, '中药节点特征', C_GREEN, fontsize=9, fontweight='bold')
    rounded_box(ax, 8, 6.3, 1.8, 0.45, 'KG特征增强', C_ORANGE, fontsize=9, fontweight='bold')

    # Arrow from KG to herb
    arrow(ax, 8, 6.05, 5.95, 6.05)

    # --- Three branches ---
    # Branch labels
    bw = 2.2
    bh = 0.4
    by_top = 5.4

    # Left branch: 症状-中药图 (2-layer GCN)
    rounded_box(ax, 2, by_top, bw, bh, '症状-中药二部图', C_BLUE_D, fontsize=8, fontweight='bold')
    arrow(ax, 2, 6.05, 2, by_top + bh/2)
    arrow(ax, 5, 6.05, 2.6, by_top + bh/2)

    # GCN layers for left branch
    ly = 4.7
    for i, label in enumerate(['GCN层1: 聚合→线性变换→Tanh', 'GCN层2: 聚合→线性变换→Tanh']):
        rounded_box(ax, 2, ly - i*0.55, 2.4, 0.4, label, C_BLUE, fontsize=6.5)
        if i == 0:
            arrow(ax, 2, by_top - bh/2, 2, ly + 0.2)
        else:
            arrow(ax, 2, ly - (i-1)*0.55 - 0.2, 2, ly - i*0.55 + 0.2)

    # Residual averaging
    res_y = 3.3
    rounded_box(ax, 2, res_y, 2.0, 0.35, '残差平均', C_YELLOW, fontsize=7.5)
    arrow(ax, 2, ly - 0.55 - 0.2, 2, res_y + 0.175)

    # Middle branch: 症状-症状图
    rounded_box(ax, 5, by_top, bw, bh, '症状-症状图', C_PURPLE, fontsize=8, fontweight='bold')
    arrow(ax, 2, 6.05, 4.6, by_top + bh/2)

    rounded_box(ax, 5, 4.7, 2.4, 0.4, 'GCN层: 聚合→线性变换→Tanh', C_PURPLE_D, fontsize=6.5)
    arrow(ax, 5, by_top - bh/2, 5, 4.9)

    rounded_box(ax, 5, res_y, 2.0, 0.35, '残差平均', C_YELLOW, fontsize=7.5)
    arrow(ax, 5, 4.5, 5, res_y + 0.175)

    # Right branch: 中药-中药图
    rounded_box(ax, 8, by_top, bw, bh, '中药-中药图', C_GREEN_D, fontsize=8, fontweight='bold')
    arrow(ax, 5, 6.05, 7.4, by_top + bh/2)

    rounded_box(ax, 8, 4.7, 2.4, 0.4, 'GCN层: 聚合→线性变换→Tanh', C_GREEN, fontsize=6.5)
    arrow(ax, 8, by_top - bh/2, 8, 4.9)

    rounded_box(ax, 8, res_y, 2.0, 0.35, '残差平均', C_YELLOW, fontsize=7.5)
    arrow(ax, 8, 4.5, 8, res_y + 0.175)

    # --- Fusion ---
    fusion_y = 2.4
    rounded_box(ax, 5, fusion_y, 2.8, 0.45, '特征融合(相加)', C_ORANGE_D, fontsize=9, fontweight='bold')
    arrow(ax, 2, res_y - 0.175, 4.2, fusion_y + 0.225)
    arrow(ax, 5, res_y - 0.175, 5, fusion_y + 0.225)
    arrow(ax, 8, res_y - 0.175, 5.8, fusion_y + 0.225)

    # --- Symptom Integration ---
    si_y = 1.5
    rounded_box(ax, 5, si_y, 2.8, 0.45, '症状集成', C_BLUE_D, fontsize=9, fontweight='bold')
    arrow(ax, 5, fusion_y - 0.225, 5, si_y + 0.225)

    # --- Scoring ---
    sc_y = 0.6
    rounded_box(ax, 5, sc_y, 2.8, 0.45, '评分与推荐', C_RED_L, fontsize=9, fontweight='bold')
    arrow(ax, 5, si_y - 0.225, 5, sc_y + 0.225)

    fig.tight_layout(pad=0.3)
    fig.savefig('/Users/a136/vs/45425/thesis_project/papers/tcm-herb/images/tcm-gcn-arch.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Saved tcm-gcn-arch.png")


# ============================================================
# 2. GAT Architecture
# ============================================================
def draw_gat():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.33), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # --- Input layer ---
    rounded_box(ax, 2, 6.3, 1.8, 0.45, '症状节点特征', C_BLUE, fontsize=9, fontweight='bold')
    rounded_box(ax, 5, 6.3, 1.8, 0.45, '中药节点特征', C_GREEN, fontsize=9, fontweight='bold')
    rounded_box(ax, 8, 6.3, 1.8, 0.45, 'KG特征增强', C_ORANGE, fontsize=9, fontweight='bold')

    arrow(ax, 8, 6.05, 5.95, 6.05)

    # --- Three branches ---
    bw = 2.2
    bh = 0.4
    by_top = 5.4

    # Left branch
    rounded_box(ax, 2, by_top, bw, bh, '症状-中药二部图', C_BLUE_D, fontsize=8, fontweight='bold')
    arrow(ax, 2, 6.05, 2, by_top + bh/2)
    arrow(ax, 5, 6.05, 2.6, by_top + bh/2)

    ly = 4.7
    for i, label in enumerate(['GAT层1: 多头注意力(4头)→Tanh', 'GAT层2: 多头注意力(4头)→Tanh']):
        rounded_box(ax, 2, ly - i*0.55, 2.5, 0.4, label, C_BLUE, fontsize=6)
        if i == 0:
            arrow(ax, 2, by_top - bh/2, 2, ly + 0.2)
        else:
            arrow(ax, 2, ly - (i-1)*0.55 - 0.2, 2, ly - i*0.55 + 0.2)

    # Attention detail annotation
    bracket_text(ax, 2, 3.7, 'a_ij = softmax(LeakyReLU(a[Wh_i||Wh_j]))', fontsize=5.5, color='#E74C3C')

    res_y = 3.3
    rounded_box(ax, 2, res_y, 2.0, 0.35, '残差 + LayerNorm', C_YELLOW, fontsize=7.5)
    arrow(ax, 2, ly - 0.55 - 0.2, 2, res_y + 0.175)

    # Middle branch
    rounded_box(ax, 5, by_top, bw, bh, '症状-症状图', C_PURPLE, fontsize=8, fontweight='bold')
    arrow(ax, 2, 6.05, 4.6, by_top + bh/2)

    rounded_box(ax, 5, 4.7, 2.5, 0.4, 'GAT层: 多头注意力(4头)→Tanh', C_PURPLE_D, fontsize=6)
    arrow(ax, 5, by_top - bh/2, 5, 4.9)

    rounded_box(ax, 5, res_y, 2.0, 0.35, '残差 + LayerNorm', C_YELLOW, fontsize=7.5)
    arrow(ax, 5, 4.5, 5, res_y + 0.175)

    # Right branch
    rounded_box(ax, 8, by_top, bw, bh, '中药-中药图', C_GREEN_D, fontsize=8, fontweight='bold')
    arrow(ax, 5, 6.05, 7.4, by_top + bh/2)

    rounded_box(ax, 8, 4.7, 2.5, 0.4, 'GAT层: 多头注意力(4头)→Tanh', C_GREEN, fontsize=6)
    arrow(ax, 8, by_top - bh/2, 8, 4.9)

    rounded_box(ax, 8, res_y, 2.0, 0.35, '残差 + LayerNorm', C_YELLOW, fontsize=7.5)
    arrow(ax, 8, 4.5, 8, res_y + 0.175)

    # --- Fusion ---
    fusion_y = 2.4
    rounded_box(ax, 5, fusion_y, 2.8, 0.45, '特征融合(相加)', C_ORANGE_D, fontsize=9, fontweight='bold')
    arrow(ax, 2, res_y - 0.175, 4.2, fusion_y + 0.225)
    arrow(ax, 5, res_y - 0.175, 5, fusion_y + 0.225)
    arrow(ax, 8, res_y - 0.175, 5.8, fusion_y + 0.225)

    si_y = 1.5
    rounded_box(ax, 5, si_y, 2.8, 0.45, '症状集成', C_BLUE_D, fontsize=9, fontweight='bold')
    arrow(ax, 5, fusion_y - 0.225, 5, si_y + 0.225)

    sc_y = 0.6
    rounded_box(ax, 5, sc_y, 2.8, 0.45, '评分与推荐', C_RED_L, fontsize=9, fontweight='bold')
    arrow(ax, 5, si_y - 0.225, 5, sc_y + 0.225)

    fig.tight_layout(pad=0.3)
    fig.savefig('/Users/a136/vs/45425/thesis_project/papers/tcm-herb/images/tcm-gat-arch.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Saved tcm-gat-arch.png")


# ============================================================
# 3. Graph Transformer Architecture
# ============================================================
def draw_gt():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.33), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Input
    rounded_box(ax, 5, 7.0, 3.5, 0.45, '节点序列输入 (1195个节点, d=64)', C_GRAY, fontsize=9, fontweight='bold')

    # Transformer block label
    # Draw a dashed rectangle around the transformer layers
    block_rect = FancyBboxPatch((1.2, 2.6), 7.6, 3.9,
                                boxstyle="round,pad=0.1",
                                facecolor='#FAFAFA', edgecolor='#BDC3C7',
                                linewidth=1.2, linestyle='--', zorder=0)
    ax.add_patch(block_rect)
    ax.text(8.5, 6.35, '×2层', fontsize=9, fontweight='bold', color='#E74C3C',
            ha='center', va='center', zorder=3)

    arrow(ax, 5, 6.75, 5, 6.35)

    # Multi-Head Self-Attention
    mhsa_y = 5.9
    rounded_box(ax, 5, mhsa_y, 4.5, 0.5, '多头自注意力 (Multi-Head Self-Attention, 4头)', C_BLUE_D, fontsize=8, fontweight='bold')

    # Q, K, V detail
    qkv_y = 5.2
    rounded_box(ax, 2.5, qkv_y, 1.5, 0.35, 'Q = XWQ', C_BLUE, fontsize=7)
    rounded_box(ax, 5, qkv_y, 1.5, 0.35, 'K = XWK', C_BLUE, fontsize=7)
    rounded_box(ax, 7.5, qkv_y, 1.5, 0.35, 'V = XWV', C_BLUE, fontsize=7)
    arrow(ax, 5, mhsa_y - 0.25, 2.5, qkv_y + 0.175)
    arrow(ax, 5, mhsa_y - 0.25, 5, qkv_y + 0.175)
    arrow(ax, 5, mhsa_y - 0.25, 7.5, qkv_y + 0.175)

    # Attention computation
    att_y = 4.55
    rounded_box(ax, 5, att_y, 5.0, 0.35, 'Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V', C_YELLOW, fontsize=7.5)
    arrow(ax, 2.5, qkv_y - 0.175, 3.5, att_y + 0.175)
    arrow(ax, 5, qkv_y - 0.175, 5, att_y + 0.175)
    arrow(ax, 7.5, qkv_y - 0.175, 6.5, att_y + 0.175)

    # Add & Norm 1
    an1_y = 3.9
    rounded_box(ax, 5, an1_y, 3.0, 0.35, 'Add & LayerNorm', C_GREEN, fontsize=8)
    arrow(ax, 5, att_y - 0.175, 5, an1_y + 0.175)

    # FFN
    ffn_y = 3.25
    rounded_box(ax, 5, ffn_y, 4.5, 0.35, 'FFN: Linear(64→256) → GELU → Linear(256→64)', C_ORANGE, fontsize=7.5)
    arrow(ax, 5, an1_y - 0.175, 5, ffn_y + 0.175)

    # Add & Norm 2
    an2_y = 2.75
    rounded_box(ax, 5, an2_y, 3.0, 0.35, 'Add & LayerNorm', C_GREEN, fontsize=8)
    arrow(ax, 5, ffn_y - 0.175, 5, an2_y + 0.175)

    # Residual connections (curved arrows on the side)
    # Residual 1: from input to Add&Norm1
    ax.annotate('', xy=(3.2, an1_y), xytext=(3.2, mhsa_y),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=1.0,
                                connectionstyle='arc3,rad=0.3', linestyle='--'))
    ax.text(1.7, (an1_y + mhsa_y)/2, '残差', fontsize=6, color='#E74C3C', ha='center')

    # Residual 2: from Add&Norm1 to Add&Norm2
    ax.annotate('', xy=(3.2, an2_y), xytext=(3.2, an1_y),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=1.0,
                                connectionstyle='arc3,rad=0.3', linestyle='--'))
    ax.text(1.7, (an2_y + an1_y)/2, '残差', fontsize=6, color='#E74C3C', ha='center')

    # Output projection
    proj_y = 2.1
    rounded_box(ax, 5, proj_y, 3.5, 0.35, '线性投影 (64→256)', C_PURPLE, fontsize=8)
    arrow(ax, 5, an2_y - 0.175, 5, proj_y + 0.175)

    # Fusion -> SI -> Scoring
    fusion_y = 1.4
    rounded_box(ax, 5, fusion_y, 2.8, 0.4, '特征融合 → 症状集成', C_BLUE_D, fontsize=8, fontweight='bold')
    arrow(ax, 5, proj_y - 0.175, 5, fusion_y + 0.2)

    sc_y = 0.7
    rounded_box(ax, 5, sc_y, 2.8, 0.4, '评分与推荐', C_RED_L, fontsize=9, fontweight='bold')
    arrow(ax, 5, fusion_y - 0.2, 5, sc_y + 0.2)

    fig.tight_layout(pad=0.3)
    fig.savefig('/Users/a136/vs/45425/thesis_project/papers/tcm-herb/images/tcm-gt-arch.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Saved tcm-gt-arch.png")


# ============================================================
# 4. Graph Mamba Architecture
# ============================================================
def draw_mamba():
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.33), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Input
    rounded_box(ax, 5, 7.0, 3.5, 0.45, '节点序列输入 (1195个节点, d=64)', C_GRAY, fontsize=9, fontweight='bold')

    # Mamba block outline
    block_rect = FancyBboxPatch((0.8, 1.95), 8.4, 4.65,
                                boxstyle="round,pad=0.1",
                                facecolor='#FAFAFA', edgecolor='#BDC3C7',
                                linewidth=1.2, linestyle='--', zorder=0)
    ax.add_patch(block_rect)
    ax.text(8.8, 6.4, '×2层', fontsize=9, fontweight='bold', color='#E74C3C',
            ha='center', va='center', zorder=3)

    arrow(ax, 5, 6.75, 5, 6.35)

    # Linear expansion (2x)
    lin_y = 5.95
    rounded_box(ax, 5, lin_y, 4.0, 0.4, '线性扩展 Linear(64→128)', C_ORANGE, fontsize=8, fontweight='bold')

    # Split into two branches
    split_y = 5.35
    ax.text(5, split_y + 0.2, '分支', fontsize=7, color=C_ARROW, ha='center')

    # SSM branch (left)
    ssm_x = 3.2
    rounded_box(ax, ssm_x, split_y, 2.8, 0.4, 'SSM分支 (状态空间模型)', C_BLUE_D, fontsize=7.5, fontweight='bold')
    arrow(ax, 4.0, lin_y - 0.2, ssm_x, split_y + 0.2)

    # SSM detail
    ssm_d1_y = 4.6
    rounded_box(ax, ssm_x, ssm_d1_y, 3.0, 0.4, '离散化: Ā=exp(Δ·A), B̄=Δ·B', C_BLUE, fontsize=6.5)
    arrow(ax, ssm_x, split_y - 0.2, ssm_x, ssm_d1_y + 0.2)

    ssm_d2_y = 3.95
    rounded_box(ax, ssm_x, ssm_d2_y, 3.0, 0.4, 'h(t)=A*h(t-1)+B*x(t), y(t)=C*h(t)', C_BLUE, fontsize=6.5)
    arrow(ax, ssm_x, ssm_d1_y - 0.2, ssm_x, ssm_d2_y + 0.2)

    # SSM parameters annotation
    ssm_p_y = 3.3
    rounded_box(ax, ssm_x, ssm_p_y, 2.6, 0.4, 'A: 64x16  B,C: 16  dt: 64', C_YELLOW, fontsize=6.5)
    arrow(ax, ssm_x, ssm_d2_y - 0.2, ssm_x, ssm_p_y + 0.2)
    bracket_text(ax, ssm_x, 2.95, '状态维度 N=16', fontsize=6, color='#E74C3C')

    # Gate branch (right)
    gate_x = 7.2
    rounded_box(ax, gate_x, split_y, 2.0, 0.4, '门控分支', C_GREEN_D, fontsize=8, fontweight='bold')
    arrow(ax, 6.0, lin_y - 0.2, gate_x, split_y + 0.2)

    rounded_box(ax, gate_x, 4.6, 2.0, 0.4, 'SiLU激活', C_GREEN, fontsize=8)
    arrow(ax, gate_x, split_y - 0.2, gate_x, 4.8)

    # Element-wise multiply
    mul_y = 3.3
    rounded_box(ax, gate_x, mul_y, 2.0, 0.4, '逐元素相乘 ⊙', C_PURPLE, fontsize=7.5, fontweight='bold')
    arrow(ax, gate_x, 4.4, gate_x, mul_y + 0.2)

    # Arrow from SSM to multiply
    arrow(ax, ssm_x + 1.3, ssm_p_y, gate_x - 1.0, mul_y)

    # Output projection
    out_y = 2.55
    rounded_box(ax, 5, out_y, 3.5, 0.4, '输出投影 Linear(64→64)', C_ORANGE, fontsize=8)
    arrow(ax, gate_x, mul_y - 0.2, 5.8, out_y + 0.2)

    # Add & Norm
    an_y = 2.05
    rounded_box(ax, 5, an_y, 3.0, 0.35, 'Add & LayerNorm', C_GREEN, fontsize=8)
    arrow(ax, 5, out_y - 0.2, 5, an_y + 0.175)

    # Residual
    ax.annotate('', xy=(1.6, an_y), xytext=(1.6, lin_y),
                arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=1.0,
                                connectionstyle='arc3,rad=0.35', linestyle='--'))
    ax.text(0.7, (an_y + lin_y)/2, '残差', fontsize=6, color='#E74C3C', ha='center')

    # Bottom: fusion -> SI -> scoring
    fusion_y = 1.3
    rounded_box(ax, 5, fusion_y, 2.8, 0.4, '特征融合 → 症状集成', C_BLUE_D, fontsize=8, fontweight='bold')
    arrow(ax, 5, an_y - 0.175, 5, fusion_y + 0.2)

    sc_y = 0.6
    rounded_box(ax, 5, sc_y, 2.8, 0.4, '评分与推荐', C_RED_L, fontsize=9, fontweight='bold')
    arrow(ax, 5, fusion_y - 0.2, 5, sc_y + 0.2)

    fig.tight_layout(pad=0.3)
    fig.savefig('/Users/a136/vs/45425/thesis_project/papers/tcm-herb/images/tcm-mamba-arch.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Saved tcm-mamba-arch.png")


if __name__ == '__main__':
    draw_gcn()
    draw_gat()
    draw_gt()
    draw_mamba()
    print("\nAll 4 diagrams generated successfully!")
