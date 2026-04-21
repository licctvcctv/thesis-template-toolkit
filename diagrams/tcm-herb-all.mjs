import { createRuntime, parseArgs } from './runtime.mjs';

/* ====== 模型总体框架图 ====== */
function buildModelFramework(R) {
  const { rect, brace, text, vLine, hLine, writeDiagram, BOLD, STROKE, snap } = R;
  const body = [];
  const frameX = 40, frameY = 40, frameW = 1600, frameH = 1300;
  const bandX = 260, bandW = 1240, labelX = 170;

  const roundedBox = (x, y, w, h, label, opts = {}) =>
    rect(x, y, w, h, label, { rounded: true, size: opts.size || 22, minSize: opts.minSize || 12, family: opts.family || BOLD, weight: '400', strokeWidth: 2.6, preserveLines: opts.preserveLines || false, maxLines: opts.maxLines || Infinity });
  const band = (y, h) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandW}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, h, inset = 12) =>
    body.push(brace(labelX, y + inset, y + h - inset, label, { size: 22, lineHeight: 25, family: BOLD }));
  const placeCenteredRow = (items, y, h, opts = {}) => {
    const pad = opts.padding ?? 32;
    const available = bandW - pad * 2;
    const widths = items.map(it => (typeof it === 'string' ? opts.width || 150 : it.width || opts.width || 150));
    const totalW = widths.reduce((s, w) => s + w, 0);
    const gap = opts.gap ?? Math.max(opts.minGap ?? 18, items.length > 1 ? (available - totalW) / (items.length - 1) : 0);
    const usedW = totalW + gap * Math.max(0, items.length - 1);
    let cx = bandX + pad + Math.max(0, (available - usedW) / 2);
    items.forEach((it) => {
      const spec = typeof it === 'string' ? { label: it, width: opts.width || 150 } : it;
      body.push(roundedBox(cx, y, spec.width || opts.width || 150, h, spec.label, { size: spec.size || opts.size || 22, minSize: spec.minSize || opts.minSize || 12, preserveLines: spec.preserveLines ?? false, maxLines: spec.maxLines || Infinity }));
      cx += (spec.width || opts.width || 150) + gap;
    });
  };

  // Frame
  body.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  body.push(`<rect x="${frameX}" y="105" width="${frameW}" height="96" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`);
  body.push(text(840, 152, '中药方剂推荐模型总体框架', { size: 36, family: BOLD, weight: '700' }));

  // 5 bands
  body.push(band(240, 110));   // 输入层
  body.push(band(390, 110));   // 图构建层
  body.push(band(540, 220));   // 图表示学习层
  body.push(band(800, 110));   // 症状集成层
  body.push(band(950, 260));   // 评分与输出层

  braceBand('输入层', 240, 110);
  braceBand('图构建层', 390, 110);
  braceBand('图表示学习层', 540, 220, 10);
  braceBand('症状集成层', 800, 110);
  braceBand('评分与输出层', 950, 260, 14);

  // 输入层
  placeCenteredRow([
    { label: ['处方数据集', '33765条处方'], width: 280, preserveLines: true, maxLines: 2 },
    { label: ['中药知识图谱', '9152味中药×7类关系'], width: 320, preserveLines: true, maxLines: 2 },
    { label: ['中药属性特征', '805味×27维独热编码'], width: 320, preserveLines: true, maxLines: 2 },
  ], 256, 78, { size: 20, padding: 40, minGap: 40, preserveLines: true, maxLines: 2 });

  // 图构建层
  placeCenteredRow([
    { label: ['症状-中药二部图', '1195节点 × 79870边'], width: 300, preserveLines: true, maxLines: 2 },
    { label: ['症状-症状共现图', '390节点 × 2546边'], width: 300, preserveLines: true, maxLines: 2 },
    { label: ['中药-中药共现图', '805节点 × 9038边'], width: 300, preserveLines: true, maxLines: 2 },
  ], 406, 78, { size: 19, padding: 40, minGap: 40, preserveLines: true, maxLines: 2 });

  // 图表示学习层
  placeCenteredRow([
    { label: ['GCN', '均值聚合+残差'], width: 220, preserveLines: true, maxLines: 2 },
    { label: ['GAT', '4头注意力聚合'], width: 220, preserveLines: true, maxLines: 2 },
    { label: ['Graph Transformer', '全局自注意力'], width: 240, preserveLines: true, maxLines: 2 },
    { label: ['Graph Mamba', '选择性状态空间'], width: 240, preserveLines: true, maxLines: 2 },
  ], 570, 72, { size: 18, padding: 30, minGap: 20, preserveLines: true, maxLines: 2 });
  placeCenteredRow([
    { label: ['信息融合', 'SH症状侧 + SS → 症状表示'], width: 400, preserveLines: true, maxLines: 2 },
    { label: ['信息融合', 'SH中药侧 + HH + KG → 中药表示'], width: 440, preserveLines: true, maxLines: 2 },
  ], 680, 62, { size: 17, padding: 60, minGap: 60, preserveLines: true, maxLines: 2 });

  // 症状集成层
  placeCenteredRow([
    { label: ['症状集成 (SI)', '处方矩阵 × 症状表示 → 加权均值 → MLP + BN + ReLU'], width: 800, preserveLines: true, maxLines: 2 },
  ], 822, 66, { size: 20, padding: 180, preserveLines: true, maxLines: 2 });

  // 评分与输出层
  placeCenteredRow([
    { label: ['内积评分', '处方表示 · 中药表示ᵀ → 805维分数'], width: 420, preserveLines: true, maxLines: 2 },
    { label: ['BCEWithLogitsLoss', '二元交叉熵损失'], width: 320, preserveLines: true, maxLines: 2 },
  ], 980, 66, { size: 19, padding: 80, minGap: 100, preserveLines: true, maxLines: 2 });
  placeCenteredRow([
    { label: ['Top-K推荐输出', 'P@5 / P@10 / P@20'], width: 320, preserveLines: true, maxLines: 2 },
    { label: ['Adam优化器', 'lr=3e-4, wd=7e-3, StepLR'], width: 340, preserveLines: true, maxLines: 2 },
  ], 1090, 66, { size: 18, padding: 160, minGap: 80, preserveLines: true, maxLines: 2 });

  // Arrows between bands (vertical center lines)
  const cx = bandX + bandW / 2;
  body.push(vLine(cx, 240 + 110, 390, { arrow: true }));
  body.push(vLine(cx, 390 + 110, 540, { arrow: true }));
  body.push(vLine(cx, 540 + 220, 800, { arrow: true }));
  body.push(vLine(cx, 800 + 110, 950, { arrow: true }));

  writeDiagram('tcm-model-framework', 1700, 1380, body);
}


