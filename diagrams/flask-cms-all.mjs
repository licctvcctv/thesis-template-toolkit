import { createRuntime, parseArgs } from './runtime.mjs';
import { buildRadialUseCase } from './radial-use-case-template.mjs';

function buildSystemArch(R) {
  const { rect, brace, text, writeDiagram, BOLD, STROKE, snap } = R;
  const body = [];
  const frameX = 40, frameY = 40, frameW = 1600, frameH = 1100;
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
    items.forEach((it, i) => {
      const spec = typeof it === 'string' ? { label: it, width: opts.width || 150 } : it;
      body.push(roundedBox(cx, y, spec.width || opts.width || 150, h, spec.label, { size: spec.size || opts.size || 22, minSize: spec.minSize || opts.minSize || 12, preserveLines: spec.preserveLines ?? false, maxLines: spec.maxLines || Infinity }));
      cx += (spec.width || opts.width || 150) + gap;
    });
  };

  body.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  body.push(`<rect x="${frameX}" y="105" width="${frameW}" height="96" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`);
  body.push(text(840, 152, '企业官网CMS系统架构图', { size: 36, family: BOLD, weight: '700' }));

  body.push(band(240, 100)); body.push(band(380, 100)); body.push(band(520, 260));
  body.push(band(820, 92)); body.push(band(950, 104));

  braceBand('客户端', 240, 100); braceBand('用户角色', 380, 100);
  braceBand('服务应用层', 520, 260, 10); braceBand('数据层', 820, 92, 10);
  braceBand('运行环境', 950, 104, 14);

  placeCenteredRow(
    [{ label: '浏览器（Bootstrap 5 响应式页面）', width: 480 }, { label: 'Jinja2 模板引擎', width: 320 }],
    262, 56, { size: 22, padding: 60, minGap: 100 });
  placeCenteredRow(['访客', '编辑', '管理员'], 405, 54, { width: 180, size: 24, padding: 150, minGap: 120 });
  placeCenteredRow(
    ['用户认证', '文章管理', '栏目管理', '单页管理', '媒体管理', '用户管理', '留言管理'],
    560, 50, { width: 140, size: 18, padding: 24, minGap: 18 });
  placeCenteredRow([
    { label: ['Flask-Login', '会话管理'], width: 180, preserveLines: true, maxLines: 2 },
    { label: ['Flask-WTF', '表单/CSRF'], width: 180, preserveLines: true, maxLines: 2 },
    { label: ['Werkzeug', '密码哈希/安全'], width: 190, preserveLines: true, maxLines: 2 },
    { label: ['WTForms', '表单验证'], width: 160, preserveLines: true, maxLines: 2 },
    { label: ['站点设置', '全局配置'], width: 160, preserveLines: true, maxLines: 2 },
  ], 680, 72, { size: 17, padding: 34, minGap: 20, preserveLines: true, maxLines: 2 });
  placeCenteredRow([
    { label: 'roles', width: 120 }, { label: 'users', width: 120 },
    { label: 'articles', width: 120 }, { label: 'categories', width: 130 },
    { label: 'pages', width: 120 }, { label: 'media_assets', width: 140 },
    { label: 'site_settings', width: 140 }, { label: 'messages', width: 130 },
  ], 840, 50, { size: 15, minSize: 11, padding: 18, minGap: 10 });
  placeCenteredRow(
    ['Python 3.10+', 'Flask 3.0', 'Bootstrap 5.3', 'SQLite', 'pytest 8.0'],
    978, 48, { width: 180, size: 17, minSize: 12, padding: 48, minGap: 28 });

  writeDiagram('cms-system-arch', 1700, 1180, body);
}


