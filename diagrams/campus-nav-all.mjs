import { parseArgs, createRuntime } from './runtime.mjs';
import { buildRadialUseCase } from './radial-use-case-template.mjs';

const args = parseArgs();
const outDir = '/Users/a136/vs/45425/thesis_project/papers/campus-nav/images';
args.set('--out-dir', outDir);
args.set('--src-dir', outDir);
const R = createRuntime(args);

// ============================================================
// 1. User use case diagram
// ============================================================
buildRadialUseCase(R, 'usecase-user', '用户', [
  ['注册登录', 290, 180],
  ['地图浏览', 290, 340],
  ['视角切换', 290, 500],
  ['兴趣点搜索', 290, 660],
  ['分类筛选', 290, 820],
], [
  ['路径规划', 890, 220],
  ['步行时间估算', 890, 400],
  ['统计图表查看', 890, 580],
  ['游客浏览', 890, 760],
]);

// ============================================================
// 2. Admin use case diagram
// ============================================================
buildRadialUseCase(R, 'usecase-admin', '管理员', [
  ['管理员登录', 290, 240],
  ['用户管理', 290, 440],
  ['兴趣点管理', 290, 640],
], [
  ['公告管理', 890, 240],
  ['导航统计', 890, 440],
  ['角色分配', 890, 640],
]);

// ============================================================
// 3. Function structure diagram
// ============================================================
function buildFunctionStructure(runtime) {
  const { rect, vLine, hLine, tallRect, BOLD, snap, writeDiagram } = runtime;
  const body = [];
  const rootY = 40;
  const rootHeight = 76;
  const rootCenterX = 800;
  const mainRailY = 180;
  const groupY = 240;
  const childRailY = 390;
  const childY = 440;
  const childWidth = 60;
  const childHeight = 218;
  const childGap = 16;

  body.push(
    rect(rootCenterX - 200, rootY, 400, rootHeight, '校园导航系统', {
      size: 28,
      family: BOLD,
    }),
  );
  body.push(vLine(rootCenterX, rootY + rootHeight, mainRailY));

  const groups = [
    {
      center: 300,
      width: 180,
      label: '用户端',
      children: ['注册登录', '地图浏览', '视角切换', '兴趣点搜索', '分类筛选', '路径规划', '步行估算'],
    },
    {
      center: 1300,
      width: 180,
      label: '管理端',
      children: ['用户管理', '兴趣点管理', '公告管理', '导航统计', '角色分配'],
    },
  ];

  body.push(hLine(groups[0].center, groups[groups.length - 1].center, mainRailY));

  groups.forEach((group) => {
    body.push(
      rect(group.center - group.width / 2, groupY, group.width, 72, group.label, {
        size: 26,
        family: BOLD,
      }),
    );
    body.push(vLine(group.center, mainRailY, groupY));
    body.push(vLine(group.center, groupY + 72, childRailY));
    const renderedBoxes = group.children.map((label, idx) => {
      const rawX =
        group.center -
        (group.children.length * childWidth + (group.children.length - 1) * childGap) / 2 +
        idx * (childWidth + childGap);
      const x = snap(rawX);
      const width = snap(childWidth);
      return { label, x, width, centerX: x + width / 2 };
    });
    body.push(
      hLine(
        renderedBoxes[0].centerX,
        renderedBoxes[renderedBoxes.length - 1].centerX,
        childRailY,
      ),
    );
    renderedBoxes.forEach(({ label, x, width, centerX }) => {
      body.push(vLine(centerX, childRailY, childY));
      body.push(tallRect(x, childY, width, childHeight, label, { size: 18, family: BOLD }));
    });
  });

  writeDiagram('function-structure', 1600, 980, body);
}

buildFunctionStructure(R);