/* ====== GCN消息传递示意图 ====== */
function buildGcnDiagram(R) {
  const { rect, text, vLine, hLine, pathLine, writeDiagram, BOLD, FONT, STROKE, snap } = R;
  const body = [];
  const W = 1600, H = 1100;

  // Title
  body.push(text(W / 2, 40, 'GCN 两层消息传递与残差融合', { size: 30, family: BOLD, weight: '700' }));

  // ---- Left column: SH graph path ----
  const lx = 120, lw = 400;
  const rowH = 70, gapY = 26;
  const rows = [
    { y: 100, label: '共享嵌入 E (1195×64)' },
    { y: 100 + rowH + gapY, label: '第1层 GCN_SH: 均值聚合' },
    { y: 100 + (rowH + gapY) * 2, label: '第2层 GCN_SH: 均值聚合' },
    { y: 100 + (rowH + gapY) * 3, label: '残差: (E₀+E₁+E₂)/3' },
    { y: 100 + (rowH + gapY) * 4, label: 'MLP + BN + Tanh' },
  ];

  body.push(text(lx + lw / 2, rows[0].y - 10, '症状-中药二部图路径', { size: 18, family: BOLD }));
  rows.forEach((r, i) => {
    const fill = i === 3 ? '#eee' : '#fff';
    body.push(`<rect x="${lx}" y="${snap(r.y)}" width="${lw}" height="${rowH}" rx="10" fill="${fill}" stroke="${STROKE}" stroke-width="2"/>`);
    body.push(text(lx + lw / 2, r.y + rowH / 2, r.label, { size: 17, family: BOLD }));
    if (i < rows.length - 1) body.push(vLine(lx + lw / 2, r.y + rowH, rows[i + 1].y, { arrow: true }));
  });
  // Residual dashed
  body.push(pathLine([[lx + lw, rows[0].y + rowH / 2], [lx + lw + 30, rows[0].y + rowH / 2], [lx + lw + 30, rows[3].y + rowH / 2], [lx + lw, rows[3].y + rowH / 2]], { width: 1.6, dash: '6,4' }));
  body.push(pathLine([[lx + lw, rows[1].y + rowH / 2], [lx + lw + 18, rows[1].y + rowH / 2], [lx + lw + 18, rows[3].y + rowH / 2]], { width: 1.6, dash: '6,4' }));

  // ---- Middle column: SS graph path ----
  const mx = 600, mw = 340;
  const mRows = [
    { y: 100, label: '嵌入 (390×64)' },
    { y: 100 + rowH + gapY, label: 'GCN_SS: 求和聚合' },
    { y: 100 + (rowH + gapY) * 2, label: '症状辅助表示 (390×256)' },
  ];
  body.push(text(mx + mw / 2, mRows[0].y - 10, '症状共现图路径', { size: 18, family: BOLD }));
  mRows.forEach((r, i) => {
    body.push(`<rect x="${mx}" y="${snap(r.y)}" width="${mw}" height="${rowH}" rx="10" fill="#fff" stroke="${STROKE}" stroke-width="2"/>`);
    body.push(text(mx + mw / 2, r.y + rowH / 2, r.label, { size: 17, family: BOLD }));
    if (i < mRows.length - 1) body.push(vLine(mx + mw / 2, r.y + rowH, mRows[i + 1].y, { arrow: true }));
  });

  // ---- Right column: HH graph path ----
  const rx = 1020, rw = 440;
  const rRows = [
    { y: 100, label: '嵌入 (805×64) + KG (805×27)' },
    { y: 100 + rowH + gapY, label: 'GCN_HH: 求和聚合 (输入91维)' },
    { y: 100 + (rowH + gapY) * 2, label: '中药辅助表示 (805×256)' },
  ];
  body.push(text(rx + rw / 2, rRows[0].y - 10, '中药共现图路径', { size: 18, family: BOLD }));
  rRows.forEach((r, i) => {
    body.push(`<rect x="${rx}" y="${snap(r.y)}" width="${rw}" height="${rowH}" rx="10" fill="#fff" stroke="${STROKE}" stroke-width="2"/>`);
    body.push(text(rx + rw / 2, r.y + rowH / 2, r.label, { size: 17, family: BOLD }));
    if (i < rRows.length - 1) body.push(vLine(rx + rw / 2, r.y + rowH, rRows[i + 1].y, { arrow: true }));
  });

  // ---- Fusion row ----
  const fuseY = 560;
  body.push(`<rect x="120" y="${fuseY}" width="600" height="70" rx="10" fill="#eee" stroke="${STROKE}" stroke-width="2.4"/>`);
  body.push(text(420, fuseY + 35, '症状表示 = SH症状侧 + SS辅助', { size: 19, family: BOLD }));
  body.push(`<rect x="820" y="${fuseY}" width="640" height="70" rx="10" fill="#eee" stroke="${STROKE}" stroke-width="2.4"/>`);
  body.push(text(1140, fuseY + 35, '中药表示 = SH中药侧 + HH辅助', { size: 19, family: BOLD }));

  // Arrows to fusion
  body.push(vLine(lx + lw / 2, rows[4].y + rowH, fuseY, { arrow: true }));
  body.push(vLine(mx + mw / 2, mRows[2].y + rowH, fuseY, { arrow: true }));
  body.push(vLine(rx + rw / 2, rRows[2].y + rowH, fuseY, { arrow: true }));
  // SH right side also feeds fusion right
  body.push(pathLine([[lx + lw / 2 + 80, rows[4].y + rowH], [lx + lw / 2 + 80, fuseY - 10], [1140, fuseY - 10], [1140, fuseY]], { width: 1.6, arrow: true }));

  // ---- SI + Score row ----
  const siY = 700;
  body.push(`<rect x="200" y="${siY}" width="500" height="70" rx="10" fill="#fff" stroke="${STROKE}" stroke-width="2.4"/>`);
  body.push(text(450, siY + 35, '症状集成 (SI): 加权均值 → MLP → BN → ReLU', { size: 17, family: BOLD }));
  body.push(vLine(420, fuseY + 70, siY, { arrow: true }));

  body.push(`<rect x="800" y="${siY}" width="500" height="70" rx="10" fill="#fff" stroke="${STROKE}" stroke-width="2.4"/>`);
  body.push(text(1050, siY + 35, '内积评分: 处方表示 · 中药表示ᵀ → Top-K', { size: 17, family: BOLD }));
  body.push(hLine(700, 800, siY + 35, { arrow: true }));
  body.push(vLine(1140, fuseY + 70, siY, { arrow: true }));

  writeDiagram('tcm-gcn-process', W, 820, body);
}