function buildFunctionStructure(R) {
  const { rect, vLine, hLine, tallRect, BOLD, snap, writeDiagram } = R;
  const body = [];
  const rootCX = 800, rootY = 40, rootH = 76;
  const mainRailY = 180, groupY = 240;
  const childRailY = 390, childY = 440;
  const childW = 60, childH = 218, childGap = 16;

  body.push(rect(rootCX - 200, rootY, 400, rootH, '企业官网CMS系统', { size: 28, family: BOLD }));
  body.push(vLine(rootCX, rootY + rootH, mainRailY));

  const groups = [
    { center: 250, width: 180, label: '前台展示模块', children: ['首页展示', '文章详情', '栏目浏览', '全文搜索', '联系表单'] },
    { center: 800, width: 180, label: '用户认证模块', children: ['用户登录', '用户登出', '权限验证'] },
    { center: 1350, width: 180, label: '后台管理模块', children: ['文章管理', '栏目管理', '单页管理', '媒体管理', '用户管理', '留言管理', '站点设置'] },
  ];

  body.push(hLine(groups[0].center, groups[groups.length - 1].center, mainRailY));
  groups.forEach(g => {
    body.push(rect(g.center - g.width / 2, groupY, g.width, 72, g.label, { size: 24, family: BOLD }));
    body.push(vLine(g.center, mainRailY, groupY));
    body.push(vLine(g.center, groupY + 72, childRailY));
    const boxes = g.children.map((label, i) => {
      const rawX = g.center - (g.children.length * childW + (g.children.length - 1) * childGap) / 2 + i * (childW + childGap);
      const x = snap(rawX);
      return { label, x, w: snap(childW), cx: x + snap(childW) / 2 };
    });
    body.push(hLine(boxes[0].cx, boxes[boxes.length - 1].cx, childRailY));
    boxes.forEach(b => {
      body.push(vLine(b.cx, childRailY, childY));
      body.push(tallRect(b.x, childY, b.w, childH, b.label, { size: 18, family: BOLD }));
    });
  });

  writeDiagram('cms-function-structure', 1600, 980, body);
}


function buildBusinessFlow(R) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram } = R;
  const body = [];
  const cx = 600, boxW = 320;

  // 单列式流程，参考 wangkong
  body.push(rect(cx - 110, 60, 220, 60, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 120, 170, { arrow: true }));

  body.push(rect(cx - boxW / 2, 170, boxW, 60, '访客浏览企业官网首页', { size: 22 }));
  body.push(vLine(cx, 230, 290, { arrow: true }));

  body.push(rect(cx - boxW / 2, 290, boxW, 60, '选择栏目或搜索文章', { size: 22 }));
  body.push(vLine(cx, 350, 410, { arrow: true }));

  body.push(rect(cx - boxW / 2, 410, boxW, 60, '浏览文章详情，浏览量+1', { size: 20 }));
  body.push(vLine(cx, 470, 530, { arrow: true }));

  // 是否提交留言
  body.push(diamond(cx, 590, 300, 110, '是否提交留言', { size: 20 }));
  body.push(hLine(cx + 150, cx + 340, 590, { arrow: true }));
  body.push(text(cx + 240, 560, '是', { size: 20 }));
  body.push(rect(cx + 340, 560, 240, 60, '填写并提交留言', { size: 20 }));

  body.push(vLine(cx, 645, 710, { arrow: true }));
  body.push(text(cx + 25, 680, '否', { size: 20 }));

  // 是否为管理员
  body.push(diamond(cx, 770, 300, 110, '是否为管理员', { size: 20 }));
  body.push(hLine(cx + 150, cx + 340, 770, { arrow: true }));
  body.push(text(cx + 240, 740, '否', { size: 20 }));
  body.push(rect(cx + 340, 740, 180, 60, '结束浏览', { size: 20 }));

  body.push(vLine(cx, 825, 890, { arrow: true }));
  body.push(text(cx + 25, 860, '是', { size: 20 }));

  body.push(rect(cx - boxW / 2, 890, boxW, 60, '输入用户名和密码登录', { size: 22 }));
  body.push(vLine(cx, 950, 1010, { arrow: true }));

  // 验证通过
  body.push(diamond(cx, 1070, 280, 110, '验证通过', { size: 20 }));
  body.push(hLine(cx + 140, cx + 340, 1070, { arrow: true }));
  body.push(text(cx + 240, 1040, '否', { size: 20 }));
  body.push(rect(cx + 340, 1040, 200, 60, '提示登录失败', { size: 18 }));

  body.push(vLine(cx, 1125, 1190, { arrow: true }));
  body.push(text(cx + 25, 1160, '是', { size: 20 }));

  body.push(rect(cx - boxW / 2, 1190, boxW, 60, '进入后台执行管理操作', { size: 22 }));
  body.push(vLine(cx, 1250, 1310, { arrow: true }));

  body.push(rect(cx - 110, 1310, 220, 60, '结束', { rounded: true, size: 26 }));

  writeDiagram('cms-business-flow', 1240, 1420, body);
}