// ============================================================
// 4. System architecture diagram
// ============================================================
function buildSystemArch(runtime) {
  const { rect, brace, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];
  const frameX = 40;
  const frameY = 40;
  const frameWidth = 1600;
  const frameHeight = 800;
  const bandX = 260;
  const bandWidth = 1240;
  const labelX = 170;
  const archText = { family: BOLD, weight: '400' };
  const roundedBox = (x, y, width, height, label, opts = {}) =>
    rect(x, y, width, height, label, {
      rounded: true,
      size: opts.size || 22,
      minSize: opts.minSize || 12,
      family: opts.family || BOLD,
      weight: opts.weight || '400',
      strokeWidth: opts.strokeWidth || 2.6,
      preserveLines: opts.preserveLines || false,
      maxLines: opts.maxLines || Infinity,
    });
  const band = (y, height) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandWidth}" height="${snap(height)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, height, inset = 12) => {
    body.push(
      brace(labelX, y + inset, y + height - inset, label, {
        ...archText,
        size: 22,
        lineHeight: 25,
      }),
    );
  };
  const placeCenteredRow = (items, y, height, opts = {}) => {
    const paddingLeft = opts.paddingLeft ?? opts.padding ?? 32;
    const paddingRight = opts.paddingRight ?? opts.padding ?? 32;
    const widths = items.map((item) =>
      typeof item === 'string' ? opts.width || 150 : item.width || opts.width || 150,
    );
    const available = bandWidth - paddingLeft - paddingRight;
    const totalWidth = widths.reduce((sum, width) => sum + width, 0);
    const defaultGap = items.length > 1 ? (available - totalWidth) / (items.length - 1) : 0;
    const gap = opts.gap ?? Math.max(opts.minGap ?? 18, defaultGap);
    const usedWidth = totalWidth + gap * Math.max(0, items.length - 1);
    let cursor = bandX + paddingLeft + Math.max(0, (available - usedWidth) / 2);

    items.forEach((item, idx) => {
      const spec = typeof item === 'string' ? { label: item, width: opts.width || 150 } : item;
      body.push(
        roundedBox(cursor, y, spec.width || opts.width || 150, height, spec.label, {
          size: spec.size || opts.size || 22,
          minSize: spec.minSize || opts.minSize || 12,
          preserveLines: spec.preserveLines ?? opts.preserveLines ?? false,
          maxLines: spec.maxLines || opts.maxLines || Infinity,
        }),
      );
      cursor += (spec.width || opts.width || 150) + (idx === items.length - 1 ? 0 : gap);
    });
  };

  // Outer frame
  body.push(
    `<rect x="${frameX}" y="${frameY}" width="${frameWidth}" height="${frameHeight}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`,
  );
  // Title bar
  body.push(
    `<rect x="${frameX}" y="105" width="${frameWidth}" height="96" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`,
  );
  body.push(text(840, 152, '校园导航系统架构图', { size: 36, family: BOLD, weight: '700' }));

  // Three bands
  body.push(band(240, 140));  // Presentation layer
  body.push(band(420, 140));  // Business logic layer
  body.push(band(600, 140));  // Data layer

  braceBand('表现层', 240, 140);
  braceBand('业务逻辑层', 420, 140);
  braceBand('数据层', 600, 140);

  // Presentation layer
  placeCenteredRow(
    [
      { label: 'Vue3', width: 200 },
      { label: 'MapLibre GL', width: 240 },
      { label: 'Naive UI', width: 200 },
      { label: 'ECharts', width: 200 },
    ],
    270, 56,
    { size: 22, padding: 40, minGap: 40 },
  );

  // Business logic layer
  placeCenteredRow(
    [
      { label: 'Express', width: 200 },
      { label: 'JWT中间件', width: 220 },
      { label: '路由模块', width: 200 },
      { label: 'RESTful API', width: 220 },
    ],
    455, 56,
    { size: 22, padding: 40, minGap: 40 },
  );

  // Data layer
  placeCenteredRow(
    [
      { label: 'SQLite', width: 240 },
      { label: 'sql.js', width: 280 },
    ],
    635, 56,
    { size: 22, padding: 160, minGap: 120 },
  );

  writeDiagram('system-arch', 1700, 880, body);
}

buildSystemArch(R);

// ============================================================
// 5. ER diagram — 使用 gen_diagrams.py (Kroki neato+pos) 生成
//    不在这里画，避免项目引擎的属性椭圆版本覆盖
// ============================================================

// ============================================================
// 6. Business flow diagram
// ============================================================
function buildBusinessFlow(runtime) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram } = runtime;
  const body = [];
  const cx = 500;
  const boxW = 280;

  // Start
  body.push(rect(cx - 110, 40, 220, 60, '打开系统', { rounded: true, size: 24 }));
  body.push(vLine(cx, 100, 160, { arrow: true }));

  // Login decision
  body.push(diamond(cx, 220, 280, 110, '是否登录', { size: 20 }));
  body.push(hLine(640, 800, 220, { arrow: true }));
  body.push(text(720, 190, '否', { size: 20 }));
  body.push(rect(800, 190, 180, 60, '游客模式浏览', { size: 18 }));

  body.push(vLine(cx, 275, 340, { arrow: true }));
  body.push(text(cx + 25, 310, '是', { size: 20 }));

  // Login
  body.push(rect(cx - boxW / 2, 340, boxW, 60, '用户登录', { size: 24 }));
  body.push(vLine(cx, 400, 460, { arrow: true }));

  // Browse map
  body.push(rect(cx - boxW / 2, 460, boxW, 60, '浏览地图', { size: 24 }));
  body.push(vLine(cx, 520, 580, { arrow: true }));

  // Search POI
  body.push(rect(cx - boxW / 2, 580, boxW, 60, '搜索兴趣点', { size: 24 }));
  body.push(vLine(cx, 640, 700, { arrow: true }));

  // Select start/end
  body.push(rect(cx - boxW / 2, 700, boxW, 60, '选择起终点', { size: 24 }));
  body.push(vLine(cx, 760, 820, { arrow: true }));

  // Route planning
  body.push(rect(cx - boxW / 2, 820, boxW, 60, '路径规划', { size: 24 }));
  body.push(vLine(cx, 880, 940, { arrow: true }));

  // Show route
  body.push(rect(cx - boxW / 2, 940, boxW, 60, '显示路线及步行时间', { size: 22 }));
  body.push(vLine(cx, 1000, 1060, { arrow: true }));

  // End
  body.push(rect(cx - 110, 1060, 220, 60, '结束', { rounded: true, size: 26 }));

  // Guest mode connects back to browse map
  body.push(pathLine([[890, 250], [890, 490], [cx + boxW / 2, 490]], { width: 2.4, arrow: true }));

  writeDiagram('business-flow', 1060, 1180, body);
}

buildBusinessFlow(R);

console.log('All campus-nav diagrams generated.');