/* ====== GAT注意力机制示意图 ====== */
function buildGatDiagram(R) {
  const { rect, text, pathLine, writeDiagram, BOLD, STROKE, snap } = R;
  const body = [];

  body.push(text(600, 40, 'GAT 多头注意力聚合机制', { size: 30, family: BOLD, weight: '700' }));

  // Center node
  body.push(`<circle cx="600" cy="400" r="50" fill="#eee" stroke="${STROKE}" stroke-width="3"/>`);
  body.push(text(600, 400, '目标节点 v', { size: 18, family: BOLD }));

  // Neighbor nodes
  const neighbors = [
    { cx: 200, cy: 200, label: '邻居 u₁' },
    { cx: 200, cy: 600, label: '邻居 u₂' },
    { cx: 600, cy: 120, label: '邻居 u₃' },
    { cx: 1000, cy: 200, label: '邻居 u₄' },
    { cx: 1000, cy: 600, label: '邻居 u₅' },
  ];

  neighbors.forEach(n => {
    body.push(`<circle cx="${n.cx}" cy="${n.cy}" r="40" fill="#f5f5f5" stroke="${STROKE}" stroke-width="2"/>`);
    body.push(text(n.cx, n.cy, n.label, { size: 16, family: BOLD }));
    // Arrow to center
    const dx = 600 - n.cx, dy = 400 - n.cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const sx = n.cx + dx / dist * 40;
    const sy = n.cy + dy / dist * 40;
    const ex = 600 - dx / dist * 50;
    const ey = 400 - dy / dist * 50;
    body.push(pathLine([[sx, sy], [ex, ey]], { width: 2, arrow: true }));
  });

  // Attention weights labels
  body.push(text(380, 260, 'α₁=0.35', { size: 16, family: BOLD }));
  body.push(text(380, 540, 'α₂=0.10', { size: 16, family: BOLD }));
  body.push(text(600, 230, 'α₃=0.25', { size: 16, family: BOLD }));
  body.push(text(820, 260, 'α₄=0.20', { size: 16, family: BOLD }));
  body.push(text(820, 540, 'α₅=0.10', { size: 16, family: BOLD }));

  // Formula
  body.push(text(600, 720, 'h\'ᵥ = σ( Σᵤ αᵥᵤ · W · hᵤ )', { size: 24, family: BOLD }));
  body.push(text(600, 770, '注意力系数 αᵥᵤ = softmax( LeakyReLU( aᵀ · [Whᵥ ∥ Whᵤ] ) )', { size: 18 }));
  body.push(text(600, 820, '多头注意力: 4个头独立计算后拼接 → 输出维度不变', { size: 18 }));

  writeDiagram('tcm-gat-attention', 1200, 860, body);
}


async function main() {
  const args = parseArgs();
  const R = createRuntime(args);
  buildModelFramework(R);
  buildGcnDiagram(R);
  buildGatDiagram(R);
  console.log('tcm-herb diagrams done.');
}

main();