function buildErDiagram(R) {
  const { rect, diamond, pathLine, card, BOLD, writeDiagram } = R;
  const body = [];

  const entity = (x, y, label, width = 160, height = 56) => {
    const node = { x, y, w: width, h: height, cx: x + width / 2, cy: y + height / 2 };
    body.push(rect(x, y, width, height, label, { size: 22, family: BOLD, strokeWidth: 2.8 }));
    return node;
  };
  const relation = (cx, cy, label, width = 90, height = 56) => {
    const node = { cx, cy, w: width, h: height };
    body.push(diamond(cx, cy, width, height, label, { size: 18, maxLines: 1 }));
    return node;
  };
  const rectAnchor = (node, tx, ty) => {
    const dx = tx - node.cx, dy = ty - node.cy;
    if (Math.abs(dx) * (node.h / 2) > Math.abs(dy) * (node.w / 2))
      return [dx >= 0 ? node.x + node.w : node.x, node.cy];
    return [node.cx, dy >= 0 ? node.y + node.h : node.y];
  };
  const diamondAnchor = (node, tx, ty) => {
    const dx = tx - node.cx, dy = ty - node.cy;
    if (Math.abs(dx) / (node.w / 2) > Math.abs(dy) / (node.h / 2))
      return [node.cx + (Math.sign(dx || 1) * node.w) / 2, node.cy];
    return [node.cx, node.cy + (Math.sign(dy || 1) * node.h) / 2];
  };
  const connect = (entityA, rel, entityB) => {
    const [x1, y1] = rectAnchor(entityA, rel.cx, rel.cy);
    const [x2, y2] = diamondAnchor(rel, entityA.cx, entityA.cy);
    body.push(pathLine([[x1, y1], [x2, y2]], { width: 2.4 }));
    const [x3, y3] = diamondAnchor(rel, entityB.cx, entityB.cy);
    const [x4, y4] = rectAnchor(entityB, rel.cx, rel.cy);
    body.push(pathLine([[x3, y3], [x4, y4]], { width: 2.4 }));
  };

  // 网格布局 3×3，用户居中，关系只走水平/垂直，不交叉
  //
  //  Col-L(160)        Col-C(600)       Col-R(1040)
  //  Row1: 角色  ——属于——  用户  ——上传——  媒体资源
  //  Row2: 站点设置——配置—— (用户) ——撰写——  文章  ——归属—— 栏目(+父子)
  //  Row3: 联系留言——提交—— (用户) ——管理——  单页

  // 为避免交叉，Row2/Row3 的关系菱形直接横向连接，不经过用户中心
  // 而是在用户下方各出一条短竖线到自己的横向通道

  const role     = entity(60,   80,  '角色');
  const user     = entity(500,  80,  '用户');
  const media    = entity(960,  80,  '媒体资源', 180);

  const setting  = entity(60,  320,  '站点设置', 180);
  const article  = entity(500, 320,  '文章');
  const category = entity(960, 320,  '栏目');

  const message  = entity(60,  560,  '联系留言', 180);
  const page     = entity(500, 560,  '单页');

  // === Row 1: 水平 ===
  connect(role, relation(310, 108, '属于'), user);
  connect(user, relation(760, 108, '上传'), media);

  // === Col-C: 用户→文章 (垂直) ===
  connect(user, relation(580, 218, '撰写'), article);

  // === Row 2: 文章→栏目 (水平) ===
  connect(article, relation(760, 348, '归属'), category);

  // 栏目自引用"父子"
  const r_parent = relation(1200, 348, '父子');
  body.push(pathLine([[category.x + category.w, category.cy], [r_parent.cx - r_parent.w / 2, r_parent.cy]], { width: 2.4 }));
  body.push(pathLine([
    [r_parent.cx + r_parent.w / 2, r_parent.cy],
    [r_parent.cx + r_parent.w / 2 + 40, r_parent.cy],
    [r_parent.cx + r_parent.w / 2 + 40, category.y + category.h + 35],
    [category.cx, category.y + category.h + 35],
    [category.cx, category.y + category.h]
  ], { width: 2.4 }));

  // === Row 2 左: 站点设置——配置——用户 (水平，连用户左侧) ===
  // 用折线: 用户左侧出 → 向下到 Row2 高度 → 向左到配置菱形 → 站点设置
  const r_config = relation(370, 348, '配置');
  body.push(pathLine([[user.x, user.cy + 15], [user.x - 30, user.cy + 15], [user.x - 30, r_config.cy], [r_config.cx + r_config.w / 2, r_config.cy]], { width: 2.4 }));
  body.push(pathLine([[r_config.cx - r_config.w / 2, r_config.cy], [setting.x + setting.w, setting.cy]], { width: 2.4 }));

  // === Row 3 左: 联系留言——提交——用户 ===
  const r_submit = relation(370, 588, '提交');
  body.push(pathLine([[user.x, user.cy + 30], [user.x - 60, user.cy + 30], [user.x - 60, r_submit.cy], [r_submit.cx + r_submit.w / 2, r_submit.cy]], { width: 2.4 }));
  body.push(pathLine([[r_submit.cx - r_submit.w / 2, r_submit.cy], [message.x + message.w, message.cy]], { width: 2.4 }));

  // === Row 3 右: 单页——管理——用户 ===
  const r_manage = relation(760, 588, '管理');
  body.push(pathLine([[user.x + user.w, user.cy + 15], [user.x + user.w + 30, user.cy + 15], [user.x + user.w + 30, r_manage.cy], [r_manage.cx - r_manage.w / 2, r_manage.cy]], { width: 2.4 }));
  body.push(pathLine([[r_manage.cx + r_manage.w / 2, r_manage.cy], [page.x, page.cy]], { width: 2.4 }));

  // Cardinality
  [
    [220, 80, '1'],  [380, 80, 'N'],      // 角色 1—N 用户
    [680, 80, '1'],  [830, 80, 'N'],      // 用户 1—N 媒体
    [600, 158, '1'], [600, 278, 'N'],     // 用户 1—N 文章
    [680, 320, 'N'], [830, 320, '1'],     // 文章 N—1 栏目
    [1130, 320, '1'],[1260, 400, 'N'],    // 栏目 父子
    [440, 320, '1'], [290, 320, 'N'],     // 用户 1—N 站点设置
    [440, 560, '1'], [290, 560, 'N'],     // 用户 1—N 留言
    [690, 560, '1'], [830, 560, 'N'],     // 用户 1—N 单页
  ].forEach(([x, y, v]) => body.push(card(x, y, v)));

  writeDiagram('er-diagram', 1340, 660, body);
}


const args = parseArgs();
const R = createRuntime(args);

console.log('Building CMS diagrams...');
buildSystemArch(R);
buildFunctionStructure(R);

buildRadialUseCase(R, 'usecase_admin', '管理员', [
  ['文章管理', 290, 220], ['栏目管理', 290, 380],
  ['单页管理', 290, 540], ['媒体管理', 290, 700],
], [
  ['用户管理', 890, 220], ['留言管理', 890, 380],
  ['站点设置', 890, 540], ['仪表盘', 890, 700],
]);

buildRadialUseCase(R, 'usecase_visitor', '访客', [
  ['浏览首页', 290, 220], ['查看文章', 290, 380], ['栏目浏览', 290, 540],
], [
  ['全文搜索', 890, 220], ['查看单页', 890, 380], ['提交留言', 890, 540],
]);

buildBusinessFlow(R);
buildErDiagram(R);
console.log('Done!');
