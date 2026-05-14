const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const projectRoot = path.resolve(__dirname, '..');
const outDir = path.join(projectRoot, 'images', 'imagegen_case');

function esc(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function text(x, y, value, opts = {}) {
  const size = opts.size || 30;
  const weight = opts.weight || 400;
  const anchor = opts.anchor || 'middle';
  return `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}" dominant-baseline="middle">${esc(value)}</text>`;
}

function entity(x, y, w, h, label) {
  return `
    <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#fff" stroke="#111" stroke-width="2"/>
    ${text(x + w / 2, y + h / 2, label, { size: 32 })}
  `;
}

function diamond(cx, cy, w, h, label) {
  const points = [
    [cx, cy - h / 2],
    [cx + w / 2, cy],
    [cx, cy + h / 2],
    [cx - w / 2, cy]
  ].map(item => item.join(',')).join(' ');
  return `
    <polygon points="${points}" fill="#fff" stroke="#111" stroke-width="2"/>
    ${text(cx, cy, label, { size: label.length > 4 ? 24 : 30 })}
  `;
}

function line(x1, y1, x2, y2, opts = {}) {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#111" stroke-width="${opts.width || 2}"/>`;
}

function poly(points) {
  return `<polyline points="${points.map(p => p.join(',')).join(' ')}" fill="none" stroke="#111" stroke-width="2"/>`;
}

function relLabel(x, y, value) {
  return text(x, y, value, { size: 28, weight: 600 });
}

function buildErSvg() {
  const W = 1600;
  const H = 900;
  const e = {
    commodity: { x: 70, y: 120, w: 145, h: 60, label: '商品' },
    price: { x: 425, y: 120, w: 165, h: 60, label: '历史价格' },
    scenario: { x: 800, y: 120, w: 165, h: 60, label: '市场情景' },
    run: { x: 1265, y: 120, w: 165, h: 60, label: '运行批次' },
    agent: { x: 75, y: 410, w: 145, h: 60, label: '智能体' },
    decision: { x: 520, y: 410, w: 165, h: 60, label: '决策记录' },
    score: { x: 900, y: 410, w: 165, h: 60, label: '评分结果' },
    failure: { x: 900, y: 690, w: 165, h: 60, label: '失败样本' },
    patch: { x: 360, y: 690, w: 165, h: 60, label: '策略补丁' }
  };
  const d = {
    own: { x: 315, y: 150, label: '拥有' },
    cite: { x: 690, y: 150, label: '引用' },
    containRun: { x: 1135, y: 150, label: '包含' },
    generate: { x: 355, y: 440, label: '生成' },
    trigger: { x: 705, y: 290, label: '触发' },
    target: { x: 355, y: 290, label: '交易标的' },
    score: { x: 790, y: 440, label: '形成' },
    belong: { x: 1160, y: 440, label: '归入' },
    fail: { x: 990, y: 565, label: '沉淀' },
    repair: { x: 705, y: 720, label: '修正' },
    apply: { x: 245, y: 720, label: '应用' }
  };
  const parts = [];
  Object.values(e).forEach(item => parts.push(entity(item.x, item.y, item.w, item.h, item.label)));
  Object.values(d).forEach(item => parts.push(diamond(item.x, item.y, item.label.length > 3 ? 130 : 95, 70, item.label)));

  parts.push(line(215, 150, 267, 150), line(363, 150, 425, 150));
  parts.push(relLabel(235, 130, '1'), relLabel(400, 130, 'N'));
  parts.push(line(590, 150, 625, 150), line(755, 150, 800, 150));
  parts.push(relLabel(610, 130, 'N'), relLabel(780, 130, '1'));
  parts.push(line(965, 150, 1070, 150), line(1200, 150, 1265, 150));
  parts.push(relLabel(1010, 130, 'N'), relLabel(1235, 130, '1'));

  parts.push(line(220, 440, 307, 440), line(403, 440, 520, 440));
  parts.push(relLabel(245, 420, '1'), relLabel(492, 420, 'N'));
  parts.push(poly([[882, 180], [882, 290], [770, 290]]), poly([[640, 290], [602, 290], [602, 410]]));
  parts.push(relLabel(870, 205, '1'), relLabel(625, 385, 'N'));
  parts.push(poly([[215, 180], [215, 290], [290, 290]]), poly([[420, 290], [602, 290], [602, 410]]));
  parts.push(relLabel(230, 205, '1'), relLabel(555, 270, 'N'));
  parts.push(line(685, 440, 743, 440), line(837, 440, 900, 440));
  parts.push(relLabel(713, 420, '1'), relLabel(870, 420, '1'));
  parts.push(line(1065, 440, 1095, 440), line(1225, 440, 1348, 180));
  parts.push(relLabel(1085, 420, 'N'), relLabel(1280, 260, '1'));
  parts.push(line(982, 470, 982, 530), line(982, 600, 982, 690));
  parts.push(relLabel(1010, 505, '1'), relLabel(1010, 660, 'N'));
  parts.push(line(900, 720, 770, 720), line(640, 720, 525, 720));
  parts.push(relLabel(870, 700, 'N'), relLabel(555, 700, '1'));
  parts.push(poly([[360, 720], [292, 720]]), poly([[198, 720], [145, 720], [145, 470]]));
  parts.push(relLabel(335, 700, 'N'), relLabel(160, 500, '1'));

  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
    <rect width="${W}" height="${H}" fill="#fff"/>
    <g font-family="SimSun, Songti SC, Noto Serif CJK SC, serif" fill="#111">
      ${text(W / 2, 58, '系统总体 E-R 图', { size: 42, weight: 700 })}
      ${parts.join('\n')}
    </g>
  </svg>`;
}

function tableBox(x, y, w, title, rows) {
  const headerH = 46;
  const rowH = 30;
  const h = headerH + rows.length * rowH;
  let out = `<g>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#fff" stroke="#111" stroke-width="2"/>
    <rect x="${x}" y="${y}" width="${w}" height="${headerH}" fill="#fff" stroke="#111" stroke-width="2"/>
    ${text(x + w / 2, y + headerH / 2, title, { size: 23, weight: 600 })}
    <line x1="${x + 54}" y1="${y + headerH}" x2="${x + 54}" y2="${y + h}" stroke="#111" stroke-width="1.5"/>
    <line x1="${x + 236}" y1="${y + headerH}" x2="${x + 236}" y2="${y + h}" stroke="#111" stroke-width="1.5"/>`;
  rows.forEach((row, idx) => {
    const yy = y + headerH + idx * rowH;
    if (idx > 0) out += `<line x1="${x}" y1="${yy}" x2="${x + w}" y2="${yy}" stroke="#ddd" stroke-width="1"/>`;
    out += text(x + 27, yy + rowH / 2, row[0], { size: 18 });
    out += text(x + 68, yy + rowH / 2, row[1], { size: 19, anchor: 'start' });
    out += text(x + 250, yy + rowH / 2, row[2], { size: 18, anchor: 'start' });
  });
  out += '</g>';
  return { svg: out, h };
}

function connector(points, labelA, labelB, labelPosA, labelPosB) {
  return `${poly(points)}${relLabel(labelPosA[0], labelPosA[1], labelA)}${relLabel(labelPosB[0], labelPosB[1], labelB)}`;
}

function buildLogicSvg() {
  const W = 1700;
  const H = 1050;
  const boxes = [];
  const t = {};
  function add(key, x, y, title, rows, w = 390) {
    const box = tableBox(x, y, w, title, rows);
    boxes.push(box.svg);
    t[key] = { x, y, w, h: box.h };
  }

  add('commodities', 55, 70, 'commodities（商品表）', [
    ['PK', 'id', '商品ID'],
    ['', 'symbol', '合约代码'],
    ['', 'name', '商品名称'],
    ['', 'exchange', '交易所'],
    ['', 'unit', '计量单位']
  ], 360);
  add('run', 655, 45, 'simulation_runs（运行批次表）', [
    ['PK', 'id', '运行ID'],
    ['', 'current_round', '当前轮次'],
    ['', 'training_window', '训练区间'],
    ['', 'test_window', '测试区间'],
    ['', 'status', '运行状态'],
    ['', 'created_at', '创建时间']
  ], 420);
  add('scenarios', 1280, 70, 'market_scenarios（市场情景表）', [
    ['PK', 'id', '情景ID'],
    ['FK', 'price_point_id', '基准价格ID'],
    ['', 'date', '情景日期'],
    ['', 'regime', '市场阶段'],
    ['', 'news_json', '资讯集合'],
    ['', 'memory_json', '历史记忆']
  ], 390);
  add('prices', 55, 350, 'price_points（历史价格表）', [
    ['PK', 'id', '价格ID'],
    ['FK', 'commodity_id', '商品ID'],
    ['', 'date', '日期'],
    ['', 'open', '开盘价'],
    ['', 'high', '最高价'],
    ['', 'low', '最低价'],
    ['', 'close', '收盘价']
  ], 360);
  add('agents', 560, 345, 'agents（智能体表）', [
    ['PK', 'id', '智能体ID'],
    ['', 'role', '角色类型'],
    ['', 'style', '策略风格'],
    ['', 'commodity_bias', '偏好商品'],
    ['', 'model_chain', '模型链'],
    ['', 'exposure_scale', '风险暴露系数']
  ], 390);
  add('decisions', 1115, 335, 'decisions（决策表）', [
    ['PK', 'id', '决策ID'],
    ['FK', 'run_id', '运行ID'],
    ['FK', 'agent_id', '智能体ID'],
    ['FK', 'scenario_id', '情景ID'],
    ['FK', 'commodity_id', '商品ID'],
    ['', 'action', '买/卖/观望'],
    ['', 'confidence', '置信度'],
    ['', 'reason', '决策理由']
  ], 430);
  add('patches', 70, 720, 'strategy_patches（进化记录表）', [
    ['PK', 'id', '补丁ID'],
    ['FK', 'agent_id', '智能体ID'],
    ['FK', 'run_id', '运行ID'],
    ['FK', 'source_failure_id', '失败样本ID'],
    ['', 'season', '进化轮次'],
    ['', 'patch_note', '修正内容']
  ], 390);
  add('scores', 650, 710, 'scores（评分表）', [
    ['PK', 'id', '评分ID'],
    ['FK', 'decision_id', '决策ID'],
    ['FK', 'agent_id', '智能体ID'],
    ['', 'score_delta', '单轮收益分'],
    ['', 'equity', '累计收益'],
    ['', 'hit_rate', '胜率'],
    ['', 'max_drawdown', '最大回撤'],
    ['', 'recommendation', '采纳建议']
  ], 430);
  add('failures', 1175, 725, 'failure_cases（失败样本表）', [
    ['PK', 'id', '失败样本ID'],
    ['FK', 'decision_id', '决策ID'],
    ['FK', 'agent_id', '智能体ID'],
    ['', 'failure_type', '失败类型'],
    ['', 'score_delta', '失分值'],
    ['', 'repair_plan', '修正策略']
  ], 420);

  const lines = [];
  lines.push(connector([[235, 350], [235, 275], [235, 220]], '1', 'N', [215, 255], [255, 325]));
  lines.push(connector([[1075, 160], [1280, 160]], '1', 'N', [1105, 140], [1250, 140]));
  lines.push(connector([[950, 445], [1115, 445]], '1', 'N', [985, 425], [1085, 425]));
  lines.push(connector([[1475, 250], [1475, 335]], '1', 'N', [1498, 278], [1498, 318]));
  lines.push(connector([[415, 430], [1115, 565]], '1', 'N', [445, 410], [1088, 545]));
  lines.push(connector([[865, 225], [865, 710]], '1', 'N', [890, 260], [848, 680]));
  lines.push(connector([[1325, 575], [865, 710]], '1', '1', [1300, 610], [930, 690]));
  lines.push(connector([[1460, 575], [1460, 725]], '1', 'N', [1485, 610], [1485, 705]));
  lines.push(connector([[755, 525], [265, 720]], '1', 'N', [735, 555], [305, 700]));
  lines.push(connector([[1175, 835], [460, 835]], 'N', '1', [1145, 815], [490, 855]));

  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
    <rect width="${W}" height="${H}" fill="#fff"/>
    <g font-family="SimSun, Songti SC, Noto Serif CJK SC, serif" fill="#111">
      ${text(W / 2, 24, '数据逻辑关系图', { size: 42, weight: 700 })}
      ${lines.join('\n')}
      ${boxes.join('\n')}
    </g>
  </svg>`;
}

function html(svg) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    html,body{margin:0;background:white;}
    svg{text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased;}
  </style></head><body>${svg}</body></html>`;
}

async function render(svg, outputPath, width, height) {
  const executablePath = fs.existsSync('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    : '/Users/a136/.homebrew/bin/chromium';
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
    await page.setContent(html(svg), { waitUntil: 'load' });
    await page.screenshot({ path: outputPath, clip: { x: 0, y: 0, width, height }, animations: 'disabled' });
  } finally {
    await browser.close();
  }
}

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  await render(buildErSvg(), path.join(outDir, 'fig4-7_er_diagram.png'), 1600, 900);
  await render(buildLogicSvg(), path.join(outDir, 'fig4-8_database_logic.png'), 1700, 1050);
  console.log(path.join(outDir, 'fig4-7_er_diagram.png'));
  console.log(path.join(outDir, 'fig4-8_database_logic.png'));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
